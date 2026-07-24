import requests
import re
import xml.etree.ElementTree as ET

import requests

from .api_key_handler import API_KEY
from .debug_helper import debug_print


def get_asset_id(url_or_id):
    """Extracts the Asset ID from a Roblox catalog URL or validates a direct Asset ID."""
    match = re.search(r"(?:catalog|library)\/(\d+)", url_or_id)
    if match:
        return match.group(1)

    # If no URL match, check if the input is just digits (an ID)
    if url_or_id.isdigit():
        return url_or_id

    return None


def get_asset_url(asset_id):
    """
    Gets the CDN download URL for the 3D model associated with an assetId.
    This URL points to the binary .rbxm model file, not the final texture image.
    """

    # This API endpoint might break in the future. Fix this if struggling.
    url = f"https://apis.roblox.com/asset-delivery-api/v1/assetId/{asset_id}"
    headers = {"x-api-key": API_KEY}

    debug_print(f"Requesting URL for assetId: {asset_id}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes (like 401, 403, 404)

        data = response.json()
        location = data.get("location")

        if not location:
            print("Error: Could not find a location URL in the API response.")
            return None

        return location

    except requests.exceptions.HTTPError as http_err:
        match http_err.response.status_code:
            case 401:
                print(
                    "Error: 401 Unauthorized. Your API key is likely invalid or expired."
                )
            case 403:
                print(
                    "Error: 403 Forbidden. You do not have permission to access this asset. "
                    "HINT: Check if your API key has 'legacy-assets' read permission enabled."
                )
            case _:
                print(f"HTTP Error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None


def get_asset_details(asset_id):
    """Gets details for an asset, including assetType, displayName, and description."""
    url = f"https://apis.roblox.com/assets/v1/assets/{asset_id}"
    headers = {"x-api-key": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        asset_type = data.get("assetType")
        display_name = data.get("displayName")
        description = data.get("description")

        if asset_type != "Shirt" and asset_type != "Pants":
            print(
                f"Unexpected Behaviour: Asset ID {asset_id} is not a Shirt or Pants. Found assetType: {asset_type}"
            )
            return None, None, None

        if not asset_type or not display_name:
            print("Error: Could not find assetType or displayName in the API response.")
            return None, None, None

        return asset_type, display_name, description

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error occurred while getting asset details: {http_err}")
        return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the asset details request: {e}")
        return None, None, None


def get_image_url_from_xml(clothes_url):
    """
    Downloads the model .rbxm (XML) file and parses it to find the texture URL.
    """
    try:
        response = requests.get(clothes_url)
        response.raise_for_status()

        xml_content = response.text
        root = ET.fromstring(xml_content)

        template_url_element = root.find(
            ".//Properties/Content[@name='ShirtTemplate']/url"
        )
        if template_url_element is None:
            template_url_element = root.find(
                ".//Properties/Content[@name='PantsTemplate']/url"
            )

        if template_url_element is not None and template_url_element.text:
            return template_url_element.text
        else:
            print(
                "Error: Could not find 'ShirtTemplate' or 'PantsTemplate' URL in the model file."
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the model file: {e}")
        return None
    except ET.ParseError as e:
        print(f"An error occurred while parsing the XML model file: {e}")
        return None

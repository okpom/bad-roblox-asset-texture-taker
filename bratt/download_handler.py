import os
import re

import requests
from rich import print

from .api_handler import (
    get_asset_details,
    get_asset_id,
    get_asset_url,
    get_image_url_from_xml,
)
from .debug_helper import debug_print

processed_assets = set()


def download_asset(url_or_id):
    """Handles the entire asset download process."""
    asset_id = get_asset_id(url_or_id)
    if not asset_id:
        print(f"Could not find a valid Asset ID from input: {url_or_id}")
        print("For more information, try '--help'")
        return

    processed_assets.add(asset_id)

    debug_print(f"Fetched Asset ID: {asset_id}")

    # Get the asset type and name for the initial asset
    asset_type, display_name, description = None, None, None
    if asset_data := get_asset_details(asset_id):
        asset_type, display_name, description = asset_data
    if not asset_type or not display_name:
        print("Could not retrieve asset details, or the asset is not a Shirt or Pants.")
        return

    debug_print(f"Asset is a '{asset_type}' named '{display_name}'")

    model_url = get_asset_url(asset_id)

    if model_url:
        texture_asset_url = get_image_url_from_xml(model_url)

        if texture_asset_url:
            texture_asset_id_match = re.search(r"id=(\d+)", texture_asset_url)
            if not texture_asset_id_match:
                print(f"Could not extract asset ID from texture URL: {texture_asset_url}")
                return

            texture_asset_id = texture_asset_id_match.group(1)
            debug_print(f"Found texture Asset ID: {texture_asset_id}")

            # Get the final image download URL
            image_location_url = get_asset_url(texture_asset_id)
            if image_location_url:
                download_and_save_image(image_location_url, asset_id, asset_type, display_name)
                recursive_asset_check(asset_id, description, processed_assets)
            else:
                print("\nFailed to get the final image download URL.")
        else:
            print("\nFailed to get the texture asset URL from the model file.")
    else:
        print(f"Could not find model URL for Asset ID: {asset_id}")


def recursive_asset_check(original_asset_id, description, processed_assets):
    """Checks for a linked asset in the description and downloads it if it's the corresponding clothing part."""
    if not description:
        return

    match = re.search(r"roblox.com/catalog/(\d+)", description)
    if not match:
        return

    recursive_asset_id = match.group(1)

    if recursive_asset_id in processed_assets:
        # print(f"Skipping already processed asset: {recursive_asset_id}") # debug
        return

    debug_print(f"Found potential linked asset ID for: {recursive_asset_id}")
    original_asset_type, display_name = None, None
    recursive_asset_type, recursive_description = None, None
    if asset_data := get_asset_details(original_asset_id):
        original_asset_type, display_name, _ = asset_data

    if asset_data := get_asset_details(recursive_asset_id):
        recursive_asset_type, _, recursive_description = asset_data

    if not original_asset_type or not recursive_asset_type:
        return

    # Optional: Check if the recursive asset links back to the original asset.
    # backlink_match = re.search(fr"roblox.com/catalog/{original_asset_id}", recursive_description or "")
    # if not backlink_match:
    #     print("Recursive asset does not link back to the original. Skipping.")
    #     return

    if original_asset_type == "Shirt" and recursive_asset_type == "Pants":
        print(f"Found matching PANTS for {display_name}.\n")
        download_asset(recursive_asset_id)
    elif original_asset_type == "Pants" and recursive_asset_type == "Shirt":
        print(f"Found matching SHIRT for {display_name}.\n")
        download_asset(recursive_asset_id)


def download_and_save_image(image_url, asset_id, asset_type, display_name):
    """Downloads the final texture image and saves it to a subfolder."""
    if not asset_type or not display_name:
        print("[red]error:[/red] Missing asset_type or displayName for saving the image.")
        return

    # Sanitize display_name for use as a filename
    safe_filename = "".join(c for c in display_name if c.isalnum() or c in (" ", "_")).rstrip()
    if not safe_filename:
        safe_filename = asset_id  # fallback to asset_id if name is all special chars

    folder_path = os.path.join("textures", asset_type)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        # print(f"Downloading final texture from: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()

        file_path = os.path.join(folder_path, f"{safe_filename}.png")
        with open(file_path, "wb") as f:
            f.write(response.content)
        # print(f"Successfully saved texture to: {file_path}")
        print(f"Successfully saved {asset_type.upper()} texture for {asset_id} ({safe_filename})\n")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the image: {e}")

import requests
import sys
import re
import os
from api_handler import (
    get_asset_id,
    get_asset_url,
    get_asset_details,
    get_image_url_from_xml,
)
from util import recursive_asset_check


def load_api_key():
    """Loads the API key from the api_key.txt file."""
    try:
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()
            if not api_key or api_key == "YOUR_API_KEY_HERE":
                print("Error: API key is missing or placeholder in api_key.txt")
                return None
            return api_key
    except FileNotFoundError:
        print("Error: api_key.txt not found. Please create it and add your API key.")
        return None


def download_and_save_image(image_url, asset_id, asset_type, display_name):
    """Downloads the final texture image and saves it to a subfolder."""
    if not asset_type or not display_name:
        print("Error: Missing asset_type or displayName for saving the image.")
        return

    # Sanitize display_name for use as a filename
    safe_filename = "".join(
        c for c in display_name if c.isalnum() or c in (" ", "_")
    ).rstrip()
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
        print(f"Successfully saved texture for {asset_id} ({safe_filename})\n")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the image: {e}")


def download_asset(url_or_id, api_key, processed_assets):
    """Handles the entire asset download process."""
    asset_id = get_asset_id(url_or_id)
    if not asset_id:
        print(f"Could not find a valid Asset ID from input: {url_or_id}")
        return

    processed_assets.add(asset_id)

    print(f"Fetched Asset ID: {asset_id}")

    # Get the asset type and name for the initial asset
    asset_type, display_name, description = get_asset_details(asset_id, api_key)
    if not asset_type or not display_name:
        print("Could not retrieve asset details, or the asset is not a Shirt or Pants.")
        return

    print(f"Asset is a '{asset_type}' named '{display_name}'")

    model_url = get_asset_url(asset_id, api_key)

    if model_url:
        texture_asset_url = get_image_url_from_xml(model_url)

        if texture_asset_url:
            texture_asset_id_match = re.search(r"id=(\d+)", texture_asset_url)
            if not texture_asset_id_match:
                print(
                    f"Could not extract asset ID from texture URL: {texture_asset_url}"
                )
                return

            texture_asset_id = texture_asset_id_match.group(1)
            print(f"Found texture Asset ID: {texture_asset_id}")

            # Get the final image download URL
            image_location_url = get_asset_url(texture_asset_id, api_key)

            if image_location_url:
                download_and_save_image(
                    image_location_url, asset_id, asset_type, display_name
                )
                recursive_asset_check(
                    asset_id, description, api_key, download_asset, processed_assets
                )
            else:
                print("\nFailed to get the final image download URL.")
        else:
            print("\nFailed to get the texture asset URL from the model file.")
    else:
        print(f"Could not find model URL for Asset ID: {asset_id}")


def main():
    """Main function to run the script."""
    api_key = load_api_key()
    if not api_key:
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python main.py <roblox_catalog_url_or_id>")
        sys.exit(1)

    url_or_id = sys.argv[1]
    processed_assets = set()
    download_asset(url_or_id, api_key, processed_assets)


if __name__ == "__main__":
    main()

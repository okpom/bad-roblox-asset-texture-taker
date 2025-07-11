import re
from api_handler import get_asset_details


def recursive_asset_check(
    original_asset_id, description, api_key, download_asset_func, processed_assets
):
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

    print(f"Found potential linked asset ID for: {recursive_asset_id}")

    original_asset_type, _, _ = get_asset_details(original_asset_id, api_key)
    recursive_asset_type, _, recursive_description = get_asset_details(
        recursive_asset_id, api_key
    )

    if not original_asset_type or not recursive_asset_type:
        return

    # Optional: Check if the recursive asset links back to the original asset.
    # backlink_match = re.search(fr"roblox.com/catalog/{original_asset_id}", recursive_description or "")
    # if not backlink_match:
    #     print("Recursive asset does not link back to the original. Skipping.")
    #     return

    if original_asset_type == "Shirt" and recursive_asset_type == "Pants":
        print("Found matching pants for the shirt. Downloading pants...\n")
        download_asset_func(recursive_asset_id, api_key, processed_assets)
    elif original_asset_type == "Pants" and recursive_asset_type == "Shirt":
        print("Found matching shirt for the pants. Downloading shirt...\n")
        download_asset_func(recursive_asset_id, api_key, processed_assets)

import sys
from util import download_asset
from api_key_handler import API_KEY

def main():
    """Main function to run the script."""
    if not API_KEY:
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python main.py <roblox_catalog_url_or_id>")
        sys.exit(1)

    url_or_id = sys.argv[1]
    download_asset(url_or_id)


if __name__ == "__main__":
    main()

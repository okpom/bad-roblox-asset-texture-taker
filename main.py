import sys
from rich import print
from download_handler import download_asset
from api_key_handler import API_KEY

def main():
    """Main function to run the script."""
    if not API_KEY:
        sys.exit(1)

    if len(sys.argv) < 2:
        print("[red]error:[/red] missing arguments")
        print("For more information, try '--help'")
        sys.exit(1)

    if sys.argv[1] == "help" or sys.argv[1] == "--help":
        print("Usage: python main.py <roblox_catalog_url_or_id>")
        print(
            "       python main.py -o <roblox_catalog_url_or_id>  (download and overlay)"
        )
        print(
            "       python main.py bg-replace                     ( batch overlay textures)"
        )
        sys.exit(1)

    url_or_id = sys.argv[1]
    download_asset(url_or_id)


if __name__ == "__main__":
    main()

import sys
from util import download_asset


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


def main():
    """Main function to run the script."""
    api_key = load_api_key()
    if not api_key:
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python main.py <roblox_catalog_url_or_id>")
        sys.exit(1)

    url_or_id = sys.argv[1]
    download_asset(url_or_id, api_key)


if __name__ == "__main__":
    main()

from rich import print
from . import PROJECT_ROOT
import os

def load_api_key():
    """Loads the API key from the api_key.txt file."""
    api_key_path = os.path.join(PROJECT_ROOT, "api_key.txt")
    try:
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()
            if not api_key or api_key == "YOUR_API_KEY_HERE":
                print("[red]error:[/red] API key is missing or placeholder in api_key.txt")
                return None
            return api_key
    except FileNotFoundError:
        print("[red]error:[/red] api_key.txt not found. Creating file \"./api_key.txt\". Please add your API key.")
        with open(api_key_path, "w") as f:
            f.write("YOUR_API_KEY_HERE")
        return None


API_KEY = load_api_key()

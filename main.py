import sys
from rich.text import Text
from download_handler import download_asset
from api_key_handler import API_KEY
from overlay_template import process_all_textures


def main():
    if not API_KEY:
        sys.exit(1)

    if len(sys.argv) < 2:
        print(Text("[red]error:[/red] missing arguments"))
        print("For more information, try '--help'")
        sys.exit(1)

    if sys.argv[1] == "help" or sys.argv[1] == "--help":
        print("Usage: python main.py <roblox_catalog_url_or_id>     (download texture)")
        print(
            "       python main.py -o <roblox_catalog_url_or_id>  (download and overlay)"
        )
        print(
            "       python main.py bg-replace                     (mass overlay textures)"
        )
        sys.exit(1)

    # Handle bg-replace command
    if sys.argv[1] == "bg-replace":
        success = process_all_textures()
        if success:
            print("Template overlay process completed successfully!")
        else:
            print(
                "Template overlay process ran into error\\(s). Good luck finding them."
            )
            sys.exit(1)
        return

    # Handle -o flag for overlay after download
    overlay_after_download = False
    if sys.argv[1] == "-o":
        if len(sys.argv) < 3:
            print("error: -o flag requires a URL or asset ID")
            sys.exit(1)
        overlay_after_download = True
        url_or_id = sys.argv[2]
    else:
        url_or_id = sys.argv[1]

    # Download the asset
    download_asset(url_or_id)

    # Apply overlay if requested
    if overlay_after_download:
        print("\nApplying template overlay to downloaded textures.")
        success = process_all_textures()
        if success:
            print("Template overlay process completed successfully.\n")
        else:
            print(
                "Template overlay process ran into error(s). Good luck finding them.\n"
            )
            # TODO: Write a better error handler. Right now it just says there's an error
            #       if even just one image fails to process.


if __name__ == "__main__":
    main()

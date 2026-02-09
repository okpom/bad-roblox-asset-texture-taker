import sys
import os
from rich.text import Text
from bratt import PROJECT_ROOT
from download_handler import download_asset
from api_key_handler import API_KEY
from overlay_template import process_all_textures
from debug_helper import debug_print


def main():
    if not API_KEY:
        sys.exit(1)

    if len(sys.argv) < 2:
        print(Text("[red]error:[/red] missing arguments"))
        print("For more information, try '--help'")
        sys.exit(1)

    args = sys.argv[1:]
    batch_mode = False
    overlay_mode = False
    batch_file = "links.txt"  # default
    url_or_id = None

    # Check for flags at the end
    if args and args[-1].startswith("-"):
        print(Text(f"[red]error:[/red] Flag '{args[-1]}' cannot be the last argument"))
        print("Flags must be followed by their required parameters or other content")
        print("For more information, try '--help'")
        sys.exit(1)

    i = 0
    while i < len(args):
        arg = args[i]

        match arg:
            case "help" | "--help":
                print(
                    "Usage: python bratt/main.py <roblox_catalog_url_or_id>     (download texture)"
                )
                print(
                    "       python bratt/main.py -o <roblox_catalog_url_or_id>  (download and overlay)"
                )
                print(
                    "       python bratt/main.py -b [file.txt]                  (batch download from file [default: links.txt])"
                )
                print(
                    "       python bratt/main.py -b -o [file.txt]               (batch download and overlay)"
                )
                print(
                    "       python bratt/main.py -o -b [file.txt]               (batch download and overlay)"
                )
                print(
                    "       python bratt/main.py bg-replace                     (mass overlay textures)"
                )
                print()
                print("Note: Flags cannot be placed at the end of the command")
                sys.exit(1)

            case "bg-replace":
                success = process_all_textures()
                if success:
                    print("Template overlay process completed successfully!")
                else:
                    print(
                        "Template overlay process ran into error\\(s). Good luck finding them."
                    )
                    sys.exit(1)
                return

            case "-b" | "--batch":
                batch_mode = True
                # Check if next argument is a filename (not a flag)
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    batch_file = args[i + 1]
                    i += 1  # Skip the filename in next iteration

            case "-o":
                overlay_mode = True
                # Check if '-o' is the last argument or if next is a flag
                if i == len(args) - 1:
                    print(Text("[red]error:[/red] -o flag cannot be the last argument"))
                    print("For more information, try '--help'")
                    sys.exit(1)
                # If not in batch mode, next argument should be URL/ID
                if (
                    not batch_mode
                    and i + 1 < len(args)
                    and not args[i + 1].startswith("-")
                ):
                    url_or_id = args[i + 1]
                    i += 1  # Skip the URL/ID in next iteration

            case _:
                # This is a URL or ID (not a flag)
                if not arg.startswith("-") and not batch_mode:
                    url_or_id = arg

        i += 1

    if batch_mode:
        if not os.path.isabs(batch_file):
            batch_file = os.path.join(PROJECT_ROOT, batch_file)

        if not os.path.exists(batch_file):
            if batch_file == "links.txt":
                print(
                    Text(
                        "[red]error:[/red] No files to process. 'links.txt' not found. Check if file is in root folder."
                    )
                )
                print(
                    "Create 'links.txt' with URLs/IDs (one per line) or specify a different file."
                )
            else:
                print(Text(f"[red]error:[/red] File '{batch_file}' not found."))
            sys.exit(1)

        print(f"Processing batch file: {batch_file}")
        try:
            with open(batch_file, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if not lines:
                print(
                    Text("[yellow]warning:[/yellow] File is empty, nothing to process.")
                )
                return

            print(f"Found {len(lines)} items to process")
            successful = 0
            failed = 0

            for i, url_or_id in enumerate(lines, 1):
                debug_print(f"\n--- Processing item {i}/{len(lines)}: {url_or_id} ---")
                try:
                    download_asset(url_or_id)
                    successful += 1
                except Exception as e:
                    print(f"Failed to process {url_or_id}: {e}")
                    failed += 1

            print("\n--- Batch processing complete ---")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")

        except Exception as e:
            print(Text(f"[red]error:[/red] Failed to read batch file: {e}"))
            sys.exit(1)

        if overlay_mode:
            print("\nApplying template overlay to all downloaded textures...")
            success = process_all_textures()
            if success:
                print("Template overlay process completed successfully!\n")
            else:
                print(
                    "Template overlay process ran into error(s). Good luck finding them.\n"
                )

        return

    # Handle single item processing
    if not url_or_id:
        print(Text("[red]error:[/red] No URL or asset ID provided"))
        print("For more information, try '--help'")
        sys.exit(1)

    download_asset(url_or_id)

    if overlay_mode:
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

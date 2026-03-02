import os
from PIL import Image
from rich import print
from .debug_helper import debug_print


def overlay_images(input_folder, output_folder, template_path):
    """Overlays all images in input_folder with template.png and saves to output_folder."""
    if not os.path.exists(template_path):
        print(f"[red]error:[/red] Template file '{template_path}' not found.")
        return False

    if not os.path.exists(input_folder):
        print(f"Warning: Input folder '{input_folder}' not found. Skipping.")
        return True

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    done_folder = os.path.join(input_folder, "done")
    if not os.path.exists(done_folder):
        os.makedirs(done_folder)

    try:
        template = Image.open(template_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading template image: {e}")
        return False

    # Process all PNG files in the input folder
    processed_count = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                texture = Image.open(input_path).convert("RGBA")

                if template.size != texture.size:
                    template_resized = template.resize(
                        texture.size, Image.Resampling.NEAREST
                    )
                else:
                    template_resized = template

                # Overlay template onto texture
                overlay_result = Image.alpha_composite(texture, template_resized)

                overlay_result.save(output_path, "PNG")
                debug_print(f"Processed: {filename}")
                processed_count += 1

                done_path = os.path.join(done_folder, filename)
                os.rename(input_path, done_path)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Processed {processed_count} images in {input_folder}\n")
    return True


def process_all_textures():
    template_path = "template.png"
    if not os.path.exists(template_path):
        template_path = "./textures/template.png"
        if not os.path.exists(template_path):
            print(
                "[red]error:[/red] Template file 'template.png' not found in current or textures folder."
            )
            return False

    folders = [
        ("textures/Shirt", "textures/e_shirt"),
        ("textures/Pants", "textures/e_pants"),
    ]

    success = True
    for input_folder, output_folder in folders:
        if not overlay_images(input_folder, output_folder, template_path):
            success = False

    return success

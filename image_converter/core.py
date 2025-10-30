import os
from PIL import Image
from typing import Callable

# --- Core logic for file conversion based on a file list ---
def convert_files(
    file_list: list[str],
    output_folder: str,
    max_width: int,
    quality: int,
    log_callback: Callable[[str], None],
) -> None:
    """Processes a list of image files, compresses them, and saves them as WebP.

    Args:
        file_list (list): A list of full paths to the source image files.
        output_folder (str): The path to the directory where compressed files will be saved.
        max_width (int): The maximum width for output images. Larger images will be resized.
        quality (int): The quality setting for WebP conversion (e.g., 1-100).
        log_callback (function): A callback function to send status messages to the GUI.
    """
    # Use a try-except block to catch any critical errors, like an invalid output folder.
    try:
        # Create the destination folder if it doesn't already exist.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            # Log a message if the destination folder was created.
            log_callback(f"Utworzono folder docelowy: {output_folder}")

        # Check if any files were provided to process.
        found_images = len(file_list) > 0

        # Iterate through each file in the list.
        for input_path in file_list:
            # Get the base name of the file.
            filename = os.path.basename(input_path)
            # Split the file name into the root and extension.
            file_root, _ = os.path.splitext(filename)
            # Join the output folder with the file root and extension.
            output_path = os.path.join(output_folder, f"{file_root}.webp")

            try:
                # Open the image file.
                img = Image.open(input_path)
                # Convert the image to RGBA mode if it's in RGBA or P mode to preserve transparency
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")

                # Check if the image is wider than the maximum width.
                if img.width > max_width:
                    aspect_ratio = img.height / img.width
                    new_height = int(max_width * aspect_ratio)
                    # Resize the image to the maximum width while maintaining the aspect ratio.
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # Save the image as WebP with the specified quality.
                img.save(output_path, "webp", quality=quality)
                log_callback(f"✔️ Skompresowano do WebP: {filename}")

            except Exception as e:
                # Log an error message if there's an issue with the file.
                log_callback(f"❌ Błąd przy pliku {filename}: {e}")

        if not found_images:
            # Log a message if no files were provided to process.
            log_callback("Nie wybrano żadnych plików do kompresji.")
        else:
            # Log a message if all files were processed successfully.
            log_callback("\nGotowe! Wszystkie zdjęcia zostały przetworzone.")
    except Exception as e:
        # Log a critical error message if there's an issue with the compression process.
        log_callback(f"Wystąpił krytyczny błąd: {e}")

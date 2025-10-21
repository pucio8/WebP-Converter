import customtkinter as ctk  # Customticker, library for creating GUI
import os  # Os library for interacting with the operating system
import threading  # Threading library for creating threads
from tkinter import (
    filedialog,
    messagebox,
    Toplevel,
    Widget,
    Event,
)  # Filedialog- open dialog for selecting files, messagebox- show messages, Toplevel- create a new window
from PIL import Image  # Pillow library for image processing
from typing import Callable, list, Optional, Any  # typing library for type hints


# --- Helper class for creating tooltips ---
class Tooltip:
    """A helper class that creates and manages a tooltip for a widget."""

    def __init__(self, widget: Widget, text: str):
        self.widget = widget  # Reference to the widget that will show the tooltip
        self.text = text  # Reference to the text of the tooltip
        self.tooltip_window: Optional[Toplevel] = (
            None  # Reference to the tooltip window, or None if hidden.
        )
        # Binds the function to show the tooltip when the mouse enters the widget.
        self.widget.bind("<Enter>", self.show_tooltip)
        # Binds the function to hide the tooltip when the mouse leaves the widget.
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event: Event):
        """Creates and displays the tooltip window at the correct position."""
        # Get the widget's position relative to its parent. Returns (x, y, width, height).
        x, y, _, _ = self.widget.bbox("insert")
        # Convert the widget's local coordinates to absolute screen coordinates.
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        # Create a new, borderless pop-up window (Toplevel).
        self.tooltip_window = Toplevel(self.widget)
        # Override the window manager's default behavior.
        self.tooltip_window.wm_overrideredirect(True)
        # Set the window's geometry to the calculated position.
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        # Create a new label with the tooltip text.
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            corner_radius=5,
            fg_color=("#333333", "#444444"),
            text_color="white",
            wraplength=200,
            justify="left",
            padx=10,
            pady=5,
        )
        # Pack the label into the window.
        label.pack()

    def hide_tooltip(self, event: Event):
        """Destroys the tooltip window if it exists and resets the state."""
        # Check if the tooltip window actually exists (is not None).
        if self.tooltip_window:
            # If it exists, destroy it completely.
            self.tooltip_window.destroy()
        self.tooltip_window = None  # Reset the tooltip window state to None.


# --- Core logic for file compression based on a file list ---
def compress_files(
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
        quality (int): The quality setting for WebP compression (e.g., 1-100).
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
                # Convert the image to RGB mode if it's in RGBA or P mode.
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

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


# --- Główna klasa aplikacji GUI ---
class ImageCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Uniwersalny Kompresor Zdjęć 2025 🖼️")
        self.geometry("700x650")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Przechowuje listę ścieżek do wybranych plików
        self.input_file_paths = []

        # Ramka z polami wyboru
        path_frame = ctk.CTkFrame(self)
        path_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            path_frame,
            text="Wybierz pliki do kompresji...",
            command=self.select_input_files,
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10, ipady=5, sticky="ew")
        self.file_status_label = ctk.CTkLabel(
            path_frame, text="Nie wybrano żadnych plików"
        )
        self.file_status_label.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w"
        )

        ctk.CTkLabel(path_frame, text="Folder docelowy").grid(
            row=2, column=0, columnspan=2, padx=10, sticky="w"
        )
        self.output_path = ctk.StringVar()
        ctk.CTkEntry(path_frame, textvariable=self.output_path).grid(
            row=3, column=0, padx=10, pady=(0, 10), sticky="ew"
        )
        ctk.CTkButton(
            path_frame, text="Wybierz...", command=self.select_output_folder, width=100
        ).grid(row=3, column=1, padx=(0, 10), pady=(0, 10))

        # Ramka z suwakami ustawień
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure((1, 4), weight=1)

        ctk.CTkLabel(settings_frame, text="Maks. szerokość:").grid(
            row=0, column=0, padx=(10, 0)
        )
        self.width_slider = ctk.CTkSlider(
            settings_frame,
            from_=400,
            to=2000,
            number_of_steps=160,
            command=self.update_width_label,
        )
        self.width_slider.set(1200)
        self.width_slider.grid(row=0, column=1, padx=(10, 5), sticky="ew")
        self.width_value_label = ctk.CTkLabel(settings_frame, text="1200 px", width=60)
        self.width_value_label.grid(row=0, column=2, padx=(0, 10))

        ctk.CTkLabel(settings_frame, text="Jakość WebP:").grid(
            row=0, column=3, padx=(10, 0)
        )
        self.quality_slider = ctk.CTkSlider(
            settings_frame,
            from_=10,
            to=100,
            number_of_steps=90,
            command=self.update_quality_label,
        )
        self.quality_slider.set(85)
        self.quality_slider.grid(row=0, column=4, padx=(10, 5), sticky="ew")
        self.quality_value_label = ctk.CTkLabel(settings_frame, text="85 %", width=50)
        self.quality_value_label.grid(row=0, column=5, padx=(0, 10))

        Tooltip(
            self.width_slider,
            "Idealna szerokość dla większości stron internetowych to 1200px.",
        )
        Tooltip(
            self.quality_slider,
            "Jakość 85% to świetny kompromis między wyglądem a rozmiarem pliku.",
        )

        # Pole logów
        self.log_area = ctk.CTkTextbox(self, state="disabled", wrap=ctk.WORD)
        self.log_area.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Przycisk startu
        self.start_button = ctk.CTkButton(
            self,
            text="🚀 Rozpocznij Kompresję",
            font=("Roboto", 16, "bold"),
            command=self.start_compression_thread,
        )
        self.start_button.grid(
            row=3, column=0, padx=20, pady=(10, 20), ipady=10, sticky="ew"
        )

    def update_width_label(self, value):
        self.width_value_label.configure(text=f"{int(value)} px")

    def update_quality_label(self, value):
        self.quality_value_label.configure(text=f"{int(value)} %")

    def select_input_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Wybierz pliki obrazów",
            filetypes=[("Pliki obrazów", "*.jpg *.jpeg *.png")],
        )
        if file_paths:
            self.input_file_paths = file_paths
            self.file_status_label.configure(
                text=f"Wybrano plików: {len(self.input_file_paths)}"
            )
            self.log(f"Wybrano {len(self.input_file_paths)} plików do przetworzenia.")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Wybierz folder docelowy")
        if folder_path:
            self.output_path.set(folder_path)
            self.log(f"Wybrano folder docelowy: {folder_path}")

    def log(self, message):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.configure(state="disabled")
        self.log_area.see("end")

    def start_compression_thread(self):
        if not self.input_file_paths or not self.output_path.get():
            messagebox.showerror(
                "Błąd", "Musisz wybrać przynajmniej jeden plik i folder docelowy!"
            )
            return

        self.start_button.configure(state="disabled", text="Pracuję...")
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")
        self.log("Rozpoczynam kompresję do formatu WebP...")

        compression_thread = threading.Thread(
            target=self.run_compression,
            args=(
                self.input_file_paths,
                self.output_path.get(),
                int(self.width_slider.get()),
                int(self.quality_slider.get()),
            ),
            daemon=True,
        )
        compression_thread.start()

    def run_compression(self, file_list, output_f, max_w, q):
        compress_files(file_list, output_f, max_w, q, self.log)
        self.start_button.configure(state="normal", text="🚀 Rozpocznij Kompresję")


# --- running the application ---
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ImageCompressorApp()
    app.mainloop()

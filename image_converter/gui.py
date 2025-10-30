import customtkinter as ctk
import threading
import os
import sys
from tkinter import filedialog, messagebox
from .core import convert_files
from .tooltip import Tooltip


# --- Main GUI application class ---
class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Konwerter Zdjęć do formatu WebP")
        self.geometry("700x650")
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        try: # Dodajmy try-except dla bezpieczeństwa
            self.iconbitmap(resource_path("icon2.ico"))
        except Exception as e:
            print(f"Błąd podczas ustawiania ikony okna: {e}")
        self.grid_columnconfigure(0, weight=1) # Configure the first column to take up all available space 
        self.grid_rowconfigure(2, weight=1) # Configure the second row to take up all available space (log area)

        # Stores the list of paths to the selected files
        self.input_file_paths = []

        # Frame with the selection fields
        path_frame = ctk.CTkFrame(self)
        path_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)

        # Button to select the files (inner frame)
        ctk.CTkButton(
            path_frame,
            text="Wybierz pliki do konwersji do formatu WebP...",
            command=self.select_input_files,
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10, ipady=5, sticky="ew")
        
        # Label to display the number of selected files (inner frame)
        self.file_status_label = ctk.CTkLabel(
            path_frame, text="Nie wybrano żadnych plików"
        )
        self.file_status_label.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="w"
        )

        # Button to clear the list of selected files (inner frame)
        self.clear_button = ctk.CTkButton(
            path_frame,
            text="Wyczyść listę",
            command=self.clear_input_files, 
            width=100,
            state="disabled"
        )
        self.clear_button.grid(
            row=1, column=1, padx=(0, 10), pady=(0, 10)
        )

        # Label to display the output folder (inner frame)
        ctk.CTkLabel(path_frame, text="Folder docelowy").grid(
            row=2, column=0, columnspan=2, padx=10, sticky="w"
        )
        # Entry to display the output folder (inner frame)
        self.output_path = ctk.StringVar()
        ctk.CTkEntry(path_frame, textvariable=self.output_path).grid(
            row=3, column=0, padx=10, pady=(0, 10), sticky="ew"
        )
        ctk.CTkButton(
            path_frame, text="Wybierz...", command=self.select_output_folder, width=100
        ).grid(row=3, column=1, padx=(0, 10), pady=(0, 10))

        # Frame with the settings sliders
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

        # Log area
        self.log_area = ctk.CTkTextbox(self, state="disabled", wrap=ctk.WORD)
        self.log_area.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Start button
        self.start_button = ctk.CTkButton(
            self,
            text="🚀 Rozpocznij Kompresję",
            font=("Roboto", 16, "bold"),
            command=self.start_compression_thread,
        )
        self.start_button.grid(
            row=3, column=0, padx=20, pady=(10, 20), ipady=10, sticky="ew"
        )

    def select_input_files(self) -> None:
        """Selects the input files for conversion."""
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
            self.clear_button.configure(state="normal")

    def select_output_folder(self) -> None:
        """Selects the output folder for the compressed files."""
        folder_path = filedialog.askdirectory(title="Wybierz folder docelowy")
        if folder_path:
            self.output_path.set(folder_path)
            self.log(f"Wybrano folder docelowy: {folder_path}")

    def clear_input_files(self) -> None:
        """Clears the list of selected input files."""
        self.input_file_paths = []
        self.file_status_label.configure(text="Nie wybrano żadnych plików")
        self.log("Wyczyszczono listę plików.")
        self.clear_button.configure(state="disabled")

    def update_width_label(self, value: int) -> None:
        """Updates the label with the current width value."""
        self.width_value_label.configure(text=f"{int(value)} px")

    def update_quality_label(self, value: int) -> None:
        """Updates the label with the current quality value."""
        self.quality_value_label.configure(text=f"{int(value)} %")

    def log(self, message: str) -> None:
        """Logs a message to the log area."""
        self.log_area.configure(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.configure(state="disabled")
        self.log_area.see("end")

    def start_compression_thread(self) -> None:
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

    def run_compression(self, file_list: list[str], output_f: str, max_w: int, q: int) -> None:
        convert_files(file_list, output_f, max_w, q, self.log)
        self.start_button.configure(state="normal", text="🚀 Rozpocznij Kompresję")


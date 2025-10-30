from image_converter.gui import ImageConverterApp
import customtkinter as ctk

# --- running the application ---
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ImageConverterApp()
    app.mainloop()
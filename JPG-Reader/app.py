import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
from PIL.ExifTags import TAGS


def format_size(num_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def get_date_taken(image):
    exif = image.getexif()
    if not exif:
        return None
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "DateTimeOriginal":
            return value
    return None


class JPGReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG Reader")
        self.root.geometry("400x220")

        open_button = tk.Button(root, text="Open", command=self.open_image)
        open_button.pack(pady=10)

        convert_button = tk.Button(
            root,
            text="\U0001F5BC  PNG to JPG Converter",
            font=("TkDefaultFont", 12, "bold"),
            command=self.convert_png_to_jpg,
        )
        convert_button.pack(pady=(0, 10))

        self.info_label = tk.Label(root, text="No file selected.", justify="left", anchor="w")
        self.info_label.pack(fill="both", expand=True, padx=10, pady=10)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select a JPG image",
            filetypes=[("JPEG images", "*.jpg *.jpeg")],
        )
        if not file_path:
            return

        try:
            with Image.open(file_path) as image:
                width, height = image.size
                date_taken = get_date_taken(image)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not read image:\n{exc}")
            return

        file_name = os.path.basename(file_path)
        file_size = format_size(os.path.getsize(file_path))
        date_taken_text = date_taken if date_taken else "Not available"

        info_text = (
            f"File name: {file_name}\n"
            f"Pixel size: {width} x {height}\n"
            f"File size: {file_size}\n"
            f"Date taken: {date_taken_text}"
        )
        self.info_label.config(text=info_text)

    def convert_png_to_jpg(self):
        file_path = filedialog.askopenfilename(
            title="Select a PNG image",
            filetypes=[("PNG images", "*.png")],
        )
        if not file_path:
            return

        default_name = os.path.splitext(os.path.basename(file_path))[0] + ".jpg"
        save_path = filedialog.asksaveasfilename(
            title="Save as JPG",
            defaultextension=".jpg",
            initialfile=default_name,
            filetypes=[("JPEG images", "*.jpg *.jpeg")],
        )
        if not save_path:
            return

        try:
            with Image.open(file_path) as image:
                if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                    rgba_image = image.convert("RGBA")
                    flattened = Image.new("RGB", rgba_image.size, (255, 255, 255))
                    flattened.paste(rgba_image, mask=rgba_image.split()[3])
                else:
                    flattened = image.convert("RGB")
                flattened.save(save_path, "JPEG")
        except Exception as exc:
            messagebox.showerror("Error", f"Could not convert image:\n{exc}")
            return

        messagebox.showinfo("Success", f"Saved as:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JPGReaderApp(root)

    # Older Tk builds on macOS sometimes fail to paint colored widgets
    # until the window is resized; nudge the size once at startup to force it.
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    root.geometry(f"{width + 1}x{height + 1}")
    root.after(50, lambda: root.geometry(f"{width}x{height}"))

    root.mainloop()

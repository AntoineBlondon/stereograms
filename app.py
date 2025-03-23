from stereograms import *
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk




class StereogramApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Stereogram")
        self.geometry("800x600")
        self.depth_map = None
        self.result_image = None
        self.init_ui()
    
    def init_ui(self):
        self.upload_btn = tk.Button(self, text="Upload Depth Map", command=self.upload_depth_map)
        self.upload_btn.pack()

        self.options_frame = tk.Frame(self)
        self.options_frame.pack()

        tk.Label(self.options_frame, text="Pattern Width").grid(row=0, column=0)
        self.pattern_width = tk.Entry(self.options_frame)
        self.pattern_width.insert(0, "100")
        self.pattern_width.grid(row=0, column=1)

        tk.Label(self.options_frame, text="Max Depth Shift").grid(row=1, column=0)
        self.depth_shift = tk.Entry(self.options_frame)
        self.depth_shift.insert(0, "40")
        self.depth_shift.grid(row=1, column=1)

        self.generate_btn = tk.Button(self, text="Generate Stereogram", command=self.generate)
        self.generate_btn.pack()

        self.canvas = tk.Canvas(self, width=600, height=300)
        self.canvas.pack()

        self.save_btn = tk.Button(self, text="Save Image", command=self.save_image)
        self.save_btn.pack()

    def upload_depth_map(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.depth_map = load_depth_map(path)
            messagebox.showinfo("Loaded", "Depth map loaded successfully!")

    def generate(self):
        if self.depth_map is None:
            messagebox.showerror("Error", "Please upload a depth map first.")
            return

        try:
            pw = int(self.pattern_width.get())
            ds = int(self.depth_shift.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input.")
            return

        stereogram = generate_stereogram(self.depth_map, pw, ds)
        stereogram = add_guide_dots(stereogram, separation=ds*2)
        self.result_img = Image.fromarray(stereogram)
        self.tk_img = ImageTk.PhotoImage(self.result_img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def save_image(self):
        if self.result_img is None:
            messagebox.showerror("Error", "No image to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            self.result_img.save(path)
            messagebox.showinfo("Saved", f"Image saved to {path}")

if __name__ == "__main__":
    app = StereogramApp()
    app.mainloop()
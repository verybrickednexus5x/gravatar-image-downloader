import hashlib
import os
import requests
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from io import BytesIO

class GravatarPuller:
    def __init__(self):
        self.available_styles = {
            "Real Gravatar": "real_gravatar"
        }
        self.output_dir = None
        self.gravatar_size = 200
        
        # Setup the GUI
        self.setup_gui()
    
    def convert_string_to_md5_hash(self, input_string):
        """Convert a string to an MD5 hash."""
        m = hashlib.md5()
        m.update(input_string.encode('utf-8'))
        return m.hexdigest()
    
    def download_avatar(self, hash_value, style):
        """Download avatar with specified style and return image data."""
        if style == "real_gravatar":
            url = f'https://www.gravatar.com/avatar/{hash_value}?s={self.gravatar_size}&d=404'
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.content, url
                else:
                    messagebox.showinfo("No Gravatar Found", "No Gravatar found for this email address.")
                    return None, url
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Download Error", f"Failed to download Gravatar: {str(e)}")
                return None, url
        else:
            url = f'https://www.gravatar.com/avatar/{hash_value}?d={style}&s={self.gravatar_size}&f=y'
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise exception for bad responses
                return response.content, url
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Download Error", f"Failed to download {style}: {str(e)}")
                return None, url
    
    def save_avatar(self, image_data, style_name):
        """No longer saves avatar to a default directory. Only used for Download button."""
        return None
    
    def generate_avatars(self):
        """Generate avatars for all selected styles."""
        input_text = self.input_text.get()
        if not input_text:
            messagebox.showwarning("Input Missing", "Please enter some text!")
            return
        
        # Clear previous images
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Get selected styles
        selected_styles = []
        for style_name, var in self.style_vars.items():
            if var.get():
                selected_styles.append((style_name, self.available_styles[style_name]))
        
        if not selected_styles:
            messagebox.showwarning("Selection Missing", "Please select at least one avatar style!")
            return
        
        # Generate hash
        hash_value = self.convert_string_to_md5_hash(input_text)
        self.hash_display.config(text=f"MD5 Hash: {hash_value}")
        
        # Create a grid for the images
        row, col = 0, 0
        
        # Download and display avatars
        for style_name, style_code in selected_styles:
            image_data, url = self.download_avatar(hash_value, style_code)
            if image_data:
                # No longer save the image to a directory
                # file_path = self.save_avatar(image_data, style_code)
                
                # Display the image
                img = Image.open(BytesIO(image_data))
                photo = ImageTk.PhotoImage(img)
                
                # Create frame for this avatar
                avatar_frame = ttk.LabelFrame(self.preview_frame, text=style_name)
                avatar_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                # Add image label
                img_label = ttk.Label(avatar_frame, image=photo)
                img_label.image = photo  # Keep a reference
                img_label.pack(padx=5, pady=5)
                
                # Add URL label that's clickable
                url_var = tk.StringVar(value=url)
                link = ttk.Label(avatar_frame, text="Open URL", foreground="blue", cursor="hand2")
                link.pack(pady=2)
                link.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

                # Add Download button
                def download_image(data=image_data):
                    filetypes = [("PNG Image", "*.png")]
                    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
                    if save_path:
                        try:
                            with open(save_path, 'wb') as f:
                                f.write(data)
                            messagebox.showinfo("Download Complete", f"Avatar saved to {save_path}")
                        except Exception as e:
                            messagebox.showerror("Save Error", f"Failed to save avatar: {str(e)}")
                download_btn = ttk.Button(avatar_frame, text="Download", command=download_image)
                download_btn.pack(pady=2)
                
                # Update grid position
                col += 1
                if col > 1:  # 2 columns
                    col = 0
                    row += 1
    
    def select_all_styles(self):
        """Select all avatar styles."""
        for var in self.style_vars.values():
            var.set(True)
    
    def deselect_all_styles(self):
        """Deselect all avatar styles."""
        for var in self.style_vars.values():
            var.set(False)
    
    def setup_gui(self):
        """Set up the GUI for the application."""
        self.root = tk.Tk()
        self.root.title("Gravatar Puller")
        self.root.geometry("600x650")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Enter email to pull avatar:").pack(anchor=tk.W)
        self.input_text = ttk.Entry(input_frame, width=50)
        self.input_text.pack(fill=tk.X, pady=5)
        
        # Hash display
        self.hash_display = ttk.Label(input_frame, text="MD5 Hash: ")
        self.hash_display.pack(anchor=tk.W, pady=5)
        
        # Style selection frame
        style_frame = ttk.LabelFrame(main_frame, text="Avatar Source", padding="10")
        style_frame.pack(fill=tk.X, pady=10)
        
        # Create style checkbuttons
        self.style_vars = {}
        style_grid = ttk.Frame(style_frame)
        style_grid.pack(fill=tk.X)
        
        for i, style_name in enumerate(self.available_styles.keys()):
            self.style_vars[style_name] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(style_grid, text=style_name, variable=self.style_vars[style_name])
            cb.grid(row=i//3, column=i%3, sticky=tk.W, padx=10)
        
        # Select/Deselect buttons
        button_frame = ttk.Frame(style_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Select All", command=self.select_all_styles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all_styles).pack(side=tk.LEFT)
        
        # Pull Avatar button
        ttk.Button(main_frame, text="Pull Avatar", command=self.generate_avatars).pack(pady=10)
        
        # Preview frame (scrollable)
        preview_outer_frame = ttk.LabelFrame(main_frame, text="Avatar", padding="10")
        preview_outer_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add scrollbar
        canvas = tk.Canvas(preview_outer_frame)
        scrollbar = ttk.Scrollbar(preview_outer_frame, orient="vertical", command=canvas.yview)
        self.preview_frame = ttk.Frame(canvas)
        
        self.preview_frame.bind("<Configure>", 
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.preview_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = GravatarPuller()
    app.run()

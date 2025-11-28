import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from pathlib import Path
import zipfile
import tempfile
from datetime import datetime


class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Canvas Converter - 500x500")
        self.root.geometry("750x950")
        self.root.resizable(True, True)
        
        self.selected_image_path = None
        self.original_image = None
        self.preview_image = None
        self.bg_removed_image = None
        self.bg_removal_in_progress = False
        
        # Create tabbed interface
        self.create_tabbed_ui()
    
    def create_tabbed_ui(self):
        """Create tabbed interface with single and bulk conversion"""
        try:
            from tkinter import ttk
        except ImportError:
            messagebox.showerror("Error", "tkinter.ttk not available")
            return
        
        # Create notebook (tabbed widget)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.single_frame = ttk.Frame(self.notebook)
        self.bulk_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.single_frame, text="Single Image")
        self.notebook.add(self.bulk_frame, text="Multiple Images")
        
        # Setup UI for each tab
        self.setup_single_ui()
        self.setup_bulk_ui()
    
    def setup_single_ui(self):
        """Set up the single image user interface"""
        # Create scrollable frame
        canvas_frame = tk.Canvas(self.single_frame)
        scrollbar = tk.Scrollbar(self.single_frame, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = tk.Frame(canvas_frame)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        
        canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Single Image Conversion",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Convert a single image to 500x500 canvas with custom options",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        
        select_button = tk.Button(
            button_frame,
            text="Select Image",
            command=self.select_image,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_button.pack(side=tk.LEFT, padx=5)
        
        remove_bg_button = tk.Button(
            button_frame,
            text="Remove Background",
            command=self.remove_background,
            width=15,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        remove_bg_button.pack(side=tk.LEFT, padx=5)
        
        convert_button = tk.Button(
            button_frame,
            text="Convert & Save",
            command=self.convert_image,
            width=15,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        convert_button.pack(side=tk.LEFT, padx=5)
        
        # Background color option frame
        bg_frame = tk.LabelFrame(self.root, text="Background Color", font=("Arial", 10, "bold"))
        bg_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.bg_color_var = tk.StringVar(value="transparent")
        
        white_radio = tk.Radiobutton(
            bg_frame,
            text="White",
            variable=self.bg_color_var,
            value="white",
            font=("Arial", 9)
        )
        white_radio.pack(side=tk.LEFT, padx=10, pady=5)
        
        transparent_radio = tk.Radiobutton(
            bg_frame,
            text="Transparent (PNG only)",
            variable=self.bg_color_var,
            value="transparent",
            font=("Arial", 9)
        )
        transparent_radio.pack(side=tk.LEFT, padx=10, pady=5)
        
        # File info frame
        info_frame = tk.LabelFrame(self.root, text="Selected File", font=("Arial", 10, "bold"))
        info_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.file_label = tk.Label(
            info_frame,
            text="No file selected",
            font=("Arial", 9),
            fg="gray",
            wraplength=650,
            justify=tk.LEFT
        )
        self.file_label.pack(padx=10, pady=5)
        
        # Output filename frame
        filename_frame = tk.LabelFrame(self.root, text="Output Filename", font=("Arial", 10, "bold"))
        filename_frame.pack(padx=10, pady=5, fill=tk.X)
        
        filename_input_frame = tk.Frame(filename_frame)
        filename_input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(filename_input_frame, text="Filename:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.filename_var = tk.StringVar(value="")
        self.filename_entry = tk.Entry(
            filename_input_frame,
            textvariable=self.filename_var,
            font=("Arial", 9),
            width=50
        )
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Label(filename_input_frame, text=".png", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Image info frame
        image_info_frame = tk.LabelFrame(self.root, text="Original Image Info", font=("Arial", 10, "bold"))
        image_info_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.image_info_label = tk.Label(
            image_info_frame,
            text="Select an image to see details",
            font=("Arial", 9),
            fg="gray"
        )
        self.image_info_label.pack(padx=10, pady=5)
        
        # Background removal status frame
        self.bg_removal_frame = tk.LabelFrame(self.root, text="Background Removal Status", font=("Arial", 10, "bold"))
        self.bg_removal_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.bg_removal_label = tk.Label(
            self.bg_removal_frame,
            text="No background removal applied",
            font=("Arial", 9),
            fg="gray"
        )
        self.bg_removal_label.pack(padx=10, pady=5)
        
        # Preview frame
        preview_frame = tk.LabelFrame(self.root, text="Preview (500x500 Canvas)", font=("Arial", 10, "bold"))
        preview_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Zoom slider
        zoom_control_frame = tk.Frame(preview_frame)
        zoom_control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(zoom_control_frame, text="Zoom:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.zoom_slider = tk.Scale(
            zoom_control_frame,
            from_=0.5,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.zoom_var,
            command=self.on_zoom_change,
            font=("Arial", 9)
        )
        self.zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.zoom_label = tk.Label(zoom_control_frame, text="100%", font=("Arial", 9), width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(
            preview_frame,
            width=350,
            height=350,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 9),
            fg="green"
        )
        self.status_label.pack(pady=5)
    
    def select_image(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.original_image = Image.open(file_path)
            
            # Update file label
            file_name = os.path.basename(file_path)
            self.file_label.config(text=f"📁 {file_name}", fg="black")
            
            # Populate filename field with image name (without extension)
            name_without_ext = os.path.splitext(file_name)[0]
            self.filename_var.set(name_without_ext)
            
            # Update image info
            width, height = self.original_image.size
            aspect_ratio = width / height
            file_size = os.path.getsize(file_path) / 1024  # KB
            self.image_info_label.config(
                text=f"Dimensions: {width}x{height} | Aspect Ratio: {aspect_ratio:.2f} | Size: {file_size:.1f} KB",
                fg="black"
            )
            
            # Show preview
            self.show_preview()
            self.status_label.config(text="Image loaded successfully", fg="green")
            
            # Reset background removal status
            self.bg_removed_image = None
            self.bg_removal_label.config(text="No background removal applied", fg="gray")
    
    def remove_background(self):
        """Remove background from the selected image"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.status_label.config(text="Removing background... this may take a moment", fg="orange")
            self.root.update()
            
            # Remove background using rembg
            from rembg import remove
            self.bg_removed_image = remove(self.original_image)
            
            # Convert to RGBA if not already
            if self.bg_removed_image.mode != 'RGBA':
                self.bg_removed_image = self.bg_removed_image.convert('RGBA')
            
            # Find the bounding box of the non-transparent content
            bbox = self.bg_removed_image.getbbox()
            
            if bbox:
                # Crop to the content
                cropped = self.bg_removed_image.crop(bbox)
                
                # Get dimensions
                crop_width, crop_height = cropped.size
                canvas_size = 500
                
                # Calculate scaling to fit in canvas while preserving aspect ratio
                scale_factor = min(canvas_size / crop_width, canvas_size / crop_height)
                new_width = int(crop_width * scale_factor)
                new_height = int(crop_height * scale_factor)
                
                # Resize the cropped image
                resized = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create a transparent canvas
                centered_image = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
                
                # Calculate position to center
                x_offset = (canvas_size - new_width) // 2
                y_offset = (canvas_size - new_height) // 2
                
                # Paste the resized image centered
                centered_image.paste(resized, (x_offset, y_offset), resized)
                
                # Update the background removed image
                self.bg_removed_image = centered_image
            
            # Update status
            self.bg_removal_label.config(
                text="✓ Background removed and centered successfully",
                fg="green"
            )
            self.status_label.config(text="Background removed - Ready to convert", fg="green")
            
            # Update preview with the background-removed image
            self.show_preview()
            
            messagebox.showinfo(
                "Success",
                "Background removed and centered successfully!\n\n"
                "The image is now centered on the 500x500 canvas.\n"
                "Click 'Convert & Save' to export."
            )
        except Exception as e:
            self.bg_removal_label.config(text=f"Error: {str(e)}", fg="red")
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to remove background:\n{str(e)}")
    
    
    def show_preview(self):
        """Display preview of the converted image on canvas"""
        if not self.original_image:
            return
        
        # Get current zoom level
        zoom_level = self.zoom_var.get()
        
        # Use background-removed image if available, otherwise use original
        image_to_preview = self.bg_removed_image if self.bg_removed_image else self.original_image
        
        # Scale image to fill 500x500 while preserving aspect ratio (without background yet)
        preview_image = self.scale_to_fill_internal(image_to_preview, 500, 500, zoom_level)
        self.preview_image = preview_image
        
        # Scale down for display (350x350) while preserving aspect ratio
        display_size = 350
        preview_image_resized = preview_image.resize((display_size, display_size), Image.Resampling.LANCZOS)
        
        # Use PPM format for better compatibility
        import io
        with io.BytesIO() as output:
            preview_image_resized.save(output, format="PPM")
            data = output.getvalue()
        
        photo = tk.PhotoImage(data=data)
        self.canvas.delete("all")
        self.canvas.create_image(175, 175, image=photo)
        self.canvas.image = photo
    
    def on_zoom_change(self, value):
        """Handle zoom slider changes"""
        zoom_level = float(value)
        self.zoom_label.config(text=f"{int(zoom_level * 100)}%")
        self.show_preview()
    
    def scale_to_fill_internal(self, image, target_width, target_height, zoom_level=1.0):
        """
        Scale image with zoom applied for preview purposes (no background).
        
        Args:
            image: PIL Image object
            target_width: Target canvas width
            target_height: Target canvas height
            zoom_level: Zoom multiplier (1.0 = fit, >1.0 = zoom in, <1.0 = zoom out)
        
        Returns:
            PIL Image object scaled and zoomed
        """
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            # Image is wider, scale by width
            new_width = target_width
            new_height = int(new_width / img_aspect)
        else:
            # Image is taller, scale by height
            new_height = target_height
            new_width = int(new_height * img_aspect)
        
        # Apply zoom
        new_width = int(new_width * zoom_level)
        new_height = int(new_height * zoom_level)
        
        # Scale the image
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create canvas with white background for preview
        canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Center the scaled image on the canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Clip if zoomed in too much
        if x_offset < 0 or y_offset < 0:
            # Crop the image to fit
            left = max(0, -x_offset)
            top = max(0, -y_offset)
            right = left + target_width
            bottom = top + target_height
            scaled_image = scaled_image.crop((left, top, right, bottom))
            x_offset = 0
            y_offset = 0
        
        canvas.paste(scaled_image, (x_offset, y_offset))
        return canvas
    
    def scale_to_fill_with_zoom(self, image, target_width, target_height, zoom_level=1.0, background_color=(255, 255, 255)):
        """
        Scale image with zoom applied and add background for export.
        
        Args:
            image: PIL Image object
            target_width: Target canvas width
            target_height: Target canvas height
            zoom_level: Zoom multiplier (1.0 = fit, >1.0 = zoom in, <1.0 = zoom out)
            background_color: RGB tuple for background, or None for transparent
        
        Returns:
            PIL Image object scaled, zoomed and with background
        """
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            # Image is wider, scale by width
            new_width = target_width
            new_height = int(new_width / img_aspect)
        else:
            # Image is taller, scale by height
            new_height = target_height
            new_width = int(new_height * img_aspect)
        
        # Apply zoom
        new_width = int(new_width * zoom_level)
        new_height = int(new_height * zoom_level)
        
        # Scale the image
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Determine image mode (RGBA for transparent, RGB for colored background)
        if background_color is None:
            # Transparent background
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            if scaled_image.mode != 'RGBA':
                scaled_image = scaled_image.convert('RGBA')
        else:
            # Colored background
            canvas = Image.new('RGB', (target_width, target_height), background_color)
            if scaled_image.mode == 'RGBA':
                scaled_image = scaled_image.convert('RGB')
        
        # Center the scaled image on the canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Handle clipping when zoomed in
        if x_offset < 0 or y_offset < 0:
            # Crop the image to fit
            left = max(0, -x_offset)
            top = max(0, -y_offset)
            right = left + target_width
            bottom = top + target_height
            scaled_image = scaled_image.crop((left, top, right, bottom))
            x_offset = 0
            y_offset = 0
        
        canvas.paste(scaled_image, (x_offset, y_offset))
        return canvas
    
    def get_image_data(self, image):
        """Convert PIL image to pixel data for PhotoImage"""
        pixels = image.getdata()
        width, height = image.size
        return [pixels[i*width:(i+1)*width] for i in range(height)]
    
    def scale_to_fill(self, image, target_width, target_height, background_color=(255, 255, 255)):
        """
        Scale image to fit within the target canvas while preserving aspect ratio.
        Fills empty space with background color (letterbox style).
        
        Args:
            image: PIL Image object
            target_width: Target canvas width
            target_height: Target canvas height
            background_color: RGB tuple for background, or None for transparent
        
        Returns:
            PIL Image object scaled and letterboxed to target dimensions
        """
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            # Image is wider, scale by width
            new_width = target_width
            new_height = int(new_width / img_aspect)
        else:
            # Image is taller, scale by height
            new_height = target_height
            new_width = int(new_height * img_aspect)
        
        # Scale the image
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Determine image mode (RGBA for transparent, RGB for colored background)
        if background_color is None:
            # Transparent background
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            if scaled_image.mode != 'RGBA':
                scaled_image = scaled_image.convert('RGBA')
        else:
            # Colored background
            canvas = Image.new('RGB', (target_width, target_height), background_color)
            if scaled_image.mode == 'RGBA':
                scaled_image = scaled_image.convert('RGB')
        
        # Center the scaled image on the canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        canvas.paste(scaled_image, (x_offset, y_offset))
        
        return canvas
    
    def convert_image(self):
        """Convert and save the image"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        # Validate filename
        custom_filename = self.filename_var.get().strip()
        if not custom_filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        # Get background color based on selection
        bg_choice = self.bg_color_var.get()
        if bg_choice == "transparent":
            background_color = None
        else:
            background_color = (255, 255, 255)  # white
        
        # Get zoom level
        zoom_level = self.zoom_var.get()
        
        # Get save location with custom filename
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=custom_filename,
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if not save_path:
            return
        
        try:
            # Warn if transparent is selected but saving as JPEG
            if bg_choice == "transparent" and save_path.lower().endswith('.jpg'):
                messagebox.showwarning(
                    "Warning",
                    "JPEG format does not support transparency.\n"
                    "The background will be white instead.\n\n"
                    "Use PNG format to preserve transparency."
                )
                background_color = (255, 255, 255)
            
            # Use background-removed image if available, otherwise use original
            image_to_convert = self.bg_removed_image if self.bg_removed_image else self.original_image
            
            # Scale to fill with zoom and convert
            converted_image = self.scale_to_fill_with_zoom(image_to_convert, 500, 500, zoom_level, background_color)
            
            # Save the image
            if save_path.lower().endswith('.png') and bg_choice == "transparent":
                converted_image.save(save_path, 'PNG')
            else:
                converted_image.save(save_path, quality=95)
            
            file_size = os.path.getsize(save_path) / 1024  # KB
            self.status_label.config(
                text=f"✓ Image saved successfully to {os.path.basename(save_path)} ({file_size:.1f} KB)",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"Image converted and saved!\n\n"
                f"Location: {save_path}\n"
                f"Size: {file_size:.1f} KB\n"
                f"Background: {bg_choice.capitalize()}\n"
                f"Zoom: {int(zoom_level * 100)}%\n"
                f"Processing: {'Background Removed + ' if self.bg_removed_image else ''}Converted"
            )
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

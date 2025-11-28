import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
from pathlib import Path
import zipfile
import tempfile
from threading import Thread
import csv
import shutil
 
 
 

 
 


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Canvas Converter - 500x500")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)
        
        # Single image tab variables
        self.selected_image_path = None
        self.original_image = None
        self.preview_image = None
        self.bg_removed_image = None
        self.offset_x = 0
        self.offset_y = 0
        self.list_renamer_files = []
        self.list_renamer_selected_index = None
        self.list_renamer_preview_image = None
        
        # Image sorter tab variables
        self.sorter_source_folder = None
        self.sorter_image_groups = {}
        self.sorter_progress_var = tk.DoubleVar(value=0)
        self.sorter_similarity_threshold = tk.DoubleVar(value=0.85)
        self.sorter_min_group_size = tk.IntVar(value=2)
        
        # High res grabber tab variables
        self.high_res_source_folders = []
        self.high_res_output_folder = "Final-Highres"
        self.high_res_progress_var = tk.DoubleVar(value=0)
        self.high_res_status_label = None
        self.high_res_results_text = None
        

        
        # Create tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.single_frame = ttk.Frame(self.notebook)
        self.bulk_frame = ttk.Frame(self.notebook)
        self.csv_frame = ttk.Frame(self.notebook)
        self.text_format_frame = ttk.Frame(self.notebook)
        self.renamer_frame = ttk.Frame(self.notebook)
        self.list_renamer_frame = ttk.Frame(self.notebook)
        self.image_sorter_frame = ttk.Frame(self.notebook)
        self.high_res_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.single_frame, text="Single Image")
        self.notebook.add(self.bulk_frame, text="Multiple Images")
        self.notebook.add(self.csv_frame, text="Filename → CSV")
        self.notebook.add(self.text_format_frame, text="Text Formatting")
        self.notebook.add(self.renamer_frame, text="Smart Renamer")
        self.notebook.add(self.list_renamer_frame, text="List Renamer")
        self.notebook.add(self.image_sorter_frame, text="Image Sorter")
        self.notebook.add(self.high_res_frame, text="Grab High Res Image")
        
        self.setup_single_ui()
        self.setup_bulk_ui()
        self.setup_csv_ui()
        self.setup_text_format_ui()
        self.setup_renamer_ui()
        self.setup_list_renamer_ui()
        self.setup_image_sorter_ui()
        self.setup_high_res_ui()
    
    def setup_single_ui(self):
        """Set up the single image conversion UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.single_frame)
        scrollbar = tk.Scrollbar(self.single_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
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
        
        # Two-column layout to keep settings on the left and preview on the right
        content_frame = tk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        left_column = tk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(content_frame)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Background color option frame
        bg_frame = tk.LabelFrame(left_column, text="Background Color", font=("Arial", 10, "bold"))
        bg_frame.pack(padx=0, pady=10, fill=tk.X)
        
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
        info_frame = tk.LabelFrame(left_column, text="Selected File", font=("Arial", 10, "bold"))
        info_frame.pack(padx=0, pady=10, fill=tk.X)
        
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
        filename_frame = tk.LabelFrame(left_column, text="Output Filename", font=("Arial", 10, "bold"))
        filename_frame.pack(padx=0, pady=5, fill=tk.X)
        
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
        image_info_frame = tk.LabelFrame(left_column, text="Original Image Info", font=("Arial", 10, "bold"))
        image_info_frame.pack(padx=0, pady=5, fill=tk.X)
        
        self.image_info_label = tk.Label(
            image_info_frame,
            text="Select an image to see details",
            font=("Arial", 9),
            fg="gray"
        )
        self.image_info_label.pack(padx=10, pady=5)
        
        # Background removal status frame
        self.bg_removal_frame = tk.LabelFrame(left_column, text="Background Removal Status", font=("Arial", 10, "bold"))
        self.bg_removal_frame.pack(padx=0, pady=5, fill=tk.X)
        
        self.bg_removal_label = tk.Label(
            self.bg_removal_frame,
            text="No background removal applied",
            font=("Arial", 9),
            fg="gray"
        )
        self.bg_removal_label.pack(padx=10, pady=5)
        
        # Preview frame sits on the right column
        preview_frame = tk.LabelFrame(right_column, text="Preview (500x500 Canvas)", font=("Arial", 10, "bold"))
        preview_frame.pack(padx=0, pady=5, fill=tk.BOTH, expand=True)
        
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
        
        # Pan controls
        pan_control_frame = tk.Frame(preview_frame)
        pan_control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(pan_control_frame, text="Position:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # X offset control
        tk.Label(pan_control_frame, text="X:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.offset_x_var = tk.IntVar(value=0)
        self.offset_x_slider = tk.Scale(
            pan_control_frame,
            from_=-250,
            to=250,
            resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.offset_x_var,
            command=self.on_offset_change,
            font=("Arial", 8),
            length=150
        )
        self.offset_x_slider.pack(side=tk.LEFT, padx=2)
        
        # Y offset control
        tk.Label(pan_control_frame, text="Y:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.offset_y_var = tk.IntVar(value=0)
        self.offset_y_slider = tk.Scale(
            pan_control_frame,
            from_=-250,
            to=250,
            resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.offset_y_var,
            command=self.on_offset_change,
            font=("Arial", 8),
            length=150
        )
        self.offset_y_slider.pack(side=tk.LEFT, padx=2)
        
        # Auto-align and reset buttons
        align_button_frame = tk.Frame(preview_frame)
        align_button_frame.pack(padx=10, pady=5)
        
        auto_align_button = tk.Button(
            align_button_frame,
            text="Auto-Align (Alpha)",
            command=self.auto_align_image,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        auto_align_button.pack(side=tk.LEFT, padx=5)
        
        reset_position_button = tk.Button(
            align_button_frame,
            text="Reset Position",
            command=self.reset_position,
            bg="#607D8B",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        reset_position_button.pack(side=tk.LEFT, padx=5)
        
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
            scrollable_frame,
            text="Ready",
            font=("Arial", 9),
            fg="green"
        )
        self.status_label.pack(pady=5)
    
    def setup_bulk_ui(self):
        """Set up the bulk image conversion UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.bulk_frame)
        scrollbar = tk.Scrollbar(self.bulk_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Bulk Image Conversion",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Convert multiple images to 500x500 canvas with automatic settings",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Settings frame
        settings_frame = tk.LabelFrame(scrollable_frame, text="Bulk Conversion Settings", font=("Arial", 10, "bold"))
        settings_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Background removal checkbox
        self.bulk_remove_bg_var = tk.BooleanVar(value=True)
        remove_bg_checkbox = tk.Checkbutton(
            settings_frame,
            text="Remove background automatically",
            variable=self.bulk_remove_bg_var,
            font=("Arial", 9)
        )
        remove_bg_checkbox.pack(padx=10, pady=5, anchor=tk.W)
        
        settings_info = tk.Label(
            settings_frame,
            text="✓ Transparent background\n✓ Centered positioning\n✓ Export as ZIP file",
            font=("Arial", 9),
            fg="darkgreen",
            justify=tk.LEFT
        )
        settings_info.pack(padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=15)
        
        select_folder_button = tk.Button(
            button_frame,
            text="Select Folder",
            command=self.select_bulk_folder,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_folder_button.pack(side=tk.LEFT, padx=5)
        
        convert_all_button = tk.Button(
            button_frame,
            text="Convert All & Export ZIP",
            command=self.convert_bulk_images,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        convert_all_button.pack(side=tk.LEFT, padx=5)
        
        # Folder info frame
        self.bulk_folder_frame = tk.LabelFrame(scrollable_frame, text="Selected Folder", font=("Arial", 10, "bold"))
        self.bulk_folder_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.bulk_folder_label = tk.Label(
            self.bulk_folder_frame,
            text="No folder selected",
            font=("Arial", 9),
            fg="gray",
            wraplength=650,
            justify=tk.LEFT
        )
        self.bulk_folder_label.pack(padx=10, pady=10)
        
        # Progress frame
        self.bulk_progress_frame = tk.LabelFrame(scrollable_frame, text="Progress", font=("Arial", 10, "bold"))
        self.bulk_progress_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.bulk_progress_label = tk.Label(
            self.bulk_progress_frame,
            text="No conversion in progress",
            font=("Arial", 9),
            fg="gray"
        )
        self.bulk_progress_label.pack(padx=10, pady=10)
        
        # Status bar
        self.bulk_status_label = tk.Label(
            scrollable_frame,
            text="Ready",
            font=("Arial", 9),
            fg="green"
        )
        self.bulk_status_label.pack(pady=5)
        
        # Store folder path for bulk operations
        self.bulk_folder_path = None
    
    def setup_csv_ui(self):
        """Set up the CSV filename generation UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.csv_frame)
        scrollbar = tk.Scrollbar(self.csv_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Filename to CSV Converter",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Extract filenames from files and export as CSV",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=15)
        
        select_files_button = tk.Button(
            button_frame,
            text="Select Files",
            command=self.csv_select_files,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_files_button.pack(side=tk.LEFT, padx=5)
        
        clear_list_button = tk.Button(
            button_frame,
            text="Clear List",
            command=self.csv_clear_list,
            width=20,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        clear_list_button.pack(side=tk.LEFT, padx=5)
        
        export_csv_button = tk.Button(
            button_frame,
            text="Export to CSV",
            command=self.csv_export,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        export_csv_button.pack(side=tk.LEFT, padx=5)
        
        # Filenames list frame
        list_frame = tk.LabelFrame(scrollable_frame, text="Filename List", font=("Arial", 10, "bold"))
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.csv_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=list_scrollbar.set,
            font=("Arial", 9),
            height=15
        )
        self.csv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        list_scrollbar.config(command=self.csv_listbox.yview)
        
        # Counter frame
        counter_frame = tk.Frame(scrollable_frame)
        counter_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.csv_counter_label = tk.Label(
            counter_frame,
            text="Total files: 0",
            font=("Arial", 9),
            fg="gray"
        )
        self.csv_counter_label.pack(side=tk.LEFT)
        
        # Status bar
        self.csv_status_label = tk.Label(
            scrollable_frame,
            text="Ready - Select files to begin",
            font=("Arial", 9),
            fg="green"
        )
        self.csv_status_label.pack(pady=5)
        
        # Store filenames list
        self.csv_filenames = []
    
    def setup_text_format_ui(self):
        """Set up the text formatting UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.text_format_frame)
        scrollbar = tk.Scrollbar(self.text_format_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Text Formatting Tool",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Combine multiple links with custom separator",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Separator configuration frame
        sep_frame = tk.LabelFrame(scrollable_frame, text="Separator Configuration", font=("Arial", 10, "bold"))
        sep_frame.pack(padx=10, pady=10, fill=tk.X)
        
        sep_label_frame = tk.Frame(sep_frame)
        sep_label_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(sep_label_frame, text="Separator Character:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.text_format_sep_var = tk.StringVar(value=",")
        sep_entry = tk.Entry(
            sep_label_frame,
            textvariable=self.text_format_sep_var,
            font=("Arial", 9),
            width=20
        )
        sep_entry.pack(side=tk.LEFT, padx=5)
        
        # Examples
        examples_label = tk.Label(
            sep_frame,
            text="Examples: , (comma)  |  ; (semicolon)  |  | (pipe)  |  → (arrow)  |  (space)",
            font=("Arial", 8),
            fg="gray"
        )
        examples_label.pack(padx=10, pady=5)
        
        # Input section
        input_frame = tk.LabelFrame(scrollable_frame, text="Input Text (Paste links here)", font=("Arial", 10, "bold"))
        input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Text input with scrollbar
        input_scrollbar = tk.Scrollbar(input_frame)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_format_input = tk.Text(
            input_frame,
            height=10,
            font=("Arial", 9),
            yscrollcommand=input_scrollbar.set,
            wrap=tk.WORD
        )
        self.text_format_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        input_scrollbar.config(command=self.text_format_input.yview)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        
        clear_input_button = tk.Button(
            button_frame,
            text="Clear Input",
            command=self.text_format_clear_input,
            width=20,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        clear_input_button.pack(side=tk.LEFT, padx=5)
        
        format_button = tk.Button(
            button_frame,
            text="Format Text",
            command=self.text_format_format,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        format_button.pack(side=tk.LEFT, padx=5)
        
        copy_button = tk.Button(
            button_frame,
            text="Copy to Clipboard",
            command=self.text_format_copy,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        copy_button.pack(side=tk.LEFT, padx=5)
        
        save_button = tk.Button(
            button_frame,
            text="Save as Text",
            command=self.text_format_save,
            width=20,
            height=2,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold")
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = tk.LabelFrame(scrollable_frame, text="Formatted Output", font=("Arial", 10, "bold"))
        output_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Output scrollbar
        output_scrollbar = tk.Scrollbar(output_frame)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_format_output = tk.Text(
            output_frame,
            height=10,
            font=("Arial", 9),
            yscrollcommand=output_scrollbar.set,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.text_format_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        output_scrollbar.config(command=self.text_format_output.yview)
        
        # Status bar
        self.text_format_status_label = tk.Label(
            scrollable_frame,
            text="Ready - Paste links and click Format Text",
            font=("Arial", 9),
            fg="green"
        )
        self.text_format_status_label.pack(pady=5)
    
    # ==================== SINGLE IMAGE METHODS ====================
    
    def select_image(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
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
            file_size = os.path.getsize(file_path) / 1024
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
        
        # Get current zoom level and offsets
        zoom_level = self.zoom_var.get()
        offset_x = self.offset_x_var.get()
        offset_y = self.offset_y_var.get()
        
        # Use background-removed image if available, otherwise use original
        image_to_preview = self.bg_removed_image if self.bg_removed_image else self.original_image
        
        # Scale image to fill 500x500 while preserving aspect ratio
        preview_image = self.scale_to_fill_internal(image_to_preview, 500, 500, zoom_level, offset_x, offset_y)
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
    
    def on_offset_change(self, value):
        """Called when offset sliders change"""
        self.offset_x = self.offset_x_var.get()
        self.offset_y = self.offset_y_var.get()
        self.show_preview()
    
    def reset_position(self):
        """Reset position to center"""
        self.offset_x_var.set(0)
        self.offset_y_var.set(0)
        self.offset_x = 0
        self.offset_y = 0
        self.show_preview()
    
    def auto_align_image(self):
        """Auto-align image based on alpha channel or active pixels"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
        
        # Use the background-removed image if available, otherwise use original
        image_to_align = self.bg_removed_image if self.bg_removed_image else self.original_image
        
        # Convert to RGBA if needed
        if image_to_align.mode != 'RGBA':
            image_to_align = image_to_align.convert('RGBA')
        
        # Get the bounding box of non-transparent pixels
        bbox = image_to_align.getbbox()
        
        if bbox is None:
            messagebox.showinfo("Auto-Align", "Image appears to be completely transparent or empty.")
            return
        
        # Calculate the center of the content
        content_left, content_top, content_right, content_bottom = bbox
        content_center_x = (content_left + content_right) / 2
        content_center_y = (content_top + content_bottom) / 2
        
        # Calculate image center
        img_center_x = image_to_align.width / 2
        img_center_y = image_to_align.height / 2
        
        # Calculate offset needed to center the content
        # Scale the offset based on zoom and canvas size
        zoom_level = self.zoom_var.get()
        
        # Calculate how the image is scaled to fit in the canvas
        img_width, img_height = image_to_align.size
        target_width, target_height = 500, 500
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            scale_factor = target_width / img_width
        else:
            scale_factor = target_height / img_height
        
        # Apply zoom to scale factor
        scale_factor *= zoom_level
        
        # Calculate offset in canvas coordinates
        offset_x = int((img_center_x - content_center_x) * scale_factor)
        offset_y = int((img_center_y - content_center_y) * scale_factor)
        
        # Clamp offsets to slider range
        offset_x = max(-250, min(250, offset_x))
        offset_y = max(-250, min(250, offset_y))
        
        # Apply offsets
        self.offset_x_var.set(offset_x)
        self.offset_y_var.set(offset_y)
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.show_preview()
        
        messagebox.showinfo(
            "Auto-Align Complete",
            f"Image aligned based on alpha channel content.\n\nOffset X: {offset_x}\nOffset Y: {offset_y}"
        )
    
    def scale_to_fill_internal(self, image, target_width, target_height, zoom_level=1.0, offset_x=0, offset_y=0):
        """Scale image with zoom applied for preview purposes"""
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            new_width = target_width
            new_height = int(new_width / img_aspect)
        else:
            new_height = target_height
            new_width = int(new_height * img_aspect)
        
        # Apply zoom
        new_width = int(new_width * zoom_level)
        new_height = int(new_height * zoom_level)
        
        # Scale the image
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create canvas with white background for preview
        canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Center the scaled image on the canvas with offset
        x_pos = (target_width - new_width) // 2 + offset_x
        y_pos = (target_height - new_height) // 2 + offset_y
        
        # Clip if zoomed in too much or offset causes overflow
        if x_pos < 0 or y_pos < 0 or x_pos + new_width > target_width or y_pos + new_height > target_height:
            left = max(0, -x_pos)
            top = max(0, -y_pos)
            right = min(new_width, left + target_width - max(0, x_pos))
            bottom = min(new_height, top + target_height - max(0, y_pos))
            scaled_image = scaled_image.crop((left, top, right, bottom))
            x_pos = max(0, x_pos)
            y_pos = max(0, y_pos)
        
        canvas.paste(scaled_image, (x_pos, y_pos))
        return canvas
    
    def scale_to_fill_with_zoom(self, image, target_width, target_height, zoom_level=1.0, background_color=(255, 255, 255), offset_x=0, offset_y=0):
        """Scale image with zoom applied and add background for export"""
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            new_width = target_width
            new_height = int(new_width / img_aspect)
        else:
            new_height = target_height
            new_width = int(new_height * img_aspect)
        
        # Apply zoom
        new_width = int(new_width * zoom_level)
        new_height = int(new_height * zoom_level)
        
        # Scale the image
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Determine image mode (RGBA for transparent, RGB for colored background)
        if background_color is None:
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            if scaled_image.mode != 'RGBA':
                scaled_image = scaled_image.convert('RGBA')
        else:
            canvas = Image.new('RGB', (target_width, target_height), background_color)
            if scaled_image.mode == 'RGBA':
                scaled_image = scaled_image.convert('RGB')
        
        # Center the scaled image on the canvas with offset
        x_pos = (target_width - new_width) // 2 + offset_x
        y_pos = (target_height - new_height) // 2 + offset_y
        
        # Handle clipping when zoomed in or offset causes overflow
        if x_pos < 0 or y_pos < 0 or x_pos + new_width > target_width or y_pos + new_height > target_height:
            left = max(0, -x_pos)
            top = max(0, -y_pos)
            right = min(new_width, left + target_width - max(0, x_pos))
            bottom = min(new_height, top + target_height - max(0, y_pos))
            scaled_image = scaled_image.crop((left, top, right, bottom))
            x_pos = max(0, x_pos)
            y_pos = max(0, y_pos)
        
        canvas.paste(scaled_image, (x_pos, y_pos))
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
            background_color = (255, 255, 255)
        
        # Get zoom level and offsets
        zoom_level = self.zoom_var.get()
        offset_x = self.offset_x_var.get()
        offset_y = self.offset_y_var.get()
        
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
            converted_image = self.scale_to_fill_with_zoom(image_to_convert, 500, 500, zoom_level, background_color, offset_x, offset_y)
            
            # Save the image
            if save_path.lower().endswith('.png') and bg_choice == "transparent":
                converted_image.save(save_path, 'PNG')
            else:
                converted_image.save(save_path, quality=95)
            
            file_size = os.path.getsize(save_path) / 1024
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
    
    # ==================== BULK IMAGE METHODS ====================
    
    def select_bulk_folder(self):
        """Select folder for bulk conversion"""
        folder_path = filedialog.askdirectory(title="Select folder with images")
        
        if folder_path:
            self.bulk_folder_path = folder_path
            
            # Get supported image files
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
            image_files = [f for f in os.listdir(folder_path) 
                          if os.path.isfile(os.path.join(folder_path, f)) 
                          and f.lower().endswith(supported_extensions)]
            
            # Update label
            folder_name = os.path.basename(folder_path)
            self.bulk_folder_label.config(
                text=f"📁 {folder_name}\n{len(image_files)} image(s) found",
                fg="black"
            )
            self.bulk_status_label.config(text="Folder selected - Ready to convert", fg="green")
    
    def convert_bulk_images(self):
        """Convert all images in the selected folder"""
        if not self.bulk_folder_path:
            messagebox.showwarning("Warning", "Please select a folder first")
            return
        
        # Ask where to save ZIP file
        zip_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialfile="converted_images.zip"
        )
        
        if not zip_path:
            return
        
        # Run conversion in separate thread
        thread = Thread(target=self._bulk_convert_thread, args=(zip_path,))
        thread.start()
    
    def _bulk_convert_thread(self, zip_path):
        """Bulk conversion thread"""
        try:
            self.bulk_status_label.config(text="Processing... Please wait", fg="orange")
            self.root.update()
            
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
            image_files = [f for f in os.listdir(self.bulk_folder_path) 
                          if os.path.isfile(os.path.join(self.bulk_folder_path, f)) 
                          and f.lower().endswith(supported_extensions)]
            
            if not image_files:
                messagebox.showwarning("Warning", "No supported images found in the folder")
                self.bulk_status_label.config(text="No images found", fg="red")
                return
            
            # Create temporary directory for processed images
            temp_dir = tempfile.mkdtemp()
            
            processed_count = 0
            
            # Process each image
            for i, filename in enumerate(image_files, 1):
                try:
                    self.bulk_progress_label.config(
                        text=f"Processing {i}/{len(image_files)}: {filename}",
                        fg="blue"
                    )
                    self.root.update()
                    
                    # Load image
                    image_path = os.path.join(self.bulk_folder_path, filename)
                    original_image = Image.open(image_path)
                    
                    # Remove background if checkbox is enabled
                    if self.bulk_remove_bg_var.get():
                        from rembg import remove
                        bg_removed = remove(original_image)
                        
                        if bg_removed.mode != 'RGBA':
                            bg_removed = bg_removed.convert('RGBA')
                    else:
                        # Use original image without background removal
                        bg_removed = original_image
                        if bg_removed.mode != 'RGBA':
                            bg_removed = bg_removed.convert('RGBA')
                    
                    # Find bounding box and center
                    bbox = bg_removed.getbbox()
                    if bbox:
                        cropped = bg_removed.crop(bbox)
                        crop_width, crop_height = cropped.size
                        canvas_size = 500
                        
                        scale_factor = min(canvas_size / crop_width, canvas_size / crop_height)
                        new_width = int(crop_width * scale_factor)
                        new_height = int(crop_height * scale_factor)
                        
                        resized = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        centered_image = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
                        
                        x_offset = (canvas_size - new_width) // 2
                        y_offset = (canvas_size - new_height) // 2
                        
                        centered_image.paste(resized, (x_offset, y_offset), resized)
                        bg_removed = centered_image
                    
                    # Save as PNG with transparent background
                    name_without_ext = os.path.splitext(filename)[0]
                    output_filename = f"{name_without_ext}.png"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    bg_removed.save(output_path, 'PNG')
                    processed_count += 1
                    
                except Exception as e:
                    self.bulk_progress_label.config(text=f"Error processing {filename}: {str(e)}", fg="red")
                    continue
            
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    zipf.write(file_path, arcname=filename)
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
            
            zip_size = os.path.getsize(zip_path) / 1024
            
            self.bulk_progress_label.config(
                text=f"✓ Completed! {processed_count}/{len(image_files)} images processed",
                fg="green"
            )
            self.bulk_status_label.config(
                text=f"✓ ZIP saved successfully ({zip_size:.1f} KB)",
                fg="green"
            )
            
            bg_removal_status = "Background removed automatically" if self.bulk_remove_bg_var.get() else "Original background preserved"
            messagebox.showinfo(
                "Success",
                f"Bulk conversion completed!\n\n"
                f"Processed: {processed_count}/{len(image_files)} images\n"
                f"Output ZIP: {os.path.basename(zip_path)}\n"
                f"Size: {zip_size:.1f} KB\n\n"
                f"All images were:\n"
                f"• {bg_removal_status}\n"
                f"• Centered on 500x500 canvas\n"
                f"• Saved with transparent background"
            )
            
        except Exception as e:
            self.bulk_status_label.config(text=f"Error: {str(e)}", fg="red")
            self.bulk_progress_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Bulk conversion failed:\n{str(e)}")
    
    # ==================== CSV METHODS ====================
    
    def csv_select_files(self):
        """Select files to extract filenames from"""
        file_paths = filedialog.askopenfilenames(
            title="Select files to extract filenames",
            filetypes=[("All files", "*.*")]
        )
        
        if file_paths:
            # Extract filenames without extensions
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                name_without_ext = os.path.splitext(filename)[0]
                
                # Add only if not already in list
                if name_without_ext not in self.csv_filenames:
                    self.csv_filenames.append(name_without_ext)
            
            # Update listbox
            self.csv_update_listbox()
            self.csv_status_label.config(text=f"Added {len(file_paths)} file(s)", fg="green")
    
    def csv_clear_list(self):
        """Clear the filenames list"""
        if messagebox.askyesno("Confirm", "Clear all filenames from the list?"):
            self.csv_filenames = []
            self.csv_update_listbox()
            self.csv_status_label.config(text="List cleared", fg="orange")
    
    def csv_update_listbox(self):
        """Update the listbox with current filenames"""
        self.csv_listbox.delete(0, tk.END)
        for filename in self.csv_filenames:
            self.csv_listbox.insert(tk.END, filename)
        
        # Update counter
        self.csv_counter_label.config(text=f"Total files: {len(self.csv_filenames)}")
    
    def csv_export(self):
        """Export filenames to CSV"""
        if not self.csv_filenames:
            messagebox.showwarning("Warning", "No filenames to export. Please select files first.")
            return
        
        # Ask where to save CSV
        csv_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="filenames.csv"
        )
        
        if not csv_path:
            return
        
        try:
            # Write to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Filename'])
                # Write filenames
                for filename in self.csv_filenames:
                    writer.writerow([filename])
            
            file_size = os.path.getsize(csv_path) / 1024
            self.csv_status_label.config(
                text=f"✓ CSV exported successfully ({file_size:.1f} KB)",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"CSV file created successfully!\n\n"
                f"Location: {csv_path}\n"
                f"Filenames: {len(self.csv_filenames)}\n"
                f"Size: {file_size:.1f} KB"
            )
        except Exception as e:
            self.csv_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")
    
    # ==================== TEXT FORMATTING METHODS ====================
    
    def text_format_clear_input(self):
        """Clear the input text area"""
        if messagebox.askyesno("Confirm", "Clear all input text?"):
            self.text_format_input.delete(1.0, tk.END)
            self.text_format_status_label.config(text="Input cleared", fg="orange")
    
    def text_format_format(self):
        """Format the input text by combining with separator"""
        try:
            # Get input text
            input_text = self.text_format_input.get(1.0, tk.END).strip()
            
            if not input_text:
                messagebox.showwarning("Warning", "Please paste or type links first")
                return
            
            # Get separator
            separator = self.text_format_sep_var.get()
            
            # Split by newlines and filter empty lines
            lines = [line.strip() for line in input_text.split('\n') if line.strip()]
            
            # Join with separator
            formatted_text = f" {separator} ".join(lines)
            
            # Display output
            self.text_format_output.config(state=tk.NORMAL)
            self.text_format_output.delete(1.0, tk.END)
            self.text_format_output.insert(1.0, formatted_text)
            self.text_format_output.config(state=tk.DISABLED)
            
            # Update status
            self.text_format_status_label.config(
                text=f"✓ Formatted {len(lines)} items with separator: '{separator}'",
                fg="green"
            )
            
        except Exception as e:
            self.text_format_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to format text:\n{str(e)}")
    
    def text_format_copy(self):
        """Copy formatted output to clipboard"""
        try:
            output_text = self.text_format_output.get(1.0, tk.END).strip()
            
            if not output_text:
                messagebox.showwarning("Warning", "No formatted output to copy. Click 'Format Text' first.")
                return
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(output_text)
            self.root.update()
            
            self.text_format_status_label.config(
                text="✓ Formatted text copied to clipboard",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"Text copied to clipboard!\n\n"
                f"Items: {output_text.count(self.text_format_sep_var.get()) + 1}\n"
                f"Length: {len(output_text)} characters"
            )
        except Exception as e:
            self.text_format_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")
    
    def text_format_save(self):
        """Save formatted text to a file"""
        try:
            output_text = self.text_format_output.get(1.0, tk.END).strip()
            
            if not output_text:
                messagebox.showwarning("Warning", "No formatted output to save. Click 'Format Text' first.")
                return
            
            # Ask where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialfile="formatted_text.txt"
            )
            
            if not save_path:
                return
            
            # Save to file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            
            file_size = os.path.getsize(save_path) / 1024
            self.text_format_status_label.config(
                text=f"✓ Text saved successfully ({file_size:.1f} KB)",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"Text file saved successfully!\n\n"
                f"Location: {save_path}\n"
                f"Items: {output_text.count(self.text_format_sep_var.get()) + 1}\n"
                f"Size: {file_size:.1f} KB"
            )
        except Exception as e:
            self.text_format_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to save text file:\n{str(e)}")
    
    # ==================== SMART RENAMER TAB ====================
    
    def setup_renamer_ui(self):
        """Set up the Smart Renamer UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.renamer_frame)
        scrollbar = tk.Scrollbar(self.renamer_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Smart Renamer",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Select multiple files and rename by replacing characters\n(Tip: Use 'Space' keyword for whitespace)",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Settings Frame
        settings_frame = tk.LabelFrame(
            scrollable_frame,
            text="Rename Settings",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        settings_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Target character input
        target_frame = tk.Frame(settings_frame)
        target_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(
            target_frame,
            text="Target Character:",
            font=("Arial", 10),
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.renamer_target_entry = tk.Entry(
            target_frame,
            font=("Arial", 10),
            width=30
        )
        self.renamer_target_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            target_frame,
            text="(e.g., '_' or 'Space' for whitespace)",
            font=("Arial", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)
        
        # Replacement character input
        replace_frame = tk.Frame(settings_frame)
        replace_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(
            replace_frame,
            text="Replace With:",
            font=("Arial", 10),
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.renamer_replace_entry = tk.Entry(
            replace_frame,
            font=("Arial", 10),
            width=30
        )
        self.renamer_replace_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            replace_frame,
            text="(leave empty to remove character)",
            font=("Arial", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons Frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=15)
        
        select_files_button = tk.Button(
            button_frame,
            text="Select Files",
            command=self.renamer_select_files,
            width=15,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_files_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(
            button_frame,
            text="Clear List",
            command=self.renamer_clear_list,
            width=15,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        rename_button = tk.Button(
            button_frame,
            text="Rename Files",
            command=self.renamer_rename_files,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        rename_button.pack(side=tk.LEFT, padx=5)
        
        # File list frame
        list_frame = tk.LabelFrame(
            scrollable_frame,
            text="Selected Files",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollbar for listbox
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox to display files
        self.renamer_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 9),
            yscrollcommand=list_scrollbar.set,
            height=15,
            selectmode=tk.EXTENDED
        )
        self.renamer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.config(command=self.renamer_listbox.yview)
        
        # Status label
        self.renamer_status_label = tk.Label(
            scrollable_frame,
            text="No files selected",
            font=("Arial", 10),
            fg="gray"
        )
        self.renamer_status_label.pack(pady=10)
        
        # Store selected file paths
        self.renamer_file_paths = []
    
    def renamer_select_files(self):
        """Select multiple files for renaming"""
        file_paths = filedialog.askopenfilenames(
            title="Select Files to Rename",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_paths:
            self.renamer_file_paths = list(file_paths)
            self.renamer_listbox.delete(0, tk.END)
            
            for file_path in self.renamer_file_paths:
                filename = os.path.basename(file_path)
                self.renamer_listbox.insert(tk.END, filename)
            
            self.renamer_status_label.config(
                text=f"{len(self.renamer_file_paths)} file(s) selected",
                fg="blue"
            )
    
    def renamer_clear_list(self):
        """Clear the file list"""
        self.renamer_file_paths = []
        self.renamer_listbox.delete(0, tk.END)
        self.renamer_status_label.config(text="No files selected", fg="gray")
    
    def renamer_rename_files(self):
        """Rename selected files based on target and replacement characters"""
        if not self.renamer_file_paths:
            messagebox.showwarning("No Files", "Please select files to rename.")
            return
        
        target = self.renamer_target_entry.get()
        replacement = self.renamer_replace_entry.get()
        
        if not target:
            messagebox.showwarning("No Target", "Please enter a target character to replace.")
            return
        
        # Handle 'Space' keyword for whitespace
        if target.lower() == "space":
            target = " "
        if replacement.lower() == "space":
            replacement = " "
        
        # Confirm action
        confirm = messagebox.askyesno(
            "Confirm Rename",
            f"Are you sure you want to rename {len(self.renamer_file_paths)} file(s)?\n\n"
            f"Target: '{target}'\n"
            f"Replace with: '{replacement}'"
        )
        
        if not confirm:
            return
        
        renamed_count = 0
        error_count = 0
        error_details = []
        
        for file_path in self.renamer_file_paths:
            try:
                directory = os.path.dirname(file_path)
                old_filename = os.path.basename(file_path)
                
                # Split filename and extension
                name_without_ext, ext = os.path.splitext(old_filename)
                
                # Replace target character in filename (not extension)
                new_name = name_without_ext.replace(target, replacement)
                new_filename = new_name + ext
                
                # Skip if no change
                if new_filename == old_filename:
                    continue
                
                new_file_path = os.path.join(directory, new_filename)
                
                # Check if target file already exists
                if os.path.exists(new_file_path):
                    error_details.append(f"{old_filename} → {new_filename} (already exists)")
                    error_count += 1
                    continue
                
                # Rename the file
                os.rename(file_path, new_file_path)
                renamed_count += 1
                
            except Exception as e:
                error_details.append(f"{old_filename}: {str(e)}")
                error_count += 1
        
        # Show results
        result_message = f"Rename completed!\n\n"
        result_message += f"✓ Successfully renamed: {renamed_count}\n"
        
        if error_count > 0:
            result_message += f"✗ Errors: {error_count}\n\n"
            result_message += "Error details:\n" + "\n".join(error_details[:10])
            if len(error_details) > 10:
                result_message += f"\n... and {len(error_details) - 10} more errors"
        
        if renamed_count > 0 or error_count > 0:
            if error_count > 0:
                messagebox.showwarning("Rename Complete with Errors", result_message)
            else:
                messagebox.showinfo("Success", result_message)
            
            # Update status
            self.renamer_status_label.config(
                text=f"Renamed {renamed_count} file(s), {error_count} error(s)",
                fg="green" if error_count == 0 else "orange"
            )
            
            # Clear the list after renaming
            self.renamer_clear_list()
        else:
            messagebox.showinfo("No Changes", "No files were renamed (no changes needed).")

    # ==================== LIST RENAMER TAB ====================

    def setup_list_renamer_ui(self):
        """Set up the List Renamer UI"""
        main_canvas = tk.Canvas(self.list_renamer_frame)
        scrollbar = tk.Scrollbar(self.list_renamer_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title_label = tk.Label(scrollable_frame, text="List Renamer", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        info_label = tk.Label(
            scrollable_frame,
            text="Select a batch of images, edit new filenames on the right, and apply all renames at once",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)

        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=10)

        select_button = tk.Button(
            button_frame,
            text="Select Images",
            command=self.list_renamer_select_files,
            width=15,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            button_frame,
            text="Clear List",
            command=self.list_renamer_clear_list,
            width=15,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        apply_button = tk.Button(
            button_frame,
            text="Apply Renames",
            command=self.list_renamer_apply_changes,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        apply_button.pack(side=tk.LEFT, padx=5)

        content_frame = tk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left column: file listing
        list_frame = tk.LabelFrame(content_frame, text="Queued Files", font=("Arial", 10, "bold"))
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scrollbar = tk.Scrollbar(list_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_renamer_tree = ttk.Treeview(
            list_frame,
            columns=("original", "new"),
            show="headings",
            height=15,
            selectmode="browse"
        )
        self.list_renamer_tree.heading("original", text="Current Filename")
        self.list_renamer_tree.heading("new", text="New Filename")
        self.list_renamer_tree.column("original", width=250, anchor="w")
        self.list_renamer_tree.column("new", width=250, anchor="w")
        self.list_renamer_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.list_renamer_tree.config(yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=self.list_renamer_tree.yview)
        self.list_renamer_tree.bind("<<TreeviewSelect>>", self.list_renamer_on_select)

        # Right column: details/editor
        detail_frame = tk.LabelFrame(content_frame, text="Rename Details", font=("Arial", 10, "bold"))
        detail_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(10, 0))

        self.list_renamer_selected_label = tk.Label(
            detail_frame,
            text="Select a file to edit",
            font=("Arial", 10, "bold"),
            fg="#3F51B5"
        )
        self.list_renamer_selected_label.pack(pady=5)

        self.list_renamer_path_label = tk.Label(
            detail_frame,
            text="Path: -",
            font=("Arial", 8),
            wraplength=250,
            justify=tk.LEFT
        )
        self.list_renamer_path_label.pack(padx=5, pady=5, anchor="w")

        self.list_renamer_extension_label = tk.Label(
            detail_frame,
            text="Extension: -",
            font=("Arial", 9)
        )
        self.list_renamer_extension_label.pack(padx=5, pady=5, anchor="w")

        entry_frame = tk.Frame(detail_frame)
        entry_frame.pack(padx=5, pady=10, fill=tk.X)

        tk.Label(entry_frame, text="New filename (without extension):", font=("Arial", 9)).pack(anchor="w")

        self.list_renamer_new_name_var = tk.StringVar(value="")
        self.list_renamer_new_name_entry = tk.Entry(entry_frame, textvariable=self.list_renamer_new_name_var, font=("Arial", 10))
        self.list_renamer_new_name_entry.pack(fill=tk.X, pady=5)

        hint_label = tk.Label(
            entry_frame,
            text="Avoid characters: / \\ : * ? \" < > |",
            font=("Arial", 8),
            fg="gray"
        )
        hint_label.pack(anchor="w")

        preview_frame = tk.LabelFrame(
            detail_frame,
            text="Preview",
            font=("Arial", 10, "bold"),
            padx=5,
            pady=5
        )
        preview_frame.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)

        self.list_renamer_preview_label = tk.Label(
            preview_frame,
            text="No preview",
            font=("Arial", 9),
            bg="#FAFAFA",
            relief=tk.SUNKEN,
            anchor=tk.CENTER
        )
        self.list_renamer_preview_label.pack(fill=tk.BOTH, expand=True)

        save_name_button = tk.Button(
            detail_frame,
            text="Save Name",
            command=self.list_renamer_save_name,
            width=15,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold")
        )
        save_name_button.pack(pady=5)

        self.list_renamer_counter_label = tk.Label(detail_frame, text="Total files: 0", font=("Arial", 9))
        self.list_renamer_counter_label.pack(pady=5)

        self.list_renamer_status_label = tk.Label(
            scrollable_frame,
            text="Ready - select images to begin",
            font=("Arial", 9),
            fg="green"
        )
        self.list_renamer_status_label.pack(pady=10)

    def list_renamer_select_files(self):
        """Add files to the list renamer queue"""
        file_paths = filedialog.askopenfilenames(
            title="Select images to rename",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )

        if not file_paths:
            return

        added = 0
        for file_path in file_paths:
            normalized = os.path.normpath(file_path)
            if not os.path.isfile(normalized):
                continue
            if any(existing["path"].lower() == normalized.lower() for existing in self.list_renamer_files):
                continue

            directory = os.path.dirname(normalized)
            original = os.path.basename(normalized)
            stem, ext = os.path.splitext(original)

            self.list_renamer_files.append({
                "path": normalized,
                "directory": directory,
                "original": original,
                "ext": ext,
                "new_name": stem
            })
            added += 1

        if added == 0:
            self.list_renamer_status_label.config(text="No new files were added", fg="orange")
            return

        self.list_renamer_update_tree()
        self.list_renamer_status_label.config(text=f"Added {added} file(s)", fg="blue")

    def list_renamer_update_tree(self, selected_index=None):
        """Refresh the treeview with current file data"""
        for item in self.list_renamer_tree.get_children():
            self.list_renamer_tree.delete(item)

        for index, info in enumerate(self.list_renamer_files):
            self.list_renamer_tree.insert("", tk.END, iid=str(index), values=(info["original"], f"{info['new_name']}{info['ext']}"))

        self.list_renamer_counter_label.config(text=f"Total files: {len(self.list_renamer_files)}")
        if selected_index is not None and 0 <= selected_index < len(self.list_renamer_files):
            self.list_renamer_tree.selection_set(str(selected_index))
            self.list_renamer_tree.focus(str(selected_index))
            self.list_renamer_selected_index = selected_index
            info = self.list_renamer_files[selected_index]
            self.list_renamer_new_name_var.set(info["new_name"])
            self.list_renamer_selected_label.config(text=f"Editing: {info['original']}")
            self.list_renamer_path_label.config(text=f"Path: {info['path']}")
            self.list_renamer_extension_label.config(text=f"Extension: {info['ext']} (kept)")
            self.list_renamer_show_preview(info["path"])
        else:
            self.list_renamer_selected_index = None
            self.list_renamer_new_name_var.set("")
            self.list_renamer_selected_label.config(text="Select a file to edit")
            self.list_renamer_path_label.config(text="Path: -")
            self.list_renamer_extension_label.config(text="Extension: -")
            self.list_renamer_clear_preview()

    def list_renamer_on_select(self, event):
        """Populate detail panel when a tree row is selected"""
        selection = self.list_renamer_tree.selection()
        if not selection:
            return

        index = int(selection[0])
        if index < 0 or index >= len(self.list_renamer_files):
            return

        info = self.list_renamer_files[index]
        self.list_renamer_selected_index = index
        self.list_renamer_new_name_var.set(info["new_name"])
        self.list_renamer_selected_label.config(text=f"Editing: {info['original']}")
        self.list_renamer_path_label.config(text=f"Path: {info['path']}")
        self.list_renamer_extension_label.config(text=f"Extension: {info['ext']} (kept)")
        self.list_renamer_show_preview(info["path"])

    def list_renamer_show_preview(self, file_path):
        """Display a preview thumbnail for the selected image"""
        if not os.path.exists(file_path):
            self.list_renamer_clear_preview("File missing")
            return
        try:
            with Image.open(file_path) as img:
                img = img.convert('RGBA')
                max_size = 280
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                canvas = Image.new('RGBA', (max_size, max_size), (255, 255, 255, 0))
                x_offset = (max_size - img.width) // 2
                y_offset = (max_size - img.height) // 2
                canvas.paste(img, (x_offset, y_offset), img)
                display_image = canvas.convert('RGB')
                import io
                with io.BytesIO() as output:
                    display_image.save(output, format="PPM")
                    data = output.getvalue()
            photo = tk.PhotoImage(data=data)
            self.list_renamer_preview_label.config(image=photo, text="")
            self.list_renamer_preview_image = photo
        except Exception as e:
            self.list_renamer_clear_preview("Preview unavailable")
            self.list_renamer_status_label.config(text=f"Preview error: {str(e)}", fg="red")

    def list_renamer_clear_preview(self, message="No preview"):
        """Clear preview image and show placeholder text"""
        self.list_renamer_preview_label.config(image="", text=message)
        self.list_renamer_preview_image = None

    def list_renamer_save_name(self):
        """Save edited name for the currently selected item"""
        if self.list_renamer_selected_index is None:
            messagebox.showwarning("No Selection", "Please select a file to edit.")
            return

        new_name = self.list_renamer_new_name_var.get().strip()
        if not new_name:
            messagebox.showwarning("Invalid Name", "New filename cannot be empty.")
            return

        invalid_chars = set('/\\:*?"<>|')
        if any(char in invalid_chars for char in new_name):
            messagebox.showwarning("Invalid Characters", "Please remove any invalid filename characters.")
            return

        info = self.list_renamer_files[self.list_renamer_selected_index]
        info["new_name"] = new_name
        current_index = self.list_renamer_selected_index
        self.list_renamer_update_tree(selected_index=current_index)
        self.list_renamer_status_label.config(text=f"Updated name for {info['original']}", fg="blue")

    def list_renamer_clear_list(self):
        """Clear all queued files"""
        if not self.list_renamer_files:
            return
        if not messagebox.askyesno("Confirm", "Clear all files from the list?"):
            return
        self.list_renamer_files = []
        self.list_renamer_update_tree()
        self.list_renamer_status_label.config(text="List cleared", fg="orange")

    def list_renamer_apply_changes(self):
        """Apply the pending renames to disk"""
        if not self.list_renamer_files:
            messagebox.showwarning("No Files", "Please add files before applying renames.")
            return

        invalid_chars = set('/\\:*?"<>|')
        planned_paths = {}
        rename_plan = []

        for info in self.list_renamer_files:
            new_base = info["new_name"].strip()
            if not new_base:
                messagebox.showwarning("Invalid Name", f"Filename cannot be empty for {info['original']}.")
                return
            if any(char in invalid_chars for char in new_base):
                messagebox.showwarning("Invalid Characters", f"Remove invalid characters from the new name for {info['original']}.")
                return

            target_filename = f"{new_base}{info['ext']}"
            target_path = os.path.join(info["directory"], target_filename)
            key = (info["directory"].lower(), target_filename.lower())

            if key in planned_paths and planned_paths[key] != info["path"].lower():
                messagebox.showwarning(
                    "Duplicate Names",
                    f"Multiple files are set to become '{target_filename}' in {info['directory']}"
                )
                return

            planned_paths[key] = info["path"].lower()
            rename_plan.append((info, target_path, target_filename))

        renamed = 0
        skipped = 0
        errors = []

        for info, target_path, target_filename in rename_plan:
            current_path = info["path"]
            if os.path.normcase(current_path) == os.path.normcase(target_path):
                skipped += 1
                continue

            if os.path.exists(target_path):
                errors.append(f"{target_filename} already exists")
                continue

            try:
                os.rename(current_path, target_path)
                info["path"] = target_path
                info["original"] = target_filename
                info["new_name"] = os.path.splitext(target_filename)[0]
                renamed += 1
            except Exception as ex:
                errors.append(f"{info['original']}: {str(ex)}")

        self.list_renamer_update_tree()

        summary = f"Renamed: {renamed}\nUnchanged: {skipped}\nErrors: {len(errors)}"
        if errors:
            summary += "\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                summary += f"\n... and {len(errors) - 10} more"

        if renamed > 0 and not errors:
            messagebox.showinfo("Rename Complete", summary)
            self.list_renamer_status_label.config(text=f"✓ Renamed {renamed} file(s)", fg="green")
        elif renamed > 0 and errors:
            messagebox.showwarning("Partial Success", summary)
            self.list_renamer_status_label.config(text=f"Renamed {renamed} file(s) with {len(errors)} error(s)", fg="orange")
        elif errors:
            messagebox.showerror("No Files Renamed", summary)
            self.list_renamer_status_label.config(text="No files were renamed", fg="red")
        else:
            messagebox.showinfo("No Changes", "All files already had the desired names.")
            self.list_renamer_status_label.config(text="No renames were needed", fg="blue")

    def select_sorter_source_folder(self):
        """Select the source folder containing images to sort"""
        folder_path = filedialog.askdirectory(title="Select Folder with Images to Sort")
        if folder_path:
            self.sorter_source_folder = folder_path
            self.sorter_folder_label.config(text=folder_path, fg="black")
            self.sorter_status_label.config(text="Folder selected. Click 'Analyze Images' to continue.", fg="blue")
            self.sorter_results_text.delete(1.0, tk.END)
            self.sorter_results_text.insert(tk.END, f"Selected folder: {folder_path}\n")
            self.sorter_results_text.insert(tk.END, "Click 'Analyze Images' to find similar image groups.\n")

    def calculate_image_hash(self, image_path, hash_size=8):
        """Calculate perceptual hash of an image for similarity comparison"""
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale and resize
                img = img.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
                # Calculate average pixel value
                pixels = list(img.getdata())
                avg = sum(pixels) / len(pixels)
                # Create hash string
                hash_string = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
                return hash_string
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

    def calculate_color_hash(self, image_path, hash_size=8):
        """Calculate color-based perceptual hash for better color similarity detection"""
        try:
            with Image.open(image_path) as img:
                # Resize and convert to RGB
                img = img.resize((hash_size, hash_size), Image.Resampling.LANCZOS).convert('RGB')
                
                # Calculate separate hashes for each color channel
                pixels = list(img.getdata())
                r_pixels = [pixel[0] for pixel in pixels]
                g_pixels = [pixel[1] for pixel in pixels]
                b_pixels = [pixel[2] for pixel in pixels]
                
                # Calculate averages for each channel
                r_avg = sum(r_pixels) / len(r_pixels)
                g_avg = sum(g_pixels) / len(g_pixels)
                b_avg = sum(b_pixels) / len(b_pixels)
                
                # Create hash strings for each channel
                r_hash = ''.join(['1' if pixel > r_avg else '0' for pixel in r_pixels])
                g_hash = ''.join(['1' if pixel > g_avg else '0' for pixel in g_pixels])
                b_hash = ''.join(['1' if pixel > b_avg else '0' for pixel in b_pixels])
                
                # Combine all three color hashes
                return r_hash + g_hash + b_hash
        except Exception as e:
            print(f"Error calculating color hash for {image_path}: {e}")
            return None

    def calculate_multi_scale_hash(self, image_path, scales=[8, 16, 32]):
        """Calculate hashes at multiple scales for better detection of similar images at different sizes"""
        try:
            with Image.open(image_path) as img:
                multi_scale_hash = ""
                
                for scale in scales:
                    # Resize to current scale
                    scaled_img = img.resize((scale, scale), Image.Resampling.LANCZOS).convert('L')
                    pixels = list(scaled_img.getdata())
                    avg = sum(pixels) / len(pixels)
                    
                    # Create hash for this scale
                    scale_hash = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
                    multi_scale_hash += scale_hash
                
                return multi_scale_hash
        except Exception as e:
            print(f"Error calculating multi-scale hash for {image_path}: {e}")
            return None

    def calculate_file_hash(self, image_path, algorithm='md5'):
        """Calculate file hash for exact duplicate detection"""
        try:
            import hashlib
            hash_func = getattr(hashlib, algorithm)
            
            with open(image_path, 'rb') as f:
                file_hash = hash_func()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash for {image_path}: {e}")
            return None

    def extract_exif_data(self, image_path):
        """Extract EXIF data for metadata-based similarity"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    # Extract key EXIF fields that might indicate similarity
                    exif_info = {
                        'camera_make': exif_data.get(271, ''),  # Make
                        'camera_model': exif_data.get(272, ''),  # Model
                        'datetime': exif_data.get(36867, ''),   # DateTimeOriginal
                        'iso': exif_data.get(34855, ''),        # ISOSpeedRatings
                        'focal_length': exif_data.get(37386, ''), # FocalLength
                        'aperture': exif_data.get(33437, ''),    # FNumber
                    }
                    return exif_info
                return None
        except Exception as e:
            print(f"Error extracting EXIF data from {image_path}: {e}")
            return None

    def hamming_distance(self, hash1, hash2):
        """Calculate Hamming distance between two hash strings"""
        if len(hash1) != len(hash2):
            return float('inf')
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    def calculate_orb_features(self, image_path, max_features=500):
        """Calculate ORB features for feature-based similarity detection"""
        try:
            import cv2
            import numpy as np
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create ORB detector
            orb = cv2.ORB_create(nfeatures=max_features)
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            return {
                'keypoints': len(keypoints),
                'descriptors': descriptors
            }
        except ImportError:
            print("OpenCV not available. Install with: pip install opencv-python")
            return None
        except Exception as e:
            print(f"Error calculating ORB features for {image_path}: {e}")
            return None
    
    def calculate_ml_features(self, image_path, model_name='mobilenet'):
        """Calculate machine learning features using pre-trained models"""
        try:
            import tensorflow as tf
            from tensorflow.keras.applications import MobileNetV2, ResNet50
            from tensorflow.keras.preprocessing import image
            from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
            import numpy as np
            
            # Load pre-trained model
            if model_name == 'mobilenet':
                model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
                target_size = (224, 224)
            elif model_name == 'resnet':
                model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
                target_size = (224, 224)
            else:
                return None
            
            # Load and preprocess image
            img = image.load_img(image_path, target_size=target_size)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            # Extract features
            features = model.predict(img_array, verbose=0)
            
            return {
                'features': features.flatten(),
                'model_name': model_name
            }
            
        except ImportError:
            print("TensorFlow not available. Install with: pip install tensorflow")
            return None
        except Exception as e:
            print(f"Error calculating ML features for {image_path}: {e}")
            return None
    
    def calculate_ml_similarity(self, ml_features1, ml_features2):
        """Calculate similarity between two sets of ML features"""
        try:
            import numpy as np
            from scipy.spatial.distance import cosine
            
            if not ml_features1 or not ml_features2:
                return 0.0
            
            if ml_features1['model_name'] != ml_features2['model_name']:
                return 0.0
            
            # Calculate cosine similarity
            features1 = ml_features1['features']
            features2 = ml_features2['features']
            
            # Cosine similarity: 1 - cosine distance
            cosine_dist = cosine(features1, features2)
            similarity = 1.0 - cosine_dist
            
            return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1
            
        except ImportError:
            return 0.0
        except Exception as e:
            print(f"Error calculating ML similarity: {e}")
            return 0.0
    
    def calculate_orb_similarity(self, features1, features2):
        """Calculate similarity between two sets of ORB features"""
        try:
            import cv2
            import numpy as np
            
            if not features1 or not features2:
                return 0.0
            
            if features1['descriptors'] is None or features2['descriptors'] is None:
                return 0.0
            
            # Create BFMatcher object
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            
            # Match descriptors
            matches = bf.match(features1['descriptors'], features2['descriptors'])
            
            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Calculate similarity score based on good matches
            good_matches = [m for m in matches if m.distance < 50]  # Lower distance = better match
            
            if len(matches) == 0:
                return 0.0
            
            similarity = len(good_matches) / len(matches)
            return similarity
            
        except ImportError:
            return 0.0
        except Exception as e:
            print(f"Error calculating ORB similarity: {e}")
            return 0.0
    
    def calculate_combined_similarity_score(self, image_path1, image_path2, weights=None):
        """Calculate a combined similarity score using multiple detection methods"""
        if weights is None:
            weights = {
                'grayscale_hash': 0.20,
                'color_hash': 0.20,
                'multi_scale_hash': 0.15,
                'file_hash': 0.15,
                'exif_similarity': 0.10,
                'orb_similarity': 0.20
            }
        
        total_score = 0.0
        max_possible_score = 0.0
        
        try:
            # 1. Grayscale perceptual hash
            if weights['grayscale_hash'] > 0:
                hash1 = self.calculate_image_hash(image_path1)
                hash2 = self.calculate_image_hash(image_path2)
                if hash1 and hash2:
                    distance = self.hamming_distance(hash1, hash2)
                    similarity = 1.0 - (distance / len(hash1))
                    total_score += similarity * weights['grayscale_hash']
                max_possible_score += weights['grayscale_hash']
            
            # 2. Color-based hash
            if weights['color_hash'] > 0:
                color_hash1 = self.calculate_color_hash(image_path1)
                color_hash2 = self.calculate_color_hash(image_path2)
                if color_hash1 and color_hash2:
                    color_distance = self.hamming_distance(color_hash1, color_hash2)
                    color_similarity = 1.0 - (color_distance / len(color_hash1))
                    total_score += color_similarity * weights['color_hash']
                max_possible_score += weights['color_hash']
            
            # 3. Multi-scale hash
            if weights['multi_scale_hash'] > 0:
                multi_hash1 = self.calculate_multi_scale_hash(image_path1)
                multi_hash2 = self.calculate_multi_scale_hash(image_path2)
                if multi_hash1 and multi_hash2:
                    multi_distance = self.hamming_distance(multi_hash1, multi_hash2)
                    multi_similarity = 1.0 - (multi_distance / len(multi_hash1))
                    total_score += multi_similarity * weights['multi_scale_hash']
                max_possible_score += weights['multi_scale_hash']
            
            # 4. File hash (exact duplicates)
            if weights['file_hash'] > 0:
                file_hash1 = self.calculate_file_hash(image_path1)
                file_hash2 = self.calculate_file_hash(image_path2)
                if file_hash1 and file_hash2:
                    file_similarity = 1.0 if file_hash1 == file_hash2 else 0.0
                    total_score += file_similarity * weights['file_hash']
                max_possible_score += weights['file_hash']
            
            # 5. EXIF similarity
            if weights['exif_similarity'] > 0:
                exif1 = self.extract_exif_data(image_path1)
                exif2 = self.extract_exif_data(image_path2)
                if exif1 and exif2:
                    exif_similarity = self.calculate_exif_similarity(exif1, exif2)
                    total_score += exif_similarity * weights['exif_similarity']
                max_possible_score += weights['exif_similarity']
            
            # 6. ORB feature similarity
            if weights['orb_similarity'] > 0:
                orb_features1 = self.calculate_orb_features(image_path1)
                orb_features2 = self.calculate_orb_features(image_path2)
                if orb_features1 and orb_features2:
                    orb_similarity = self.calculate_orb_similarity(orb_features1, orb_features2)
                    total_score += orb_similarity * weights['orb_similarity']
                max_possible_score += weights['orb_similarity']
            
            # Normalize score
            return total_score / max_possible_score if max_possible_score > 0 else 0.0
            
        except Exception as e:
            print(f"Error calculating combined similarity: {e}")
            return 0.0
    
    def calculate_exif_similarity(self, exif1, exif2):
        """Calculate similarity between two EXIF data dictionaries"""
        try:
            similarity_score = 0.0
            total_fields = 0
            
            # Compare camera make and model
            if exif1.get('camera_make') and exif2.get('camera_make'):
                total_fields += 1
                if exif1['camera_make'] == exif2['camera_make']:
                    similarity_score += 1.0
            
            if exif1.get('camera_model') and exif2.get('camera_model'):
                total_fields += 1
                if exif1['camera_model'] == exif2['camera_model']:
                    similarity_score += 1.0
            
            # Compare datetime (same day = similar)
            if exif1.get('datetime') and exif2.get('datetime'):
                total_fields += 1
                date1 = exif1['datetime'][:10]  # Extract date part
                date2 = exif2['datetime'][:10]
                if date1 == date2:
                    similarity_score += 1.0
            
            # Compare ISO
            if exif1.get('iso') and exif2.get('iso'):
                total_fields += 1
                iso1 = exif1['iso']
                iso2 = exif2['iso']
                if iso1 == iso2:
                    similarity_score += 1.0
            
            return similarity_score / total_fields if total_fields > 0 else 0.0
            
        except Exception as e:
            print(f"Error calculating EXIF similarity: {e}")
            return 0.0

    def analyze_images_for_sorting(self):
        """Analyze images in the source folder and group similar ones"""
        if not self.sorter_source_folder:
            messagebox.showwarning("Warning", "Please select a source folder first")
            return
        
        try:
            self.sorter_status_label.config(text="Analyzing images...", fg="orange")
            self.root.update()
            
            # Get all image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
            image_files = []
            
            for file in os.listdir(self.sorter_source_folder):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(self.sorter_source_folder, file))
            
            if not image_files:
                messagebox.showwarning("Warning", "No image files found in the selected folder")
                self.sorter_status_label.config(text="No images found", fg="red")
                return
            
            total_images = len(image_files)
            self.sorter_results_text.delete(1.0, tk.END)
            self.sorter_results_text.insert(tk.END, f"Found {total_images} images to analyze...\n")
            
            # Calculate hashes for all images based on selected detection method
            image_hashes = {}
            for i, image_path in enumerate(image_files):
                self.sorter_progress_var.set((i / total_images) * 50)  # First 50% for hashing
                self.root.update()
                
                detection_method = self.sorter_detection_method.get()
                hash_value = None
                
                if detection_method == "basic":
                    hash_value = self.calculate_image_hash(image_path)
                elif detection_method == "color":
                    hash_value = self.calculate_color_hash(image_path)
                elif detection_method == "multi_scale":
                    hash_value = self.calculate_multi_scale_hash(image_path)
                elif detection_method == "combined":
                    # For combined method, we'll store multiple hash types
                    hash_value = {
                        'basic': self.calculate_image_hash(image_path),
                        'color': self.calculate_color_hash(image_path),
                        'multi_scale': self.calculate_multi_scale_hash(image_path),
                        'file_hash': self.calculate_file_hash(image_path),
                        'exif': self.extract_exif_data(image_path)
                    }
                elif detection_method == "exact_duplicate":
                    hash_value = self.calculate_file_hash(image_path)
                elif detection_method == "orb_features":
                    hash_value = self.calculate_orb_features(image_path)
                elif detection_method == "ml_features":
                    hash_value = self.calculate_ml_features(image_path)
                
                if hash_value:
                    image_hashes[image_path] = hash_value
            
            # Group similar images based on selected detection method
            groups = []
            processed = set()
            detection_method = self.sorter_detection_method.get()
            
            # Set appropriate threshold based on detection method
            if detection_method == "basic":
                threshold = int((1 - self.sorter_similarity_threshold.get()) * 64)  # 64 bits in 8x8 hash
            elif detection_method == "color":
                threshold = int((1 - self.sorter_similarity_threshold.get()) * 192)  # 192 bits in color hash (8x8x3)
            elif detection_method == "multi_scale":
                threshold = int((1 - self.sorter_similarity_threshold.get()) * 896)  # 896 bits total (64+256+576)
            elif detection_method == "combined":
                threshold = self.sorter_similarity_threshold.get()  # Use percentage threshold for combined
            elif detection_method == "exact_duplicate":
                threshold = 0  # Exact match required for duplicates
            elif detection_method == "orb_features":
                threshold = 0.3  # ORB similarity threshold (0.0 to 1.0)
            elif detection_method == "ml_features":
                threshold = 0.8  # ML similarity threshold (0.0 to 1.0)
            
            for image_path, hash_value in image_hashes.items():
                if image_path in processed:
                    continue
                
                current_group = [image_path]
                processed.add(image_path)
                
                # Find similar images
                for other_path, other_hash in image_hashes.items():
                    if other_path in processed:
                        continue
                    
                    if detection_method == "combined":
                        # Use combined similarity score
                        similarity = self.calculate_combined_similarity_score(image_path, other_path)
                        if similarity >= threshold:
                            current_group.append(other_path)
                            processed.add(other_path)
                    elif detection_method == "exact_duplicate":
                        # Check for exact file hash match
                        if hash_value == other_hash:
                            current_group.append(other_path)
                            processed.add(other_path)
                    elif detection_method == "orb_features":
                        # Use ORB similarity for feature-based matching
                        orb_similarity = self.calculate_orb_similarity(hash_value, other_hash)
                        if orb_similarity >= threshold:
                            current_group.append(other_path)
                            processed.add(other_path)
                    elif detection_method == "ml_features":
                        # Use ML similarity for machine learning-based matching
                        ml_similarity = self.calculate_ml_similarity(hash_value, other_hash)
                        if ml_similarity >= threshold:
                            current_group.append(other_path)
                            processed.add(other_path)
                    else:
                        # Use hamming distance for other methods
                        distance = self.hamming_distance(hash_value, other_hash)
                        if distance <= threshold:
                            current_group.append(other_path)
                            processed.add(other_path)
                
                # Only add groups that meet minimum size requirement
                if len(current_group) >= self.sorter_min_group_size.get():
                    groups.append(current_group)
            
            # Store results
            self.sorter_image_groups = groups
            
            # Update UI
            self.sorter_progress_var.set(100)
            self.sorter_status_label.config(text=f"Analysis complete! Found {len(groups)} groups", fg="green")
            
            # Display results
            self.sorter_results_text.delete(1.0, tk.END)
            self.sorter_results_text.insert(tk.END, f"Analysis Results:\n")
            self.sorter_results_text.insert(tk.END, f"Detection method: {detection_method.replace('_', ' ').title()}\n")
            self.sorter_results_text.insert(tk.END, f"Total images analyzed: {len(image_hashes)}\n")
            self.sorter_results_text.insert(tk.END, f"Similarity threshold: {self.sorter_similarity_threshold.get():.2f}\n")
            self.sorter_results_text.insert(tk.END, f"Found {len(groups)} groups with {self.sorter_min_group_size.get()}+ images:\n\n")
            
            for i, group in enumerate(groups, 1):
                self.sorter_results_text.insert(tk.END, f"Group {i} ({len(group)} images):\n")
                for image_path in group[:5]:  # Show first 5 images
                    filename = os.path.basename(image_path)
                    self.sorter_results_text.insert(tk.END, f"  - {filename}\n")
                if len(group) > 5:
                    self.sorter_results_text.insert(tk.END, f"  ... and {len(group) - 5} more\n")
                self.sorter_results_text.insert(tk.END, "\n")
            
            # Enable sort button if groups were found
            if groups:
                self.sorter_sort_button.config(state=tk.NORMAL)
            else:
                self.sorter_results_text.insert(tk.END, "No similar image groups found. Try adjusting the similarity threshold.\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze images:\n{str(e)}")
            self.sorter_status_label.config(text="Analysis failed", fg="red")

    def sort_images_into_folders(self):
        """Sort analyzed images into separate folders"""
        if not self.sorter_image_groups:
            messagebox.showwarning("Warning", "Please analyze images first")
            return
        
        try:
            self.sorter_status_label.config(text="Sorting images...", fg="orange")
            self.sorter_progress_var.set(0)
            self.root.update()
            
            total_images = sum(len(group) for group in self.sorter_image_groups)
            processed = 0
            
            for i, group in enumerate(self.sorter_image_groups, 1):
                # Create folder for this group
                group_folder_name = f"similar_group_{i}_{len(group)}_images"
                group_folder_path = os.path.join(self.sorter_source_folder, group_folder_name)
                
                os.makedirs(group_folder_path, exist_ok=True)
                
                # Move images to the group folder
                for image_path in group:
                    filename = os.path.basename(image_path)
                    destination = os.path.join(group_folder_path, filename)
                    
                    # Move the file
                    shutil.move(image_path, destination)
                    
                    processed += 1
                    self.sorter_progress_var.set((processed / total_images) * 100)
                    self.root.update()
            
            self.sorter_status_label.config(text=f"Sorting complete! Created {len(self.sorter_image_groups)} folders", fg="green")
            
            # Show summary
            summary = f"Created {len(self.sorter_image_groups)} folders\n"
            summary += f"Moved {total_images} images\n"
            summary += f"Source folder: {self.sorter_source_folder}"
            
            messagebox.showinfo("Sorting Complete", summary)
            
            # Clear results for next operation
            self.sorter_image_groups = {}
            self.sorter_sort_button.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sort images:\n{str(e)}")
            self.sorter_status_label.config(text="Sorting failed", fg="red")

    def setup_image_sorter_ui(self):
        """Set up the image sorting UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.image_sorter_frame)
        scrollbar = tk.Scrollbar(self.image_sorter_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Image Sorter - Group Similar Images",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Automatically group similar images from a folder into separate subfolders",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Source folder selection
        folder_frame = tk.LabelFrame(scrollable_frame, text="Source Folder", font=("Arial", 10, "bold"))
        folder_frame.pack(padx=10, pady=10, fill=tk.X)
        
        folder_button_frame = tk.Frame(folder_frame)
        folder_button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        select_folder_button = tk.Button(
            folder_button_frame,
            text="Select Source Folder",
            command=self.select_sorter_source_folder,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_folder_button.pack(side=tk.LEFT, padx=5)
        
        self.sorter_folder_label = tk.Label(
            folder_button_frame,
            text="No folder selected",
            font=("Arial", 9),
            fg="gray",
            wraplength=600,
            justify=tk.LEFT
        )
        self.sorter_folder_label.pack(side=tk.LEFT, padx=10)
        
        # Settings frame
        settings_frame = tk.LabelFrame(scrollable_frame, text="Sorting Settings", font=("Arial", 10, "bold"))
        settings_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Detection method selection
        detection_frame = tk.Frame(settings_frame)
        detection_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(detection_frame, text="Detection Method:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.sorter_detection_method = tk.StringVar(value="combined")
        detection_combo = ttk.Combobox(
               detection_frame,
               textvariable=self.sorter_detection_method,
               values=["basic", "color", "multi_scale", "combined", "exact_duplicate", "orb_features", "ml_features"],
               width=15,
               state="readonly"
           )
        detection_combo.pack(side=tk.LEFT, padx=5)
        
        # Method descriptions
        method_desc = {
               "basic": "Standard grayscale hashing",
               "color": "Color-aware similarity detection",
               "multi_scale": "Multi-resolution hashing",
               "combined": "All methods combined (recommended)",
               "exact_duplicate": "Byte-level duplicate detection",
               "orb_features": "Feature-based detection using ORB",
               "ml_features": "ML-based similarity using pre-trained models"
           }
        
        self.sorter_method_desc_label = tk.Label(
            detection_frame,
            text=method_desc["combined"],
            font=("Arial", 8),
            fg="gray"
        )
        self.sorter_method_desc_label.pack(side=tk.LEFT, padx=10)
        
        def update_method_desc(event):
            method = self.sorter_detection_method.get()
            self.sorter_method_desc_label.config(text=method_desc.get(method, ""))
        
        detection_combo.bind('<<ComboboxSelected>>', update_method_desc)
        
        # Similarity threshold
        threshold_frame = tk.Frame(settings_frame)
        threshold_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(threshold_frame, text="Similarity Threshold:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        threshold_scale = tk.Scale(
            threshold_frame,
            from_=0.5,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.sorter_similarity_threshold,
            length=200,
            font=("Arial", 8)
        )
        threshold_scale.pack(side=tk.LEFT, padx=5)
        
        tk.Label(threshold_frame, text="(0.5 = loose, 1.0 = exact match)", font=("Arial", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Minimum group size
        min_group_frame = tk.Frame(settings_frame)
        min_group_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(min_group_frame, text="Minimum Group Size:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        min_group_spinbox = tk.Spinbox(
            min_group_frame,
            from_=1,
            to=10,
            textvariable=self.sorter_min_group_size,
            width=5,
            font=("Arial", 9)
        )
        min_group_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(min_group_frame, text="images (groups smaller than this will be ignored)", font=("Arial", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(scrollable_frame)
        action_frame.pack(pady=20)
        
        analyze_button = tk.Button(
            action_frame,
            text="Analyze Images",
            command=self.analyze_images_for_sorting,
            width=15,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        analyze_button.pack(side=tk.LEFT, padx=10)
        
        sort_button = tk.Button(
            action_frame,
            text="Sort Images",
            command=self.sort_images_into_folders,
            width=15,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        sort_button.pack(side=tk.LEFT, padx=10)
        
        self.sorter_sort_button = sort_button
        
        # Progress frame
        progress_frame = tk.LabelFrame(scrollable_frame, text="Progress", font=("Arial", 10, "bold"))
        progress_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.sorter_progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.sorter_progress_var,
            maximum=100,
            mode='determinate'
        )
        self.sorter_progress_bar.pack(padx=10, pady=10, fill=tk.X)
        
        self.sorter_status_label = tk.Label(
            progress_frame,
            text="Ready to sort images",
            font=("Arial", 9),
            fg="gray"
        )
        self.sorter_status_label.pack(pady=5)
        
        # Results frame
        results_frame = tk.LabelFrame(scrollable_frame, text="Analysis Results", font=("Arial", 10, "bold"))
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create scrolled text widget for results
        results_text_frame = tk.Frame(results_frame)
        results_text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.sorter_results_text = tk.Text(
            results_text_frame,
            height=15,
            width=80,
            font=("Arial", 9),
            wrap=tk.WORD
        )
        
        results_scrollbar = tk.Scrollbar(results_text_frame, command=self.sorter_results_text.yview)
        self.sorter_results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.sorter_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store reference to results text widget for updates
        self.sorter_results_frame = results_frame

    def setup_high_res_ui(self):
        """Set up the high resolution image grabber UI"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.high_res_frame)
        scrollbar = tk.Scrollbar(self.high_res_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Grab High Resolution Images",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Select multiple folders and copy the highest resolution image from each folder to 'Final-Highres'",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Source folders selection
        folders_frame = tk.LabelFrame(scrollable_frame, text="Source Folders", font=("Arial", 10, "bold"))
        folders_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Add folders button
        add_folders_button = tk.Button(
            folders_frame,
            text="Add Folders",
            command=self.add_high_res_folders,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        add_folders_button.pack(pady=10)
        
        # Selected folders list
        self.high_res_folders_frame = tk.Frame(folders_frame)
        self.high_res_folders_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Output folder selection
        output_frame = tk.LabelFrame(scrollable_frame, text="Output Settings", font=("Arial", 10, "bold"))
        output_frame.pack(padx=10, pady=10, fill=tk.X)
        
        output_folder_frame = tk.Frame(output_frame)
        output_folder_frame.pack(padx=10, pady=10, fill=tk.X)
        
        tk.Label(output_folder_frame, text="Output Folder:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.high_res_output_entry = tk.Entry(output_folder_frame, font=("Arial", 10), width=30)
        self.high_res_output_entry.pack(side=tk.LEFT, padx=5)
        self.high_res_output_entry.insert(0, self.high_res_output_folder)
        
        browse_output_button = tk.Button(
            output_folder_frame,
            text="Browse",
            command=self.browse_high_res_output_folder,
            width=10
        )
        browse_output_button.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(scrollable_frame)
        action_frame.pack(padx=10, pady=20)
        
        self.high_res_start_button = tk.Button(
            action_frame,
            text="Start Grabbing",
            command=self.start_high_res_grabbing,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            state=tk.DISABLED
        )
        self.high_res_start_button.pack(side=tk.LEFT, padx=10)
        
        clear_button = tk.Button(
            action_frame,
            text="Clear Folders",
            command=self.clear_high_res_folders,
            width=15,
            height=2
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        progress_frame = tk.Frame(scrollable_frame)
        progress_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.high_res_progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.high_res_progress_var,
            maximum=100,
            length=400
        )
        self.high_res_progress_bar.pack(pady=5)
        
        # Status label
        self.high_res_status_label = tk.Label(
            progress_frame,
            text="Add folders to start",
            font=("Arial", 9),
            fg="gray"
        )
        self.high_res_status_label.pack(pady=5)
        
        # Results text area
        results_frame = tk.LabelFrame(scrollable_frame, text="Results", font=("Arial", 10, "bold"))
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.high_res_results_text = tk.Text(
            results_frame,
            height=15,
            width=80,
            font=("Arial", 9),
            wrap=tk.WORD
        )
        
        results_scrollbar = tk.Scrollbar(results_frame, command=self.high_res_results_text.yview)
        self.high_res_results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.high_res_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    def add_high_res_folders(self):
        """Add multiple folders to process with subfolder selection"""
        # First select a parent folder
        parent_folder = filedialog.askdirectory(
            title="Select Parent Folder (will scan for subfolders)",
            initialdir=os.getcwd()
        )
        
        if not parent_folder:
            return
        
        # Scan for subfolders
        subfolders = []
        try:
            for item in os.listdir(parent_folder):
                item_path = os.path.join(parent_folder, item)
                if os.path.isdir(item_path):
                    subfolders.append(item_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan folder: {str(e)}")
            return
        
        if not subfolders:
            messagebox.showinfo("Info", "No subfolders found in the selected folder.")
            # Offer to add the parent folder itself
            if messagebox.askyesno("Add Parent Folder?", "No subfolders found. Add the parent folder itself?"):
                if parent_folder not in self.high_res_source_folders:
                    self.high_res_source_folders.append(parent_folder)
                    self.add_folder_to_list(parent_folder)
                    self.update_high_res_ui()
            return
        
        # Create a selection dialog for subfolders
        self.create_subfolder_selection_dialog(subfolders)
    
    def create_subfolder_selection_dialog(self, subfolders):
        """Create a dialog for selecting subfolders with checkboxes"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Subfolders")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text="Select Subfolders to Process:", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        info_label = tk.Label(dialog, text="Check the folders you want to include:", font=("Arial", 9))
        info_label.pack(pady=5)
        
        # Frame for checkboxes with scrollbar
        checkbox_frame = tk.Frame(dialog)
        checkbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(checkbox_frame, height=250)
        scrollbar = tk.Scrollbar(checkbox_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create checkboxes for each subfolder
        checkbox_vars = {}
        for i, folder_path in enumerate(subfolders):
            folder_name = os.path.basename(folder_path)
            
            var = tk.BooleanVar(value=True)  # Default to selected
            checkbox_vars[folder_path] = var
            
            checkbox = tk.Checkbutton(
                scrollable_frame,
                text=folder_name,
                variable=var,
                font=("Arial", 9),
                anchor=tk.W
            )
            checkbox.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Add path info
            path_label = tk.Label(
                scrollable_frame,
                text=folder_path,
                font=("Arial", 8),
                fg="gray",
                anchor=tk.W
            )
            path_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def select_all():
            for var in checkbox_vars.values():
                var.set(True)
        
        def select_none():
            for var in checkbox_vars.values():
                var.set(False)
        
        def confirm_selection():
            selected_folders = [folder for folder, var in checkbox_vars.items() if var.get()]
            
            if selected_folders:
                # Add selected folders to the main list
                for folder_path in selected_folders:
                    if folder_path not in self.high_res_source_folders:
                        self.high_res_source_folders.append(folder_path)
                        self.add_folder_to_list(folder_path)
                
                self.update_high_res_ui()
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select at least one folder.", parent=dialog)
        
        def cancel_selection():
            dialog.destroy()
        
        # Control buttons
        select_all_btn = tk.Button(button_frame, text="Select All", command=select_all, width=10)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        select_none_btn = tk.Button(button_frame, text="Select None", command=select_none, width=10)
        select_none_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_selection, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        confirm_btn = tk.Button(button_frame, text="OK", command=confirm_selection, width=10, bg="#4CAF50", fg="white")
        confirm_btn.pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        dialog.wait_window(dialog)
    
    def add_folder_to_list(self, folder_path):
        """Add a folder to the visual list"""
        folder_frame = tk.Frame(self.high_res_folders_frame)
        folder_frame.pack(fill=tk.X, padx=5, pady=2)
        
        folder_label = tk.Label(
            folder_frame,
            text=os.path.basename(folder_path),
            font=("Arial", 9),
            anchor=tk.W,
            width=30
        )
        folder_label.pack(side=tk.LEFT, padx=5)
        
        path_label = tk.Label(
            folder_frame,
            text=folder_path,
            font=("Arial", 8),
            fg="gray",
            anchor=tk.W
        )
        path_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        remove_button = tk.Button(
            folder_frame,
            text="Remove",
            command=lambda: self.remove_high_res_folder(folder_frame, folder_path),
            width=8,
            height=1,
            font=("Arial", 8)
        )
        remove_button.pack(side=tk.RIGHT, padx=5)
    
    def remove_high_res_folder(self, frame, folder_path):
        """Remove a folder from the list"""
        frame.destroy()
        if folder_path in self.high_res_source_folders:
            self.high_res_source_folders.remove(folder_path)
        self.update_high_res_ui()
    
    def clear_high_res_folders(self):
        """Clear all selected folders"""
        self.high_res_source_folders.clear()
        # Clear the visual list
        for widget in self.high_res_folders_frame.winfo_children():
            widget.destroy()
        self.update_high_res_ui()
    
    def browse_high_res_output_folder(self):
        """Browse for output folder"""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.high_res_output_folder = folder_path
            self.high_res_output_entry.delete(0, tk.END)
            self.high_res_output_entry.insert(0, folder_path)
    
    def update_high_res_ui(self):
        """Update the UI based on current state"""
        if self.high_res_source_folders:
            self.high_res_start_button.config(state=tk.NORMAL)
            self.high_res_status_label.config(
                text=f"Ready to process {len(self.high_res_source_folders)} folders",
                fg="blue"
            )
        else:
            self.high_res_start_button.config(state=tk.DISABLED)
            self.high_res_status_label.config(
                text="Add folders to start",
                fg="gray"
            )
    
    def get_image_resolution(self, image_path):
        """Get the resolution (width * height) of an image"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                return width * height  # Total pixels
        except Exception as e:
            print(f"Error getting resolution for {image_path}: {e}")
            return 0
    
    def find_highest_res_image(self, folder_path):
        """Find the highest resolution image in a folder"""
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.tif'}
            image_files = []
            
            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(folder_path, file))
            
            if not image_files:
                return None
            
            # Find image with highest resolution
            best_image = None
            best_resolution = 0
            
            for image_path in image_files:
                resolution = self.get_image_resolution(image_path)
                if resolution > best_resolution:
                    best_resolution = resolution
                    best_image = image_path
            
            return best_image
            
        except Exception as e:
            print(f"Error processing folder {folder_path}: {e}")
            return None
    
    def start_high_res_grabbing(self):
        """Start the high resolution image grabbing process"""
        if not self.high_res_source_folders:
            messagebox.showwarning("Warning", "Please add at least one folder to process")
            return
        
        # Get output folder
        output_folder = self.high_res_output_entry.get().strip()
        if not output_folder:
            messagebox.showwarning("Warning", "Please specify an output folder")
            return
        
        # Create output folder if it doesn't exist
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder: {str(e)}")
            return
        
        # Start processing in a separate thread to avoid freezing UI
        Thread(target=self.process_high_res_folders, args=(output_folder,), daemon=True).start()
    
    def process_high_res_folders(self, output_folder):
        """Process all folders and copy highest resolution images"""
        try:
            total_folders = len(self.high_res_source_folders)
            processed = 0
            copied_images = []
            
            # Clear results
            self.high_res_results_text.delete(1.0, tk.END)
            self.high_res_results_text.insert(tk.END, "Starting high resolution image grabbing...\n\n")
            
            for folder_path in self.high_res_source_folders:
                processed += 1
                progress = (processed / total_folders) * 100
                self.high_res_progress_var.set(progress)
                self.high_res_status_label.config(
                    text=f"Processing folder {processed}/{total_folders}",
                    fg="orange"
                )
                
                # Find highest resolution image in folder
                best_image = self.find_highest_res_image(folder_path)
                
                if best_image:
                    # Get image info
                    folder_name = os.path.basename(folder_path)
                    image_name = os.path.basename(best_image)
                    resolution = self.get_image_resolution(best_image)
                    
                    # Create new filename with folder name prefix
                    new_filename = f"{folder_name}_{image_name}"
                    destination_path = os.path.join(output_folder, new_filename)
                    
                    # Handle duplicate filenames
                    counter = 1
                    original_destination = destination_path
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(original_destination)
                        destination_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Copy the image
                    try:
                        shutil.copy2(best_image, destination_path)
                        copied_images.append({
                            'source': best_image,
                            'destination': destination_path,
                            'folder': folder_name,
                            'resolution': resolution
                        })
                        
                        self.high_res_results_text.insert(tk.END, f"✓ {folder_name}: {image_name} ({resolution:,} pixels)\n")
                        
                    except Exception as e:
                        self.high_res_results_text.insert(tk.END, f"✗ {folder_name}: Failed to copy {image_name} - {str(e)}\n")
                        
                else:
                    self.high_res_results_text.insert(tk.END, f"✗ {os.path.basename(folder_path)}: No images found\n")
                
                self.root.update()
            
            # Final results
            self.high_res_progress_var.set(100)
            self.high_res_status_label.config(
                text=f"Complete! Copied {len(copied_images)} images",
                fg="green"
            )
            
            self.high_res_results_text.insert(tk.END, f"\n{'='*50}\n")
            self.high_res_results_text.insert(tk.END, f"Process complete!\n")
            self.high_res_results_text.insert(tk.END, f"Total folders processed: {total_folders}\n")
            self.high_res_results_text.insert(tk.END, f"Images copied: {len(copied_images)}\n")
            self.high_res_results_text.insert(tk.END, f"Output folder: {output_folder}\n")
            
            if copied_images:
                self.high_res_results_text.insert(tk.END, f"\nCopied images:\n")
                for img in copied_images:
                    self.high_res_results_text.insert(tk.END, f"  • {img['folder']} → {os.path.basename(img['destination'])}\n")
            
            # Open output folder if images were copied
            if copied_images:
                self.high_res_results_text.insert(tk.END, f"\nOpening output folder...\n")
                try:
                    os.startfile(output_folder)
                except:
                    pass
            
        except Exception as e:
            self.high_res_status_label.config(text="Process failed", fg="red")
            self.high_res_results_text.insert(tk.END, f"\nError: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to process folders: {str(e)}")





 
 

 
 

 
 

 
 


def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

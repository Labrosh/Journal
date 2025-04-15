import tkinter as tk
from tkinter import messagebox, ttk, font, filedialog  # Add filedialog import
import json
import os
from datetime import datetime

JOURNAL_FILE = "journal.json"  # Keep default filename as fallback

# Basic structure of the journal
default_journal = {
    # Header fields
    "Name": "",
    "Stage": "",
    
    # Cultivation tab
    "Path/Style": "",
    "Affinity/Element(s)": "",
    "Notable Breakthroughs": "",
    "Active Techniques": "",
    "Passive Techniques": "",
    
    # Background tab
    "Origin/Background": "",
    "Known By": "",
    "Notable Actions": "",
    
    # Inventory tab
    "Spirit Stones": "0",
    "Items/Artifacts": "",
    "Consumables": "",
    
    # Quests & Goals tab
    "Goals": "",
    "Hints & Rumors": "",
    "Unfinished Quests": "",
    
    # Session Journal tab
    "Session Notes": "",
    
    # AI Prompt (used when sharing with AI assistants)
    "AI Prompt": """This is my Cultivation Journal for my character in a cultivation-themed roleplaying game.

This journal tracks my character's cultivation journey, including their techniques, breakthroughs, inventory, and goals.

When responding about this journal:
- Refer to my character by name and respect their current cultivation stage
- Use terminology and concepts from cultivation novels (qi, meridians, spiritual energy, etc.)
- Help me brainstorm next steps based on my character's current goals and situation
- Feel free to suggest potential plot developments or challenges based on the information provided
- Maintain the tone and setting of a cultivation world

The journal is organized into sections for Cultivation details, Background information, Inventory, and Quests & Goals.""",
    
    # Metadata (not displayed directly)
    "Last Updated": "",
    "Window Width": 800,
    "Window Height": 600
}

class CultivationJournalApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cultivation Journal")
        self.style = ttk.Style(self.master)  # Store style object

        # Set initial theme (can be overridden by saved settings later)
        self.active_theme = "Mortal Realm"  # Start with the neutral theme

        # Define themes dictionary BEFORE first apply_theme call
        self.themes = {
            "Mortal Realm": {"base_theme": "clam", "bg": "#F5F5F5", "fg": "#212121", "text_bg": "#FFFFFF", "button_bg": "#E0E0E0"},  # Neutral grey/white
            "Jade Forest": {"base_theme": "clam", "bg": "#E8F5E9", "fg": "#1B5E20", "text_bg": "#FFFFFF", "button_bg": "#A5D6A7"},
            "Crimson Path": {"base_theme": "clam", "bg": "#212121", "fg": "#FFCDD2", "text_bg": "#424242", "button_bg": "#E57373"},
            "Azure Sky": {"base_theme": "clam", "bg": "#E3F2FD", "fg": "#0D47A1", "text_bg": "#FFFFFF", "button_bg": "#90CAF9"},
            "Scholarly Scroll": {"base_theme": "clam", "bg": "#FFF8E1", "fg": "#4E342E", "text_bg": "#FFFDE7", "button_bg": "#FFCC80"}
        }

        self.journal = default_journal.copy()  # Initialize journal data first
        self.fields = {}  # Initialize fields dictionary BEFORE applying theme
        self.last_focused_text_widget = None  # Track the text widget that last had focus
        self.status_bar = None  # Will hold reference to status bar
        self.current_file = None  # Track which file is currently open

        # Set window size from saved settings or defaults
        width = self.journal.get("Window Width", 800)
        height = self.journal.get("Window Height", 600)
        self.master.geometry(f"{width}x{height}")
        
        # Bind window resize event to save dimensions
        self.master.bind("<Configure>", self.on_window_resize)
        
        # Setup keyboard shortcuts
        self.master.bind("<Control-s>", self.save_journal)
        self.master.bind("<Control-l>", self.load_journal)
        self.master.bind("<Control-n>", self.clear_journal)
        self.master.bind("<Control-o>", self.load_journal)
        
        self.apply_theme(self.active_theme)  # Apply initial theme

        self.create_menu()  # Add menu bar
        self.create_widgets()

    def create_widgets(self):
        # --- Main Container Frame ---
        main_container = ttk.Frame(self.master, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        
        # Configure rows for layout sections
        main_container.rowconfigure(0, weight=0)  # Header (fixed height)
        main_container.rowconfigure(1, weight=1)  # Content (expandable)
        main_container.rowconfigure(2, weight=0)  # Footer (fixed height)
        main_container.columnconfigure(0, weight=1)  # All sections expand horizontally
        
        # --- 1. HEADER AREA ---
        header_frame = ttk.Frame(main_container, padding=(0, 0, 0, 10))
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Left side: Character name with label
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(name_frame, text="Character Name:", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        name_entry = ttk.Entry(name_frame, width=30, font=("TkDefaultFont", 10))
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.fields["Name"] = name_entry  # Store the Entry widget
        name_entry.insert(0, self.journal.get("Name", ""))
        
        # Update window title when name changes
        name_entry.bind("<KeyRelease>", self.update_window_title)
        name_entry.bind("<FocusIn>", self._on_entry_focus)
        
        # Right side: Cultivation stage with label
        stage_frame = ttk.Frame(header_frame)
        stage_frame.pack(side=tk.RIGHT)
        
        ttk.Label(stage_frame, text="Cultivation Stage:", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        stage_entry = ttk.Entry(stage_frame, width=20, font=("TkDefaultFont", 10))
        stage_entry.pack(side=tk.LEFT)
        self.fields["Stage"] = stage_entry  # Store the Entry widget
        stage_entry.insert(0, self.journal.get("Stage", ""))
        stage_entry.bind("<FocusIn>", self._on_entry_focus)
        
        # Theme selector
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side=tk.RIGHT, padx=(0, 20))
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(10, 5))
        theme_combo = ttk.Combobox(theme_frame, values=list(self.themes.keys()), width=15, state="readonly")
        theme_combo.pack(side=tk.LEFT)
        theme_combo.set(self.active_theme)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_theme(theme_combo.get()))
        
        # --- 2. MAIN CONTENT AREA (NOTEBOOK) ---
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create Notebook (Tabbed interface)
        notebook = ttk.Notebook(content_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Define tab structure and fields for each tab
        # Create status bar at the bottom of content frame
        self.status_bar = ttk.Label(content_frame, text="", anchor="e", padding=(5, 2))
        self.status_bar.grid(row=1, column=0, sticky=(tk.E, tk.W))
        self.update_status_bar()
        
        tabs_config = {
            "Cultivation": ["Path/Style", "Affinity/Element(s)", "Notable Breakthroughs", "Active Techniques", "Passive Techniques"],
            "Background": ["Origin/Background", "Known By", "Notable Actions"],
            "Inventory": ["Spirit Stones", "Items/Artifacts", "Consumables"],
            "Quests & Goals": ["Goals", "Hints & Rumors", "Unfinished Quests"],
            "Session Journal": ["Session Notes"]
        }
        
        # Create tabs and place widgets
        for tab_name, fields_in_tab in tabs_config.items():
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text=tab_name)
            tab_frame.columnconfigure(1, weight=1)  # Allow content column to expand
            
            row = 0
            for key in fields_in_tab:
                if key in self.journal:  # Ensure the key exists in our default journal
                    # Label
                    label = ttk.Label(tab_frame, text=key + ":", font=("TkDefaultFont", 9, "bold"))
                    label.grid(row=row, column=0, sticky="nw", padx=5, pady=5)
                    
                    # Choose appropriate widget type based on the field
                    if key == "Spirit Stones":
                        # Use Spinbox for numeric values
                        spinbox = ttk.Spinbox(tab_frame, from_=0, to=1000000, width=10)
                        spinbox.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                        spinbox.set(self.journal.get(key, "0"))
                        self.fields[key] = spinbox
                        spinbox.bind("<FocusIn>", self._on_entry_focus)
                    else:
                        # Use Text widget for multi-line fields
                        # Adjust height based on expected content length
                        # Make Session Notes much taller
                        if key == "Session Notes":
                            height = 15  # Taller for session journal
                        elif key in ["Origin/Background", "Notable Actions", "Goals"]:
                            height = 5   # Medium height for important narrative fields
                        else:
                            height = 3   # Standard height for other fields
                        
                        text_widget = tk.Text(tab_frame, wrap="word", height=height, width=50)
                        
                        # Configure text tags for formatting
                        text_widget.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
                        text_widget.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
                        
                        # Add scrollbar
                        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=text_widget.yview)
                        text_widget.configure(yscrollcommand=scrollbar.set)
                        
                        # Grid placement
                        text_widget.grid(row=row, column=1, sticky="nsew", padx=(5, 0), pady=5)
                        scrollbar.grid(row=row, column=2, sticky="ns", padx=(0, 5), pady=5)
                        
                        # Insert content and store widget reference
                        text_widget.insert("1.0", self.journal.get(key, ""))
                        self.fields[key] = text_widget
                        
                        # Bind focus event
                        text_widget.bind("<FocusIn>", self._on_text_focus)
                    
                    # Add separator after certain fields for visual grouping
                    if key in ["Affinity/Element(s)", "Passive Techniques", "Notable Actions", "Items/Artifacts"]:
                        separator = ttk.Separator(tab_frame, orient="horizontal")
                        row += 1
                        separator.grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
                    
                    row += 1
        
        # --- 3. FOOTER AREA ---
        footer_frame = ttk.Frame(main_container, padding=(0, 10, 0, 0))
        footer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Left side: Action buttons
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="New (Ctrl+N)", command=self.clear_journal).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save (Ctrl+S)", command=self.save_journal).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load (Ctrl+L)", command=self.load_journal).pack(side=tk.LEFT, padx=5)
        
        # Right side: Formatting toolbar
        format_frame = ttk.Frame(footer_frame)
        format_frame.pack(side=tk.RIGHT)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="B", width=2, command=lambda: self.toggle_tag("bold")).pack(side=tk.LEFT, padx=2)
        ttk.Button(format_frame, text="I", width=2, command=lambda: self.toggle_tag("italic")).pack(side=tk.LEFT, padx=2)

    def save_journal(self, event=None):  # Add optional event parameter for key binding
        """Saves the journal data to file, including a timestamp."""
        # Read current values from widgets before saving
        for key in self.journal:
            if key in self.fields:
                # Handle different widget types
                if isinstance(self.fields[key], tk.Text):
                    # Get text from start ('1.0') to end ('end'), stripping trailing newline
                    self.journal[key] = self.fields[key].get("1.0", "end-1c").strip()
                elif isinstance(self.fields[key], ttk.Entry):
                    # Get text from Entry widget
                    self.journal[key] = self.fields[key].get().strip()
                elif isinstance(self.fields[key], ttk.Spinbox):
                    # Get value from Spinbox
                    self.journal[key] = self.fields[key].get()
        
        # Save window dimensions
        self.journal["Window Width"] = self.master.winfo_width()
        self.journal["Window Height"] = self.master.winfo_height()
        
        # Ensure AI Prompt is saved
        if "AI Prompt" not in self.journal:
            self.journal["AI Prompt"] = default_journal["AI Prompt"]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.journal["Last Updated"] = timestamp
        
        # Determine character name for suggested filename
        character_name = self.journal.get("Name", "").strip()
        default_filename = f"{character_name}_journal.json" if character_name else JOURNAL_FILE
        
        # Use current file if exists, otherwise prompt for location
        file_to_save = self.current_file if self.current_file else None
        
        if not file_to_save:
            # Show save dialog with default filename and only allow .json files
            file_to_save = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialfile=default_filename,
                title="Save Cultivation Journal"
            )
        
        if file_to_save:  # User selected a file
            self.current_file = file_to_save  # Update current file
            
            with open(file_to_save, "w") as f:
                json.dump(self.journal, f, indent=4)
                
            # Update status bar
            self.update_status_bar(f"Saved to {os.path.basename(file_to_save)} at {timestamp}")
            
            # Update window title
            self.update_window_title()
            
            return True  # Save successful
        
        return False  # Save cancelled

    def save_as_journal(self):
        """Saves the journal to a new file location."""
        # Reset current file to force file dialog
        orig_file = self.current_file
        self.current_file = None
        
        # Call save_journal which will now show dialog
        if self.save_journal():
            return True
        else:
            # Restore original file if save was cancelled
            self.current_file = orig_file
            return False

    def load_journal(self, event=None):  # Add optional event parameter
        """Loads the journal data from a user-selected file."""
        file_to_load = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Load Cultivation Journal"
        )
        
        if not file_to_load:  # User cancelled
            return False
            
        try:
            with open(file_to_load, "r") as f:
                loaded_journal = json.load(f)
                
            # Check if it's a valid journal file (has at least some essential keys)
            essential_keys = ["Name", "Stage"]
            if not all(key in loaded_journal for key in essential_keys):
                messagebox.showwarning(
                    "Invalid Journal File", 
                    "The selected file does not appear to be a valid Cultivation Journal."
                )
                return False
                
            # Update current file reference
            self.current_file = file_to_load
            
            # Apply the loaded journal
            self.journal = loaded_journal
            
            # Ensure AI Prompt exists after loading
            if "AI Prompt" not in self.journal:
                self.journal["AI Prompt"] = default_journal["AI Prompt"]
                
            # Update UI fields
            for key in self.journal:
                if key in self.fields:
                    if isinstance(self.fields[key], tk.Text):
                        # Clear existing text and insert loaded value
                        self.fields[key].delete("1.0", "end")
                        self.fields[key].insert("1.0", self.journal.get(key, ""))
                    elif isinstance(self.fields[key], ttk.Entry):
                        # Clear and set Entry widget
                        self.fields[key].delete(0, tk.END)
                        self.fields[key].insert(0, self.journal.get(key, ""))
                    elif isinstance(self.fields[key], ttk.Spinbox):
                        # Set Spinbox value
                        self.fields[key].set(self.journal.get(key, "0"))
            
            # Update window title to reflect loaded file
            self.update_window_title()
            
            # Show timestamp if available
            timestamp = self.journal.get("Last Updated", "")
            file_name = os.path.basename(file_to_load)
            if timestamp:
                self.update_status_bar(f"Loaded {file_name} (Last updated: {timestamp})")
                messagebox.showinfo("Loaded", f"Journal loaded successfully from {file_name}!\nLast updated: {timestamp}")
            else:
                self.update_status_bar(f"Loaded {file_name}")
                messagebox.showinfo("Loaded", f"Journal loaded successfully from {file_name}!")
                
            return True
            
        except json.JSONDecodeError:
            messagebox.showerror(
                "Load Failed", 
                f"Failed to load journal. The file is not valid JSON format."
            )
        except Exception as e:
            messagebox.showerror("Load Failed", f"An error occurred while loading: {str(e)}")
            
        return False

    def clear_journal(self, event=None):  # Add optional event parameter
        """Clears all fields to their default state after confirmation."""
        if messagebox.askyesno("Confirm New", "Are you sure you want to clear all fields? Unsaved changes will be lost."):
            self.journal = default_journal.copy()  # Reset internal data
            self.current_file = None  # Reset current file reference
            
            for key, widget in self.fields.items():
                if isinstance(widget, tk.Text):
                    widget.delete("1.0", "end")
                    widget.insert("1.0", self.journal.get(key, ""))  # Insert default value
                elif isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, self.journal.get(key, ""))
                elif isinstance(widget, ttk.Spinbox):
                    widget.set(self.journal.get(key, "0"))
                    
            # Update window title and status bar
            self.update_window_title()
            self.update_status_bar("New journal created")
            return True
        return False

    def create_menu(self):
        """Creates the main menu bar."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File menu - add this new menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New (Ctrl+N)", command=self.clear_journal)
        file_menu.add_command(label="Open... (Ctrl+O)", command=self.load_journal)
        file_menu.add_command(label="Save (Ctrl+S)", command=self.save_journal)
        file_menu.add_command(label="Save As...", command=self.save_as_journal)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Themes Submenu
        themes_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Themes", menu=themes_menu)

        # Populate themes menu from the themes dictionary defined in __init__
        for theme_name in self.themes:
            themes_menu.add_command(label=theme_name, command=lambda t=theme_name: self.apply_theme(t))
            
        # Add separator and AI Prompt option
        settings_menu.add_separator()
        settings_menu.add_command(label="Edit AI Prompt...", command=self.edit_ai_prompt)

    def on_exit(self):
        """Handle application exit with unsaved changes check."""
        # Check for unsaved changes
        if self._has_unsaved_changes():
            if messagebox.askyesno("Unsaved Changes", 
                                 "You have unsaved changes. Would you like to save before exiting?"):
                if not self.save_journal():
                    # User cancelled save, abort exit
                    return
        
        self.master.quit()
        
    def _has_unsaved_changes(self):
        """Check if there are unsaved changes by comparing with current file."""
        # Simple implementation - can be enhanced to actually compare content
        if self.current_file is None and any(
            self.fields[key].get() != "" if isinstance(self.fields[key], ttk.Entry) else
            self.fields[key].get("1.0", "end-1c").strip() != "" 
            for key in self.fields if key != "Spirit Stones"
        ):
            return True
            
        # More sophisticated checking could be added here
        return False
    
    def update_window_title(self, event=None):
        """Updates the window title to include character name and filename."""
        name = ""
        if "Name" in self.fields:
            if isinstance(self.fields["Name"], ttk.Entry):
                name = self.fields["Name"].get().strip()
        
        title_parts = []
        if name:
            title_parts.append(name)
            
        if self.current_file:
            file_name = os.path.basename(self.current_file)
            title_parts.append(f"[{file_name}]")
            
        if title_parts:
            self.master.title(f"{' - '.join(title_parts)} - Cultivation Journal")
        else:
            self.master.title("Cultivation Journal")

    def apply_theme(self, theme_name):
        """Applies the selected color theme."""
        if theme_name not in self.themes:
            print(f"Theme '{theme_name}' not found.")
            return

        self.active_theme = theme_name
        theme_config = self.themes[theme_name]
        base_theme = theme_config.get("base_theme", "clam")  # Default to clam if not specified

        try:
            self.style.theme_use(base_theme)
        except tk.TclError:
            print(f"Base theme '{base_theme}' not available, using default.")
            try:
                self.style.theme_use('default')  # Try default as fallback
            except tk.TclError:
                print("Default theme also not available. Styling might be inconsistent.")
                return  # Cannot proceed without a base theme

        print(f"Applying theme: {theme_name}")  # Debug print

        # --- Configure Styles based on theme_config ---
        # Define default fallbacks if a theme doesn't specify a color
        default_bg = "#F0F0F0"  # System default-like grey
        default_fg = "#000000"  # Black
        default_text_bg = "#FFFFFF"  # White
        default_button_bg = "#E0E0E0"  # Light grey

        bg_color = theme_config.get("bg", default_bg)
        fg_color = theme_config.get("fg", default_fg)
        text_bg_color = theme_config.get("text_bg", default_text_bg)
        button_bg_color = theme_config.get("button_bg", default_button_bg)

        # Configure root window background (always apply, using fallback if needed)
        self.master.config(bg=bg_color)

        # Configure general ttk widget styles
        self.style.configure('.', background=bg_color, foreground=fg_color)  # General style for all ttk widgets
        self.style.configure('TFrame', background=bg_color)  # Frames
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)  # Labels
        self.style.configure('TNotebook', background=bg_color)  # Notebook background
        self.style.configure('TNotebook.Tab', background=bg_color, foreground=fg_color)  # Tab labels
        select_bg_color = button_bg_color  # Simple example: use button color for selected tab
        self.style.map('TNotebook.Tab', background=[('selected', select_bg_color)], foreground=[('selected', fg_color)])

        self.style.configure('TButton', background=button_bg_color, foreground=fg_color)  # Buttons
        self.style.map('TButton',
                       background=[('active', bg_color), ('pressed', fg_color)],  # Example: Invert on press
                       foreground=[('active', fg_color), ('pressed', bg_color)])

        # Configure Text widgets (not ttk, need direct config - always apply using fallbacks)
        for key, widget in self.fields.items():
            if isinstance(widget, tk.Text):
                widget.config(bg=text_bg_color, fg=fg_color, insertbackground=fg_color)  # Set text bg, fg, and cursor color

        # Configure Scrollbars (ttk)
        self.style.configure('Vertical.TScrollbar', background=button_bg_color)  # Scrollbar color matches button

    def _on_entry_focus(self, event):
        """Callback function to clear the last focused text widget when an Entry gets focus."""
        self.last_focused_text_widget = None
        
    def _on_text_focus(self, event):
        """Callback function to store the text widget that gained focus."""
        self.last_focused_text_widget = event.widget

    def toggle_tag(self, tag_name):
        """Toggles the given tag on the selected text in the LAST FOCUSED Text widget."""
        widget = self.last_focused_text_widget  # Use the stored widget reference

        if not widget:
            return

        if not isinstance(widget, tk.Text):
            return

        try:
            # Check if the tag is already applied to the selection
            current_tags = widget.tag_names("sel.first")
            if tag_name in current_tags:
                # If applied, remove it
                widget.tag_remove(tag_name, "sel.first", "sel.last")
            else:
                # If not applied, add it
                widget.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass
    
    def update_status_bar(self, message=None):
        """Updates the status bar with the last saved time or a custom message."""
        if self.status_bar:
            if message:
                self.status_bar.config(text=message)
            else:
                timestamp = self.journal.get("Last Updated", "")
                if timestamp:
                    self.status_bar.config(text=f"Last saved: {timestamp}")
                else:
                    self.status_bar.config(text="Not saved yet")
    
    def on_window_resize(self, event=None):
        """Captures window resize events to save dimensions."""
        if event and event.widget == self.master:
            if hasattr(self.master, 'after_id'):
                self.master.after_cancel(self.master.after_id)
            self.master.after_id = self.master.after(250, lambda: None)
    
    def edit_ai_prompt(self):
        """Opens a dialog to edit the AI prompt."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit AI Prompt")
        dialog.geometry("600x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Edit the prompt that will be included when sharing your journal with AI assistants:",
                 wraplength=580).pack(pady=(0, 10))
        
        text_area = tk.Text(frame, wrap="word", height=15, width=70)
        text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(text_area, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        current_prompt = self.journal.get("AI Prompt", default_journal["AI Prompt"])
        text_area.insert("1.0", current_prompt)
        
        default_prompt = """This is my Cultivation Journal for my character in a cultivation-themed roleplaying game.

This journal tracks my character's cultivation journey, including their techniques, breakthroughs, inventory, and goals.

When responding about this journal:
- Refer to my character by name and respect their current cultivation stage
- Use terminology and concepts from cultivation novels (qi, meridians, spiritual energy, etc.)
- Help me brainstorm next steps based on my character's current goals and situation
- Feel free to suggest potential plot developments or challenges based on the information provided
- Maintain the tone and setting of a cultivation world

The journal is organized into sections for Cultivation details, Background information, Inventory, and Quests & Goals."""
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def reset_to_default():
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", default_prompt)
        
        reset_button = ttk.Button(button_frame, text="Reset to Default", command=reset_to_default)
        reset_button.pack(side=tk.LEFT, padx=(0, 5))
        
        def save_prompt():
            new_prompt = text_area.get("1.0", "end-1c")
            self.journal["AI Prompt"] = new_prompt
            dialog.destroy()
            self.update_status_bar("AI Prompt updated")
        
        save_button = ttk.Button(button_frame, text="Save", command=save_prompt)
        save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(5, 5))
        
        dialog.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - dialog.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CultivationJournalApp(root)
    root.mainloop()

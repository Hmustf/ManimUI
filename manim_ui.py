import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QSpinBox, 
                           QPushButton, QComboBox, QFileDialog, QTextEdit,
                           QMessageBox, QRadioButton, QButtonGroup, QCheckBox,
                           QColorDialog, QSlider, QFrame, QScrollArea, QSizePolicy,
                           QGridLayout, QMenuBar, QMenu, QTabWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QKeySequence, QShortcut, QAction
from manim import *
import tempfile
import glob
import subprocess
import time

class ManimUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manim Text Animation UI")
        self.setMinimumSize(1200, 800)
        
        # Initialize theme
        self.is_dark_theme = True
        self.setup_theme()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Initialize recent projects list
        self.recent_projects = []
        self.max_recent_projects = 5
        
        # Create temporary directory for preview files
        self.temp_dir = tempfile.mkdtemp()
        
        # Define available animation methods
        self.animation_methods = {
            "Simple Fade In": FadeIn,
            "Write Text": Write,
            "Create": Create,
            "Grow from Center": GrowFromCenter,
            "Draw with Border": DrawBorderThenFill
        }
        
        self.fade_out_methods = {
            "Simple Fade Out": FadeOut,
            "Erase Text": Unwrite,
            "Uncreate": Uncreate,
            "Shrink to Center": ShrinkToCenter
        }
        
        # Quality options with friendly names
        self.quality_options = {
            "Low Quality (Fast)": "low_quality",
            "Medium Quality": "medium_quality",
            "High Quality": "high_quality",
            "Production Quality (Slow)": "production_quality"
        }
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Main horizontal layout to split controls and preview
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget for controls
        tab_widget = QTabWidget()
        tab_widget.setMinimumWidth(500)
        
        # Create Text Animation tab
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        text_layout.setSpacing(15)
        
        # Create scroll area for text controls
        text_scroll = QScrollArea()
        text_scroll_widget = QWidget()
        text_scroll_layout = QVBoxLayout(text_scroll_widget)
        text_scroll.setWidget(text_scroll_widget)
        text_scroll.setWidgetResizable(True)
        text_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text_layout.addWidget(text_scroll)
        
        # Project name input
        project_group = QHBoxLayout()
        project_group.setSpacing(10)
        project_label = QLabel("Project Name:")
        project_label.setMinimumWidth(120)
        self.project_name = QLineEdit()
        self.project_name.setMinimumHeight(30)
        self.project_name.setPlaceholderText("Enter project name...")
        project_group.addWidget(project_label)
        project_group.addWidget(self.project_name, stretch=1)
        text_scroll_layout.addLayout(project_group)
        
        # Text/LaTeX mode selection
        mode_group = QHBoxLayout()
        mode_group.setSpacing(10)
        mode_label = QLabel("Render Mode:")
        mode_label.setMinimumWidth(120)
        mode_buttons = QHBoxLayout()
        self.text_mode = QRadioButton("Text")
        self.latex_mode = QRadioButton("LaTeX")
        self.text_mode.setChecked(True)
        mode_buttons.addWidget(self.text_mode)
        mode_buttons.addWidget(self.latex_mode)
        mode_buttons.addStretch()
        mode_group.addWidget(mode_label)
        mode_group.addLayout(mode_buttons)
        text_scroll_layout.addLayout(mode_group)
        
        # Font size
        font_group = QHBoxLayout()
        font_group.setSpacing(10)
        font_size_label = QLabel("Font Size:")
        font_size_label.setMinimumWidth(120)
        self.font_size = QSpinBox()
        self.font_size.setRange(12, 200)
        self.font_size.setValue(48)
        self.font_size.setSingleStep(2)
        self.font_size.setFixedWidth(100)
        self.font_size.setMinimumHeight(30)
        font_group.addWidget(font_size_label)
        font_group.addWidget(self.font_size)
        font_group.addStretch()
        text_scroll_layout.addLayout(font_group)
        
        # Color selection section
        color_section = QVBoxLayout()
        color_section.setSpacing(10)
        
        # Color mode frame
        mode_frame = QFrame()
        mode_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        mode_layout = QVBoxLayout(mode_frame)
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(10, 10, 10, 10)
        
        color_mode_label = QLabel("Color Mode:")
        mode_layout.addWidget(color_mode_label)
        
        self.solid_color_radio = QRadioButton("Solid Color")
        self.gradient_color_radio = QRadioButton("Gradient Color")
        self.solid_color_radio.setChecked(True)
        mode_layout.addWidget(self.solid_color_radio)
        mode_layout.addWidget(self.gradient_color_radio)
        
        color_section.addWidget(mode_frame)
        
        # Solid color selection
        self.solid_color_frame = QFrame()
        solid_layout = QHBoxLayout(self.solid_color_frame)
        solid_layout.setSpacing(10)
        color_label = QLabel("Text Color:")
        color_label.setMinimumWidth(100)
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.current_color = "#FFFFFF"
        self.update_color_button()
        solid_layout.addWidget(color_label)
        solid_layout.addWidget(self.color_button)
        solid_layout.addStretch()
        color_section.addWidget(self.solid_color_frame)
        
        # Gradient color selection
        self.gradient_frame = QFrame()
        gradient_layout = QVBoxLayout(self.gradient_frame)
        gradient_layout.setSpacing(10)
        
        gradient_colors_row = QHBoxLayout()
        gradient_label = QLabel("Gradient Colors:")
        gradient_label.setMinimumWidth(100)
        gradient_colors_row.addWidget(gradient_label)
        self.gradient_color1_button = QPushButton()
        self.gradient_color2_button = QPushButton()
        self.gradient_color1_button.setFixedSize(30, 30)
        self.gradient_color2_button.setFixedSize(30, 30)
        self.gradient_color1 = "#FF0000"
        self.gradient_color2 = "#0000FF"
        self.update_gradient_buttons()
        gradient_colors_row.addWidget(self.gradient_color1_button)
        gradient_colors_row.addWidget(self.gradient_color2_button)
        gradient_colors_row.addStretch()
        gradient_layout.addLayout(gradient_colors_row)
        
        color_section.addWidget(self.gradient_frame)
        text_scroll_layout.addLayout(color_section)
        
        # Text input section
        text_group = QVBoxLayout()
        text_group.setSpacing(5)
        text_label = QLabel("Enter Text/LaTeX:")
        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(100)
        text_group.addWidget(text_label)
        text_group.addWidget(self.text_input)
        text_scroll_layout.addLayout(text_group)
        
        # Animation controls
        anim_section = QVBoxLayout()
        anim_section.setSpacing(10)
        
        # Fade in controls
        fade_in_group = QGridLayout()
        fade_in_group.setSpacing(10)
        fade_in_label = QLabel("Animation In:")
        self.fade_in_method = QComboBox()
        self.fade_in_method.setMinimumHeight(30)
        self.fade_in_method.setMinimumWidth(200)
        self.fade_in_method.addItems(self.animation_methods.keys())
        fade_in_duration_label = QLabel("Duration (s):")
        self.fade_in_duration = QSpinBox()
        self.fade_in_duration.setRange(1, 100)
        self.fade_in_duration.setValue(1)
        self.fade_in_duration.setFixedWidth(100)
        self.fade_in_duration.setMinimumHeight(30)
        fade_in_group.addWidget(fade_in_label, 0, 0)
        fade_in_group.addWidget(self.fade_in_method, 0, 1)
        fade_in_group.addWidget(fade_in_duration_label, 1, 0)
        fade_in_group.addWidget(self.fade_in_duration, 1, 1)
        anim_section.addLayout(fade_in_group)
        
        # Wait duration
        wait_group = QGridLayout()
        wait_group.setSpacing(10)
        wait_label = QLabel("Wait Duration:")
        wait_duration_label = QLabel("Duration (s):")
        self.wait_duration = QSpinBox()
        self.wait_duration.setRange(0, 100)
        self.wait_duration.setValue(2)
        self.wait_duration.setFixedWidth(100)
        self.wait_duration.setMinimumHeight(30)
        empty_widget = QWidget()
        empty_widget.setFixedSize(200, 30)
        wait_group.addWidget(wait_label, 0, 0)
        wait_group.addWidget(empty_widget, 0, 1)
        wait_group.addWidget(wait_duration_label, 1, 0)
        wait_group.addWidget(self.wait_duration, 1, 1)
        anim_section.addLayout(wait_group)
        
        # Fade out controls
        fade_out_group = QGridLayout()
        fade_out_group.setSpacing(10)
        fade_out_label = QLabel("Animation Out:")
        self.fade_out_method = QComboBox()
        self.fade_out_method.setMinimumHeight(30)
        self.fade_out_method.setMinimumWidth(200)
        self.fade_out_method.addItems(self.fade_out_methods.keys())
        fade_out_duration_label = QLabel("Duration (s):")
        self.fade_out_duration = QSpinBox()
        self.fade_out_duration.setRange(1, 100)
        self.fade_out_duration.setValue(1)
        self.fade_out_duration.setFixedWidth(100)
        self.fade_out_duration.setMinimumHeight(30)
        fade_out_group.addWidget(fade_out_label, 0, 0)
        fade_out_group.addWidget(self.fade_out_method, 0, 1)
        fade_out_group.addWidget(fade_out_duration_label, 1, 0)
        fade_out_group.addWidget(self.fade_out_duration, 1, 1)
        anim_section.addLayout(fade_out_group)
        
        text_scroll_layout.addLayout(anim_section)
        
        # Export controls
        export_section = QVBoxLayout()
        export_section.setSpacing(10)
        
        export_path_label = QLabel("Export Path:")
        export_section.addWidget(export_path_label)
        
        export_group = QHBoxLayout()
        export_group.setSpacing(10)
        self.export_path = QLineEdit()
        self.export_path.setMinimumHeight(30)
        self.export_path.setPlaceholderText("Export path...")
        self.export_path.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.setMinimumHeight(30)
        self.browse_button.setFixedWidth(100)
        export_group.addWidget(self.export_path)
        export_group.addWidget(self.browse_button)
        export_section.addLayout(export_group)
        
        # Quality selection
        quality_group = QHBoxLayout()
        quality_group.setSpacing(10)
        quality_label = QLabel("Quality:")
        quality_label.setMinimumWidth(120)
        self.quality_combo = QComboBox()
        self.quality_combo.setMinimumHeight(30)
        self.quality_combo.setMinimumWidth(200)
        self.quality_combo.addItems(self.quality_options.keys())
        self.quality_combo.setCurrentText("Medium Quality")
        quality_group.addWidget(quality_label)
        quality_group.addWidget(self.quality_combo)
        quality_group.addStretch()
        export_section.addLayout(quality_group)
        
        text_scroll_layout.addLayout(export_section)
        
        # Action buttons
        button_section = QVBoxLayout()
        button_section.setSpacing(10)
        
        self.preview_button = QPushButton("Update Preview")
        self.preview_button.setMinimumHeight(40)
        button_section.addWidget(self.preview_button)
        
        export_buttons = QHBoxLayout()
        export_buttons.setSpacing(10)
        self.export_button = QPushButton("Export Animation")
        self.open_folder_button = QPushButton("Open Export Folder")
        self.export_button.setMinimumHeight(30)
        self.open_folder_button.setMinimumHeight(30)
        export_buttons.addWidget(self.export_button)
        export_buttons.addWidget(self.open_folder_button)
        button_section.addLayout(export_buttons)
        
        text_scroll_layout.addLayout(button_section)
        
        # Create SVG Animation tab
        svg_tab = QWidget()
        svg_layout = QVBoxLayout(svg_tab)
        svg_layout.setSpacing(15)
        
        # Create scroll area for SVG controls
        svg_scroll = QScrollArea()
        svg_scroll_widget = QWidget()
        svg_scroll_layout = QVBoxLayout(svg_scroll_widget)
        svg_scroll.setWidget(svg_scroll_widget)
        svg_scroll.setWidgetResizable(True)
        svg_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        svg_layout.addWidget(svg_scroll)
        
        # SVG File Selection
        svg_file_group = QHBoxLayout()
        svg_file_label = QLabel("SVG File:")
        svg_file_label.setMinimumWidth(120)
        self.svg_path = QLineEdit()
        self.svg_path.setMinimumHeight(30)
        self.svg_path.setPlaceholderText("Select SVG file...")
        self.svg_path.setReadOnly(True)
        self.svg_browse_button = QPushButton("Browse")
        self.svg_browse_button.setMinimumHeight(30)
        self.svg_browse_button.setFixedWidth(100)
        svg_file_group.addWidget(svg_file_label)
        svg_file_group.addWidget(self.svg_path)
        svg_file_group.addWidget(self.svg_browse_button)
        svg_scroll_layout.addLayout(svg_file_group)
        
        # Project name input for SVG
        svg_project_group = QHBoxLayout()
        svg_project_group.setSpacing(10)
        svg_project_label = QLabel("Project Name:")
        svg_project_label.setMinimumWidth(120)
        self.svg_project_name = QLineEdit()
        self.svg_project_name.setMinimumHeight(30)
        self.svg_project_name.setPlaceholderText("Enter project name...")
        svg_project_group.addWidget(svg_project_label)
        svg_project_group.addWidget(self.svg_project_name, stretch=1)
        svg_scroll_layout.addLayout(svg_project_group)
        
        # Scale Factor
        scale_group = QHBoxLayout()
        scale_label = QLabel("Scale Factor:")
        scale_label.setMinimumWidth(120)
        self.scale_factor = QSpinBox()
        self.scale_factor.setRange(1, 20)
        self.scale_factor.setValue(4)
        self.scale_factor.setFixedWidth(100)
        self.scale_factor.setMinimumHeight(30)
        scale_group.addWidget(scale_label)
        scale_group.addWidget(self.scale_factor)
        scale_group.addStretch()
        svg_scroll_layout.addLayout(scale_group)
        
        # Animation controls for SVG
        svg_anim_section = QVBoxLayout()
        svg_anim_section.setSpacing(10)
        
        # Fade in controls
        svg_fade_in_group = QGridLayout()
        svg_fade_in_group.setSpacing(10)
        svg_fade_in_label = QLabel("Animation In:")
        self.svg_fade_in_method = QComboBox()
        self.svg_fade_in_method.setMinimumHeight(30)
        self.svg_fade_in_method.setMinimumWidth(200)
        self.svg_fade_in_method.addItems([
            "Draw Border Then Fill",
            "Create",
            "Fade In",
            "Grow From Center",
            "Show Increasing Subsets",
            "Write",
            "Spiral In",
            "Scale From Point",
            "Rotate In"
        ])
        svg_fade_in_duration_label = QLabel("Duration (s):")
        self.svg_fade_in_duration = QSpinBox()
        self.svg_fade_in_duration.setRange(1, 100)
        self.svg_fade_in_duration.setValue(5)
        self.svg_fade_in_duration.setFixedWidth(100)
        self.svg_fade_in_duration.setMinimumHeight(30)
        svg_fade_in_group.addWidget(svg_fade_in_label, 0, 0)
        svg_fade_in_group.addWidget(self.svg_fade_in_method, 0, 1)
        svg_fade_in_group.addWidget(svg_fade_in_duration_label, 1, 0)
        svg_fade_in_group.addWidget(self.svg_fade_in_duration, 1, 1)
        svg_anim_section.addLayout(svg_fade_in_group)
        
        # Wait duration
        svg_wait_group = QGridLayout()
        svg_wait_group.setSpacing(10)
        svg_wait_label = QLabel("Wait Duration:")
        svg_wait_duration_label = QLabel("Duration (s):")
        self.svg_wait_duration = QSpinBox()
        self.svg_wait_duration.setRange(0, 100)
        self.svg_wait_duration.setValue(10)
        self.svg_wait_duration.setFixedWidth(100)
        self.svg_wait_duration.setMinimumHeight(30)
        empty_widget = QWidget()
        empty_widget.setFixedSize(200, 30)
        svg_wait_group.addWidget(svg_wait_label, 0, 0)
        svg_wait_group.addWidget(empty_widget, 0, 1)
        svg_wait_group.addWidget(svg_wait_duration_label, 1, 0)
        svg_wait_group.addWidget(self.svg_wait_duration, 1, 1)
        svg_anim_section.addLayout(svg_wait_group)
        
        # Fade out controls
        svg_fade_out_group = QGridLayout()
        svg_fade_out_group.setSpacing(10)
        svg_fade_out_label = QLabel("Animation Out:")
        self.svg_fade_out_method = QComboBox()
        self.svg_fade_out_method.setMinimumHeight(30)
        self.svg_fade_out_method.setMinimumWidth(200)
        self.svg_fade_out_method.addItems([
            "Uncreate",
            "Fade Out",
            "Shrink To Center",
            "Unwrite",
            "Show Decreasing Subsets",
            "Spiral Out",
            "Scale To Point",
            "Rotate Out"
        ])
        svg_fade_out_duration_label = QLabel("Duration (s):")
        self.svg_fade_out_duration = QSpinBox()
        self.svg_fade_out_duration.setRange(1, 100)
        self.svg_fade_out_duration.setValue(15)
        self.svg_fade_out_duration.setFixedWidth(100)
        self.svg_fade_out_duration.setMinimumHeight(30)
        svg_fade_out_group.addWidget(svg_fade_out_label, 0, 0)
        svg_fade_out_group.addWidget(self.svg_fade_out_method, 0, 1)
        svg_fade_out_group.addWidget(svg_fade_out_duration_label, 1, 0)
        svg_fade_out_group.addWidget(self.svg_fade_out_duration, 1, 1)
        svg_anim_section.addLayout(svg_fade_out_group)
        
        svg_scroll_layout.addLayout(svg_anim_section)
        
        # Add preview and export controls for SVG
        svg_preview_button = QPushButton("Update SVG Preview")
        svg_preview_button.setMinimumHeight(40)
        svg_scroll_layout.addWidget(svg_preview_button)
        
        # Add export controls for SVG
        svg_export_section = QVBoxLayout()
        svg_export_section.setSpacing(10)
        
        svg_export_path_label = QLabel("Export Path:")
        svg_export_section.addWidget(svg_export_path_label)
        
        svg_export_group = QHBoxLayout()
        svg_export_group.setSpacing(10)
        self.svg_export_path = QLineEdit()
        self.svg_export_path.setMinimumHeight(30)
        self.svg_export_path.setPlaceholderText("Export path...")
        self.svg_export_path.setReadOnly(True)
        self.svg_browse_export_button = QPushButton("Browse")
        self.svg_browse_export_button.setMinimumHeight(30)
        self.svg_browse_export_button.setFixedWidth(100)
        svg_export_group.addWidget(self.svg_export_path)
        svg_export_group.addWidget(self.svg_browse_export_button)
        svg_export_section.addLayout(svg_export_group)
        
        # Quality selection for SVG
        svg_quality_group = QHBoxLayout()
        svg_quality_group.setSpacing(10)
        svg_quality_label = QLabel("Quality:")
        svg_quality_label.setMinimumWidth(120)
        self.svg_quality_combo = QComboBox()
        self.svg_quality_combo.setMinimumHeight(30)
        self.svg_quality_combo.setMinimumWidth(200)
        self.svg_quality_combo.addItems(self.quality_options.keys())
        self.svg_quality_combo.setCurrentText("Medium Quality")
        svg_quality_group.addWidget(svg_quality_label)
        svg_quality_group.addWidget(self.svg_quality_combo)
        svg_quality_group.addStretch()
        svg_export_section.addLayout(svg_quality_group)
        
        svg_scroll_layout.addLayout(svg_export_section)
        
        # Add export buttons for SVG
        svg_button_section = QVBoxLayout()
        svg_button_section.setSpacing(10)
        
        svg_export_buttons = QHBoxLayout()
        svg_export_buttons.setSpacing(10)
        self.svg_export_button = QPushButton("Export Animation")
        self.svg_open_folder_button = QPushButton("Open Export Folder")
        self.svg_export_button.setMinimumHeight(30)
        self.svg_open_folder_button.setMinimumHeight(30)
        svg_export_buttons.addWidget(self.svg_export_button)
        svg_export_buttons.addWidget(self.svg_open_folder_button)
        svg_button_section.addLayout(svg_export_buttons)
        
        svg_scroll_layout.addLayout(svg_button_section)
        
        # Connect SVG export signals
        self.svg_browse_export_button.clicked.connect(lambda: self.browse_export_path(True))
        self.svg_export_button.clicked.connect(self.export_svg_animation)
        self.svg_open_folder_button.clicked.connect(lambda: self.open_export_folder(True))
        
        # Connect SVG signals
        self.svg_browse_button.clicked.connect(self.browse_svg_file)
        svg_preview_button.clicked.connect(self.update_svg_preview)
        self.scale_factor.valueChanged.connect(self.update_svg_preview)
        
        # Add tabs to tab widget
        tab_widget.addTab(text_tab, "Text Animation")
        tab_widget.addTab(svg_tab, "SVG Animation")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget, stretch=0)
        
        # Right panel for preview
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setSpacing(20)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview label and image
        preview_label = QLabel("Preview:")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image = QLabel()
        self.preview_image.setMinimumSize(640, 480)
        self.preview_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image.setStyleSheet("QLabel { background-color: black; color: white; border: 1px solid #666; }")
        self.preview_image.setText("Preview will appear here")
        
        preview_layout.addStretch(1)
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_image)
        preview_layout.addStretch(1)
        
        # Add preview container to main layout
        main_layout.addWidget(preview_container, stretch=1)
        
        # Configure Manim to not open window
        config.preview = False
        config.media_dir = os.path.join(os.getcwd(), "media")
        
        # Initialize color mode after all UI elements are created
        self.update_color_mode()
        
        # Initialize tooltips
        self.setup_tooltips()
        
        # Connect buttons
        self.connect_signals()

    def reset_manim_config(self):
        """Reset Manim's configuration and clear cache"""
        # Clear media directory
        try:
            media_dir = os.path.join(os.getcwd(), "media")
            if os.path.exists(media_dir):
                for subdir in ['images', 'videos', 'texts', 'Tex', 'partial_movie_files']:
                    dir_path = os.path.join(media_dir, subdir)
                    if os.path.exists(dir_path):
                        for file in os.listdir(dir_path):
                            try:
                                os.remove(os.path.join(dir_path, file))
                            except:
                                pass
        except:
            pass
        
        # Reset Manim configuration
        config.preview = False
        config.write_to_movie = False
        config.save_last_frame = True
        config.disable_caching = True
        config.output_file = f"preview_{int(time.time() * 1000)}"
        config.media_dir = os.path.join(os.getcwd(), "media")

    def update_color_mode(self):
        # Show/hide appropriate color controls based on selected mode
        use_gradient = self.gradient_color_radio.isChecked()
        self.solid_color_frame.setVisible(not use_gradient)
        self.gradient_frame.setVisible(use_gradient)
        
        # Force a preview update when changing color mode
        if self.text_input.toPlainText():
            self.reset_manim_config()
            self.update_preview()

    def browse_export_path(self, for_svg=False):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            if for_svg:
                self.svg_export_path.setText(folder)
            else:
                self.export_path.setText(folder)

    def validate_inputs(self):
        if not self.text_input.toPlainText():
            QMessageBox.warning(self, "Input Error", "Please enter some text first!")
            return False
        if not self.project_name.text():
            QMessageBox.warning(self, "Input Error", "Please enter a project name!")
            return False
        return True

    def cleanup_export_files(self, output_file, is_svg=False):
        """Clean up extra files after export, keeping only the final video"""
        try:
            export_dir = self.svg_export_path.text() if is_svg else self.export_path.text()
            # Get the final video file path
            video_file = os.path.join(export_dir, "videos", f"{output_file}.mp4")
            
            if os.path.exists(video_file):
                # Move the video file to the main export directory
                final_path = os.path.join(export_dir, f"{output_file}.mp4")
                os.rename(video_file, final_path)
            
            # Clean up all other files and directories
            for subdir in ['images', 'videos', 'texts', 'Tex', 'partial_movie_files']:
                dir_path = os.path.join(export_dir, subdir)
                if os.path.exists(dir_path):
                    import shutil
                    shutil.rmtree(dir_path)
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")

    def export_animation(self):
        if not self.validate_inputs():
            return
            
        if not self.export_path.text():
            QMessageBox.warning(self, "Error", "Please select an export path first!")
            return
            
        # Configure Manim for video export
        config.preview = False
        config.write_to_movie = True
        config.save_last_frame = False
        output_name = self.project_name.text()
        config.output_file = output_name
        config.media_dir = self.export_path.text()
        # Get the actual quality value from the friendly name
        config.quality = self.quality_options[self.quality_combo.currentText()]
        
        class AnimationScene(Scene):
            def construct(self_scene):
                content = self.text_input.toPlainText()
                
                if self.latex_mode.isChecked():
                    text = MathTex(content)
                    # Apply colors to LaTeX text
                    if self.gradient_color_radio.isChecked():
                        text.set_color_by_gradient(self.gradient_color1, self.gradient_color2)
                    else:
                        text.set_color(self.current_color)
                    # Scale LaTeX text
                    text.scale(self.font_size.value() / 48)
                else:
                    if self.gradient_color_radio.isChecked():
                        text = Text(
                            content,
                            font_size=self.font_size.value(),
                            gradient=(self.gradient_color1, self.gradient_color2)
                        )
                    else:
                        text = Text(
                            content,
                            font_size=self.font_size.value(),
                            color=self.current_color
                        )
                
                # Get selected animation methods
                fade_in_animation = self.animation_methods[self.fade_in_method.currentText()]
                fade_out_animation = self.fade_out_methods[self.fade_out_method.currentText()]
                
                # Fade in with selected method
                self_scene.play(
                    fade_in_animation(text),
                    run_time=self.fade_in_duration.value()
                )
                
                # Wait
                self_scene.wait(self.wait_duration.value())
                
                # Fade out with selected method
                self_scene.play(
                    fade_out_animation(text),
                    run_time=self.fade_out_duration.value()
                )
        
        try:
            scene = AnimationScene()
            scene.render()
            
            # Clean up extra files, keeping only the final video
            self.cleanup_export_files(output_name, is_svg=False)
            
            QMessageBox.information(self, "Success", "Animation exported successfully!")
            
            # Open the export folder after successful export
            self.open_export_folder(is_svg=False)
            
            # Add to recent projects
            self.add_recent_project(self.project_name.text(), self.export_path.text())
            
        except Exception as e:
            error_msg = str(e)
            self.statusBar().showMessage(f"Export failed: {error_msg}")
            QMessageBox.critical(self, "Error", f"Failed to export animation:\n{error_msg}")
        finally:
            self.show_loading_indicator(False)

    def open_export_folder(self, is_svg=False):
        export_path = self.svg_export_path.text() if is_svg else self.export_path.text()
        if not export_path:
            QMessageBox.warning(self, "Error", "No export folder selected!")
            return
            
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', export_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['explorer', export_path])
        else:  # Linux
            subprocess.run(['xdg-open', export_path])

    def closeEvent(self, event):
        # Clean up temporary files when closing the application
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
        super().closeEvent(event)

    def update_color_button(self):
        self.color_button.setStyleSheet(
            f"background-color: {self.current_color}; border: 1px solid #666;"
        )
        
    def update_gradient_buttons(self):
        self.gradient_color1_button.setStyleSheet(
            f"background-color: {self.gradient_color1}; border: 1px solid #666;"
        )
        self.gradient_color2_button.setStyleSheet(
            f"background-color: {self.gradient_color2}; border: 1px solid #666;"
        )
        
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.current_color))
        if color.isValid():
            self.current_color = color.name()
            self.update_color_button()
            self.reset_manim_config()
            self.update_preview()
            
    def choose_gradient_color(self, button_num):
        if button_num == 1:
            color = QColorDialog.getColor(QColor(self.gradient_color1))
            if color.isValid():
                self.gradient_color1 = color.name()
        else:
            color = QColorDialog.getColor(QColor(self.gradient_color2))
            if color.isValid():
                self.gradient_color2 = color.name()
        self.update_gradient_buttons()
        self.reset_manim_config()
        self.update_preview()

    def update_preview(self):
        if not self.text_input.toPlainText():
            self.preview_image.clear()
            self.preview_image.setText("Preview will appear here")
            return

        self.show_loading_indicator(True)
        try:
            # Reset Manim config for preview
            self.reset_manim_config()
            
            class PreviewScene(Scene):
                def construct(self_scene):
                    content = self.text_input.toPlainText()
                    
                    if self.latex_mode.isChecked():
                        text = MathTex(content)
                        text.scale(self.font_size.value() / 48)
                        
                        if self.gradient_color_radio.isChecked():
                            text.set_color_by_gradient(self.gradient_color1, self.gradient_color2)
                        else:
                            text.set_color(self.current_color)
                    else:
                        if self.gradient_color_radio.isChecked():
                            text = Text(
                                content,
                                font_size=self.font_size.value(),
                                gradient=(self.gradient_color1, self.gradient_color2)
                            )
                        else:
                            text = Text(
                                content,
                                font_size=self.font_size.value(),
                                color=self.current_color
                            )
                    
                    text.move_to(ORIGIN)
                    self_scene.add(text)
            
            # Create and render the preview scene
            scene = PreviewScene()
            scene.render()
            
            # Find and display the latest preview
            preview_files = glob.glob(os.path.join(os.getcwd(), "media", "images", "preview_*.png"))
            if preview_files:
                latest_preview = max(preview_files, key=os.path.getctime)
                
                # Load the image and create a pixmap
                pixmap = QPixmap(latest_preview)
                if not pixmap.isNull():
                    # Calculate the scaling while maintaining aspect ratio
                    preview_size = self.preview_image.size()
                    scaled_pixmap = pixmap.scaled(
                        preview_size.width(),
                        preview_size.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # Set the pixmap and ensure proper display
                    self.preview_image.setPixmap(scaled_pixmap)
                    self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Force an immediate update
                    self.preview_image.update()
                    QApplication.processEvents()
                else:
                    self.preview_image.setText("Failed to load preview image")
            else:
                self.preview_image.setText("Preview file not found")
        except Exception as e:
            error_msg = str(e)
            self.statusBar().showMessage(f"Preview failed: {error_msg}")
            self.preview_image.setText(f"Preview failed:\n{error_msg}")
        finally:
            self.show_loading_indicator(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update preview scaling when window is resized
        if hasattr(self.preview_image, 'pixmap') and self.preview_image.pixmap() is not None:
            preview_size = self.preview_image.size()
            scaled_pixmap = self.preview_image.pixmap().scaled(
                preview_size.width(),
                preview_size.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_image.setPixmap(scaled_pixmap)
            self.preview_image.update()
            QApplication.processEvents()

    def setup_shortcuts(self):
        # Update Preview shortcut (Cmd+R or Ctrl+R)
        preview_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        preview_shortcut.activated.connect(self.update_preview)
        
        # Export shortcut (Cmd+E or Ctrl+E)
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_animation)
        
        # Toggle theme shortcut (Cmd+T or Ctrl+T)
        theme_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        theme_shortcut.activated.connect(self.toggle_theme)

    def setup_tooltips(self):
        # Project name tooltip
        self.project_name.setToolTip("Enter a name for your animation project")
        
        # Render mode tooltips
        self.text_mode.setToolTip("Render text as plain text")
        self.latex_mode.setToolTip("Render text using LaTeX formatting")
        
        # Font size tooltip
        self.font_size.setToolTip("Adjust the size of the text (24-96)")
        
        # Color tooltips
        self.color_button.setToolTip("Click to choose a solid color")
        self.gradient_color1_button.setToolTip("Click to choose the starting gradient color")
        self.gradient_color2_button.setToolTip("Click to choose the ending gradient color")
        
        # Animation tooltips
        self.fade_in_method.setToolTip("Choose how the text appears")
        self.fade_out_method.setToolTip("Choose how the text disappears")
        self.fade_in_duration.setToolTip("Duration of the entrance animation (seconds)")
        self.wait_duration.setToolTip("How long to display the text (seconds)")
        self.fade_out_duration.setToolTip("Duration of the exit animation (seconds)")
        
        # Quality tooltip
        self.quality_combo.setToolTip("Select the rendering quality (higher quality takes longer)")

    def show_loading_indicator(self, show=True):
        if show:
            self.statusBar().showMessage("Rendering... Please wait")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            self.statusBar().showMessage("Ready")
            QApplication.restoreOverrideCursor()

    def add_recent_project(self, name, path):
        project = {'name': name, 'path': path}
        if project in self.recent_projects:
            self.recent_projects.remove(project)
        self.recent_projects.insert(0, project)
        if len(self.recent_projects) > self.max_recent_projects:
            self.recent_projects.pop()
        self.update_recent_menu()

    def load_recent_project(self, project):
        self.project_name.setText(project['name'])
        self.export_path.setText(project['path'])

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.setup_theme()
        theme_name = "Dark" if self.is_dark_theme else "Light"
        self.statusBar().showMessage(f"Switched to {theme_name} theme")

    def show_error_dialog(self, title, message, details=None):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.exec()

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Recent projects submenu
        self.recent_menu = QMenu("Recent Projects", self)
        file_menu.addMenu(self.recent_menu)
        
        # Add other menu items
        export_action = QAction("Export Animation", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_animation)
        file_menu.addAction(export_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Theme toggle
        theme_action = QAction("Toggle Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Update preview action
        preview_action = QAction("Update Preview", self)
        preview_action.setShortcut(QKeySequence.StandardKey.Refresh)
        preview_action.triggered.connect(self.update_preview)
        view_menu.addAction(preview_action)

    def update_recent_menu(self):
        self.recent_menu.clear()
        for project in self.recent_projects:
            action = QAction(f"{project['name']} ({project['path']})", self)
            action.triggered.connect(lambda p=project: self.load_recent_project(p))
            self.recent_menu.addAction(action)

    def setup_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QTextEdit, QSpinBox, QComboBox {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 2px;
                }
                QPushButton {
                    background-color: #4b4b4b;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #5b5b5b;
                }
                QPushButton:pressed {
                    background-color: #3b3b3b;
                }
                QScrollArea {
                    border: 1px solid #555555;
                }
                QFrame {
                    border: 1px solid #555555;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #4b4b4b;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #4b4b4b;
                }
                QRadioButton {
                    color: #ffffff;
                }
                QRadioButton::indicator {
                    border: 1px solid #555555;
                    border-radius: 7px;
                }
                QRadioButton::indicator:checked {
                    background-color: #4b9eff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QLineEdit, QTextEdit, QSpinBox, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
                QScrollArea {
                    border: 1px solid #cccccc;
                }
                QFrame {
                    border: 1px solid #cccccc;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QMenuBar::item:selected {
                    background-color: #d0d0d0;
                }
                QMenu {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QMenu::item:selected {
                    background-color: #d0d0d0;
                }
                QRadioButton {
                    color: #000000;
                }
                QRadioButton::indicator {
                    border: 1px solid #cccccc;
                    border-radius: 7px;
                }
                QRadioButton::indicator:checked {
                    background-color: #0078d4;
                }
            """)

    def connect_signals(self):
        # Connect radio buttons
        self.solid_color_radio.toggled.connect(self.update_color_mode)
        self.gradient_color_radio.toggled.connect(self.update_color_mode)
        
        # Connect color buttons
        self.color_button.clicked.connect(self.choose_color)
        self.gradient_color1_button.clicked.connect(lambda: self.choose_gradient_color(1))
        self.gradient_color2_button.clicked.connect(lambda: self.choose_gradient_color(2))
        
        # Connect preview and export buttons
        self.preview_button.clicked.connect(self.update_preview)
        self.export_button.clicked.connect(self.export_animation)
        self.open_folder_button.clicked.connect(lambda: self.open_export_folder(False))
        self.browse_button.clicked.connect(lambda: self.browse_export_path(False))
        
        # Connect text input changes
        self.text_input.textChanged.connect(lambda: self.statusBar().showMessage("Text changed. Click 'Update Preview' to see changes."))
        
        # Connect font size changes to preview update
        self.font_size.valueChanged.connect(self.update_preview)

    def browse_svg_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select SVG File",
            "",
            "SVG Files (*.svg);;All Files (*.*)"
        )
        if file_name:
            self.svg_path.setText(file_name)
            self.update_svg_preview()

    def update_svg_preview(self):
        if not self.svg_path.text():
            self.preview_image.setText("Please select an SVG file")
            return

        self.show_loading_indicator(True)
        try:
            self.reset_manim_config()
            
            class SVGPreviewScene(Scene):
                def construct(self_scene):
                    svg = SVGMobject(self.svg_path.text())
                    svg.scale(self.scale_factor.value())
                    svg.move_to(ORIGIN)
                    self_scene.add(svg)
            
            scene = SVGPreviewScene()
            scene.render()
            
            preview_files = glob.glob(os.path.join(os.getcwd(), "media", "images", "preview_*.png"))
            if preview_files:
                latest_preview = max(preview_files, key=os.path.getctime)
                pixmap = QPixmap(latest_preview)
                if not pixmap.isNull():
                    preview_size = self.preview_image.size()
                    scaled_pixmap = pixmap.scaled(
                        preview_size.width(),
                        preview_size.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.preview_image.setPixmap(scaled_pixmap)
                    self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.preview_image.update()
                    QApplication.processEvents()
                else:
                    self.preview_image.setText("Failed to load preview image")
            else:
                self.preview_image.setText("Preview file not found")
        except Exception as e:
            error_msg = str(e)
            self.statusBar().showMessage(f"SVG Preview failed: {error_msg}")
            self.preview_image.setText(f"SVG Preview failed:\n{error_msg}")
        finally:
            self.show_loading_indicator(False)

    def export_svg_animation(self):
        if not self.svg_path.text():
            QMessageBox.warning(self, "Error", "Please select an SVG file first!")
            return
            
        if not self.svg_project_name.text():
            QMessageBox.warning(self, "Error", "Please enter a project name!")
            return
            
        if not self.svg_export_path.text():
            QMessageBox.warning(self, "Error", "Please select an export path first!")
            return
            
        # Configure Manim for video export
        config.preview = False
        config.write_to_movie = True
        config.save_last_frame = False
        config.output_file = self.svg_project_name.text()
        config.media_dir = self.svg_export_path.text()
        config.quality = self.quality_options[self.svg_quality_combo.currentText()]
        
        class SVGAnimationScene(Scene):
            def construct(self_scene):
                svg = SVGMobject(self.svg_path.text())
                svg.scale(self.scale_factor.value())
                svg.move_to(ORIGIN)
                
                # Get animation methods
                fade_in_method = self.svg_fade_in_method.currentText()
                fade_out_method = self.svg_fade_out_method.currentText()
                
                # Map animation names to Manim classes and functions
                animation_map = {
                    "Draw Border Then Fill": DrawBorderThenFill,
                    "Create": Create,
                    "Fade In": FadeIn,
                    "Grow From Center": GrowFromCenter,
                    "Show Increasing Subsets": ShowIncreasingSubsets,
                    "Write": Write,
                    "Spiral In": lambda m: Create(m, rate_func=spiral),
                    "Scale From Point": lambda m: Create(m, rate_func=lambda t: smooth(t)),
                    "Rotate In": lambda m: Create(m, rate_func=lambda t: smooth(t)),
                    "Uncreate": Uncreate,
                    "Fade Out": FadeOut,
                    "Shrink To Center": ShrinkToCenter,
                    "Unwrite": Unwrite,
                    "Show Decreasing Subsets": lambda m: ShowIncreasingSubsets(m, rate_func=lambda t: 1-smooth(t)),
                    "Spiral Out": lambda m: Uncreate(m, rate_func=spiral),
                    "Scale To Point": lambda m: Uncreate(m, rate_func=lambda t: smooth(t)),
                    "Rotate Out": lambda m: Uncreate(m, rate_func=lambda t: smooth(t))
                }
                
                # Helper function for spiral animation
                def spiral(t):
                    angle = 2 * PI * t
                    return np.array([
                        np.cos(angle) * t,
                        np.sin(angle) * t,
                        0
                    ])
                
                # Get the animation for fade in
                fade_in_anim = animation_map[fade_in_method]
                if isinstance(fade_in_anim, type):
                    anim_in = fade_in_anim(svg)
                else:
                    anim_in = fade_in_anim(svg)
                
                # Get the animation for fade out
                fade_out_anim = animation_map[fade_out_method]
                if isinstance(fade_out_anim, type):
                    anim_out = fade_out_anim(svg)
                else:
                    anim_out = fade_out_anim(svg)
                
                # Animate in
                self_scene.play(anim_in, run_time=self.svg_fade_in_duration.value())
                
                # Wait
                self_scene.wait(self.svg_wait_duration.value())
                
                # Animate out
                self_scene.play(anim_out, run_time=self.svg_fade_out_duration.value())
        
        try:
            scene = SVGAnimationScene()
            scene.render()
            
            # Clean up extra files, keeping only the final video
            self.cleanup_export_files(self.svg_project_name.text(), is_svg=True)
            
            QMessageBox.information(self, "Success", "SVG Animation exported successfully!")
            
            # Open the export folder after successful export
            self.open_export_folder(is_svg=True)
            
            # Add to recent projects
            self.add_recent_project(self.svg_project_name.text(), self.svg_export_path.text())
            
        except Exception as e:
            error_msg = str(e)
            self.statusBar().showMessage(f"Export failed: {error_msg}")
            QMessageBox.critical(self, "Error", f"Failed to export SVG animation:\n{error_msg}")
        finally:
            self.show_loading_indicator(False)

def main():
    app = QApplication(sys.argv)
    window = ManimUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
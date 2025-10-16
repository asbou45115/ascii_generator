from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QSpinBox, QStatusBar,
    QLineEdit, QSlider
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from src.Renderer import Renderer
import sys, os, cv2


class AsciiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Image Renderer")
        self.setGeometry(100, 100, 1200, 800)

        # Default values
        self.file_paths = []
        self.upscale_width = 1920
        self.upscale_height = 1080
        self.edge_tolerance = 13
        self.custom_w = 1920
        self.custom_h = 1080

        # --- Image preview labels ---
        self.input_label = QLabel("No image loaded")
        self.input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_label = QLabel("Rendered output")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Buttons ---
        self.load_btn = QPushButton("Load Images")
        self.load_btn.clicked.connect(self.load_images)

        self.render_btn = QPushButton("Render ASCII")
        self.render_btn.clicked.connect(self.render_ascii)
        self.render_btn.setEnabled(False)

        self.save_btn = QPushButton("Save Output(s)")
        self.save_btn.clicked.connect(self.save_renders)
        self.save_btn.setEnabled(False)

        # --- Resolution dropdown ---
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1080p (1920x1080)",
            "1440p (2560x1440)",
            "4K (3840x2160)",
            "Custom"
        ])
        self.resolution_combo.currentTextChanged.connect(self.change_resolution)

        # --- Width / Height inputs (hidden until Custom selected) ---
        self.width_label = QLabel("W:")
        self.height_label = QLabel("H:")
        self.width_input = QLineEdit(str(self.custom_w))
        self.height_input = QLineEdit(str(self.custom_h))
        for w in (self.width_input, self.height_input):
            w.setFixedWidth(70)
            w.editingFinished.connect(self.custom_resolution_changed)

        # hide these initially
        self.width_input.setVisible(False)
        self.height_input.setVisible(False)
        self.width_label.setVisible(False)
        self.height_label.setVisible(False)

        # --- Edge tolerance controls ---
        self.edge_slider = QSlider(Qt.Orientation.Horizontal)
        self.edge_slider.setMinimum(0)
        self.edge_slider.setMaximum(100)
        self.edge_slider.setValue(self.edge_tolerance)
        self.edge_slider.valueChanged.connect(self.update_edge_tolerance)

        self.edge_spin = QSpinBox()
        self.edge_spin.setRange(0, 100)
        self.edge_spin.setValue(self.edge_tolerance)
        self.edge_spin.valueChanged.connect(self.update_edge_tolerance)

        edge_layout = QHBoxLayout()
        edge_layout.addWidget(QLabel("Edge tolerance:"))
        edge_layout.addWidget(self.edge_slider)
        edge_layout.addWidget(self.edge_spin)

        # --- Layouts ---
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.render_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.resolution_combo)
        button_layout.addWidget(self.width_label)
        button_layout.addWidget(self.width_input)
        button_layout.addWidget(self.height_label)
        button_layout.addWidget(self.height_input)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.input_label)
        main_layout.addWidget(self.output_label)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(edge_layout)
        layout.addLayout(main_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setStatusBar(QStatusBar())

    # -------------------------------
    # GUI logic
    # -------------------------------

    def change_resolution(self, text):
        """Handle preset dropdown change and show/hide custom inputs."""
        options = {
            "1080p (1920x1080)": (1920, 1080),
            "1440p (2560x1440)": (2560, 1440),
            "4K (3840x2160)": (3840, 2160)
        }

        is_custom = text == "Custom"

        # Toggle visibility of custom boxes
        self.width_input.setVisible(is_custom)
        self.height_input.setVisible(is_custom)
        self.width_label.setVisible(is_custom)
        self.height_label.setVisible(is_custom)

        if not is_custom:
            self.upscale_width, self.upscale_height = options[text]
            self.statusBar().showMessage(f"Resolution set to {text}")
        else:
            # Restore previously entered custom values
            self.width_input.setText(str(self.custom_w))
            self.height_input.setText(str(self.custom_h))
            self.statusBar().showMessage("Enter custom width and height")

    def custom_resolution_changed(self):
        """When user finishes typing in custom width/height."""
        try:
            w = int(self.width_input.text())
            h = int(self.height_input.text())
            if w > 0 and h > 0:
                self.custom_w, self.custom_h = w, h
                self.upscale_width, self.upscale_height = w, h
                self.statusBar().showMessage(f"Custom resolution: {w}x{h}")
        except ValueError:
            self.statusBar().showMessage("Invalid custom resolution input")

    def update_edge_tolerance(self, value):
        """Synchronize slider and spinbox values."""
        sender = self.sender()
        self.edge_tolerance = value
        if sender == self.edge_slider:
            self.edge_spin.setValue(value)
        elif sender == self.edge_spin:
            self.edge_slider.setValue(value)
        self.statusBar().showMessage(f"Edge tolerance: {value}")

    def load_images(self):
        """Load one or more image files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Images",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if not file_paths:
            return

        self.file_paths = file_paths
        self.statusBar().showMessage(f"Loaded {len(file_paths)} image(s)")
        self.render_btn.setEnabled(True)

        # Show first image preview
        img = Renderer.get_image_from_file(file_paths[0], self.upscale_height, self.upscale_width)
        if img is not None:
            self._show_cv_image(self.input_label, img)

    def render_ascii(self):
        """Render ASCII art for all loaded images."""
        if not self.file_paths:
            return

        self.renders = []
        self.statusBar().showMessage("Rendering images...")

        for path in self.file_paths:
            img = Renderer.get_image_from_file(path, self.upscale_height, self.upscale_width)
            render = Renderer.render_as_ascii(img, edge_tolerance=self.edge_tolerance)
            self.renders.append((path, render))

        if self.renders:
            self._show_cv_image(self.output_label, self.renders[0][1])

        self.statusBar().showMessage(f"Rendered {len(self.renders)} image(s)")
        self.save_btn.setEnabled(True)

    def save_renders(self):
        """Save all rendered ASCII images to a user-chosen folder."""
        if not hasattr(self, "renders") or not self.renders:
            return

        # Open folder selection dialog
        folder = QFileDialog.getExistingDirectory(
            self, "Select folder to save ASCII renders"
        )
        if not folder:
            return  # user cancelled

        for path, render in self.renders:
            base_name = os.path.basename(path)
            name, _ = os.path.splitext(base_name)
            out_path = os.path.join(folder, f"{name}_ascii.png")
            Renderer.save_render(render, out_path)

        self.statusBar().showMessage(f"Saved {len(self.renders)} render(s) to {folder}")

    def _show_cv_image(self, label: QLabel, img):
        """Display OpenCV image in QLabel."""
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        label.setPixmap(pixmap.scaled(
            label.width(), label.height(), Qt.AspectRatioMode.KeepAspectRatio
        ))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AsciiApp()
    window.show()
    sys.exit(app.exec())

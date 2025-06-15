
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout
)
from PyQt6.QtGui import QDoubleValidator, QClipboard
from PyQt6.QtCore import Qt

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J·s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T
DEFAULT_GFACTOR = 2.0023

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(480, 320)
        self.init_ui()

    def init_ui(self):
        # Validators
        freq_validator = QDoubleValidator(0.0, 1000.0, 6)

        # Input fields
        self.bridge_input = QLineEdit()
        self.bridge_input.setPlaceholderText("e.g. 9.5")
        self.bridge_input.setValidator(freq_validator)

        self.if_input = QLineEdit()
        self.if_input.setPlaceholderText("e.g. 0.0")
        self.if_input.setValidator(freq_validator)

        self.gfactor_input = QLineEdit()
        self.gfactor_input.setPlaceholderText("e.g. 2.0023")
        self.gfactor_input.setValidator(QDoubleValidator(0.0, 10.0, 6))

        # Labels
        self.operating_label = QLabel("Operating Frequency: --- GHz")
        self.b0_label = QLabel("B₀: --- T")

        # Buttons
        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        default_g_button = QPushButton("Load Default g-Factor")
        default_g_button.clicked.connect(self.load_default_gfactor)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copy_b0_to_clipboard)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Bridge Frequency (GHz):", self.bridge_input)
        form_layout.addRow("IF Frequency (GHz):", self.if_input)
        form_layout.addRow("g-Factor:", self.gfactor_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(calc_button)
        button_layout.addWidget(default_g_button)

        b0_layout = QHBoxLayout()
        b0_layout.addWidget(self.b0_label)
        b0_layout.addWidget(copy_button)
        b0_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.operating_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(b0_layout)

        self.setLayout(main_layout)

        # Internal storage for copied value
        self.b0_value_tesla = None

    def load_default_gfactor(self):
        self.gfactor_input.setText(str(DEFAULT_GFACTOR))

    def calculate_field(self):
        try:
            bridge_freq = float(self.bridge_input.text())
            if_freq = float(self.if_input.text())
            g = float(self.gfactor_input.text())

            if bridge_freq < 0 or if_freq < 0 or g <= 0:
                raise ValueError("All values must be positive.")

            total_freq_hz = (bridge_freq + if_freq) * 1e9
            B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)

            # Display results
            self.operating_label.setText(
                f"Operating Frequency: {bridge_freq + if_freq:.6f} GHz"
            )
            self.b0_label.setText(f"B₀: {B0_Tesla:.6f} T")

            # Store for copy
            self.b0_value_tesla = B0_Tesla

        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))
            self.b0_label.setText("B₀: --- T")
            self.b0_value_tesla = None

    def copy_b0_to_clipboard(self):
        if self.b0_value_tesla is not None:
            text = f"{self.b0_value_tesla:.6f} T"
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        else:
            QMessageBox.information(self, "No Value", "Please calculate B₀ first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

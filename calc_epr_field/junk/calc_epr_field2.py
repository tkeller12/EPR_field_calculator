
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J·s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T
DEFAULT_GFACTOR = 2.0023

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(450, 300)
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
        self.result_field = QLabel("B₀: --- T / --- G")

        # Buttons
        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        default_g_button = QPushButton("Load Default g-Factor")
        default_g_button.clicked.connect(self.load_default_gfactor)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Bridge Frequency (GHz):", self.bridge_input)
        form_layout.addRow("IF Frequency (GHz):", self.if_input)
        form_layout.addRow("g-Factor:", self.gfactor_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(calc_button)
        button_layout.addWidget(default_g_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.operating_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.result_field, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

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
            B0_Gauss = B0_Tesla * 1e4

            # Display results
            self.operating_label.setText(
                f"Operating Frequency: {bridge_freq + if_freq:.6f} GHz"
            )
            self.result_field.setText(
                f"B₀: {B0_Tesla:.6f} T  ({B0_Gauss:.2f} G)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

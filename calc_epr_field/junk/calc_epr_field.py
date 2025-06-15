import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J·s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(400, 200)
        self.init_ui()

    def init_ui(self):
        # Labels
        freq_label = QLabel("Microwave Frequency (GHz):")
        gfactor_label = QLabel("g-Factor:")
        result_label = QLabel("Magnetic Field B₀ (T & G):")
        self.result_field = QLabel("---")

        # Input fields
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("e.g. 9.5")
        self.freq_input.setValidator(QDoubleValidator(0.0, 1000.0, 6))

        self.gfactor_input = QLineEdit()
        self.gfactor_input.setPlaceholderText("e.g. 2.0023")
        self.gfactor_input.setValidator(QDoubleValidator(0.0, 10.0, 6))

        # Calculate button
        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        # Layouts
        layout = QVBoxLayout()

        freq_layout = QHBoxLayout()
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_input)

        gfactor_layout = QHBoxLayout()
        gfactor_layout.addWidget(gfactor_label)
        gfactor_layout.addWidget(self.gfactor_input)

        result_layout = QHBoxLayout()
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_field)

        layout.addLayout(freq_layout)
        layout.addLayout(gfactor_layout)
        layout.addWidget(calc_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(result_layout)

        self.setLayout(layout)

    def calculate_field(self):
        try:
            freq_ghz = float(self.freq_input.text())
            g = float(self.gfactor_input.text())

            if g <= 0 or freq_ghz <= 0:
                raise ValueError("Inputs must be positive numbers.")

            freq_hz = freq_ghz * 1e9
            B0_Tesla = (PLANCK_CONSTANT * freq_hz) / (g * BOHR_MAGNETON)
            B0_Gauss = B0_Tesla * 1e4

            result_text = f"{B0_Tesla:.6f} T  ({B0_Gauss:.2f} G)"
            self.result_field.setText(result_text)
        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

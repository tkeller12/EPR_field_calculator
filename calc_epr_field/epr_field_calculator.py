import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, QRadioButton, QButtonGroup, QComboBox
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt
import numpy as np

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J·s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T
DEFAULT_GFACTOR = 2.0023
DEFAULT_RATIO = 28.0  # GHz/T, approx. for g ≈ 2.0023

from sim_nitroxide_spectrum import simulate_nitroxide_spectrum

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(520, 420)
        self.init_ui()

    def init_ui(self):
        freq_validator = QDoubleValidator(0.0, 1000.0, 6)

        # Inputs
        self.bridge_input = QLineEdit()
        self.bridge_input.setPlaceholderText("e.g. 9.5")
        self.bridge_input.setValidator(freq_validator)

        self.if_input = QLineEdit()
        self.if_input.setPlaceholderText("e.g. 0.0")
        self.if_input.setValidator(freq_validator)

        self.gfactor_input = QLineEdit()
        self.gfactor_input.setPlaceholderText("e.g. 2.0023")
        self.gfactor_input.setValidator(QDoubleValidator(0.0, 10.0, 6))

        self.ratio_input = QLineEdit()
        self.ratio_input.setPlaceholderText("e.g. 28.0")
        self.ratio_input.setValidator(QDoubleValidator(0.0, 100.0, 6))
        self.ratio_input.setText(str(DEFAULT_RATIO))

        # Radical selector
        self.radical_selector = QComboBox()
        self.radical_selector.addItems(["g = 2", "Nitroxide"])

        # Mode selection
        self.radio_gfactor = QRadioButton("Use g-Factor")
        self.radio_ratio = QRadioButton("Use Field-to-Frequency Ratio (GHz/T)")
        self.radio_sim = QRadioButton("Use Simulation")
        self.radio_gfactor.setChecked(True)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_gfactor)
        self.mode_group.addButton(self.radio_ratio)
        self.mode_group.addButton(self.radio_sim)

        # Labels
        self.operating_label = QLabel("Operating Frequency: --- GHz")
        self.b0_label = QLabel("B₀: --- T")

        # Buttons
        specman_button = QPushButton("Load from SpecMan")
        specman_button.clicked.connect(self.load_from_specman)

        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        default_g_button = QPushButton("Load Default g-Factor")
        default_g_button.clicked.connect(self.load_default_gfactor)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copy_b0_to_clipboard)

        send_specman_button = QPushButton("Send Field to SpecMan")
        send_specman_button.clicked.connect(self.send_field_to_specman)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Bridge Frequency (GHz):", self.bridge_input)
        form_layout.addRow("IF Frequency (GHz):", self.if_input)
        form_layout.addRow("g-Factor:", self.gfactor_input)
        form_layout.addRow("Field-to-Frequency Ratio (GHz/T):", self.ratio_input)
        form_layout.addRow("Radical:", self.radical_selector)

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.radio_gfactor)
        mode_layout.addWidget(self.radio_ratio)
        mode_layout.addWidget(self.radio_sim)

        button_layout = QHBoxLayout()
        button_layout.addWidget(calc_button)
        button_layout.addWidget(default_g_button)

        b0_layout = QHBoxLayout()
        b0_layout.addWidget(self.b0_label)
        b0_layout.addWidget(copy_button)
        b0_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(specman_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(mode_layout)
        main_layout.addWidget(self.operating_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(b0_layout)
        main_layout.addWidget(send_specman_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)
        self.b0_value_tesla = None

    def load_default_gfactor(self):
        self.gfactor_input.setText(str(DEFAULT_GFACTOR))

    def calculate_field(self):
        try:
            bridge_freq = float(self.bridge_input.text())
            if_freq = float(self.if_input.text())
            freq_ghz = bridge_freq + if_freq
            total_freq_hz = freq_ghz * 1e9

            if freq_ghz <= 0:
                raise ValueError("Total frequency must be positive.")

            self.operating_label.setText(f"Operating Frequency: {freq_ghz:.6f} GHz")

            if self.radio_gfactor.isChecked():
                g = float(self.gfactor_input.text())
                if g <= 0:
                    raise ValueError("g-factor must be positive.")
                B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)
            elif self.radio_ratio.isChecked():
                ratio = float(self.ratio_input.text())
                if ratio <= 0:
                    raise ValueError("Field-to-frequency ratio must be positive.")
                B0_Tesla = freq_ghz / ratio
            elif self.radio_sim.isChecked():
                if self.radical_selector.currentText() == "Nitroxide":
                    B, spectrum = simulate_nitroxide_spectrum(total_freq_hz)
                    B0_Tesla = B[np.argmax(spectrum)]
                else:
                    g = 2.0026
                    B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)
            else:
                raise ValueError("No mode selected.")

            self.b0_label.setText(f"B₀: {B0_Tesla:.6f} T")
            self.b0_value_tesla = B0_Tesla

        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))
            self.b0_label.setText("B₀: --- T")
            self.b0_value_tesla = None

    def copy_b0_to_clipboard(self):
        if self.b0_value_tesla is not None:
            text = f"{self.b0_value_tesla:.6f} T"
            QApplication.clipboard().setText(text)
        else:
            QMessageBox.information(self, "No Value", "Please calculate B₀ first.")

    def load_from_specman(self):
        self.bridge_input.setText("9.5")
        self.if_input.setText("0.5")
        # TODO: Add actual SpecMan integration logic here.
        print("Loaded placeholder values from SpecMan (9.5 GHz + 0.5 GHz).")

    def send_field_to_specman(self):
        if self.b0_value_tesla is not None:
            print(f"Sending B₀ = {self.b0_value_tesla:.6f} T to SpecMan...")
            # TODO: Add actual integration with SpecMan API or communication protocol here.
        else:
            QMessageBox.information(self, "No Value", "Please calculate B₀ before sending to SpecMan.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

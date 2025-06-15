import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, QRadioButton, QButtonGroup, QComboBox
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J·s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T
DEFAULT_GFACTOR = 2.0023
DEFAULT_RATIO = 28.0  # GHz/T, approx. for g ≈ 2.0023

def simulate_nitroxide_spectrum(frequency_hz):
    # Dummy simulation, returns a Gaussian centered around 1.2 T
    B = np.linspace(1.1, 1.3, 1000)
    spectrum = np.exp(-((B - 1.2) ** 2) / (2 * (0.01 ** 2)))
    return B, spectrum

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(600, 600)
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

        self.sweep_width_input = QLineEdit()
        self.sweep_width_input.setPlaceholderText("e.g. 0.03")
        self.sweep_width_input.setValidator(QDoubleValidator(0.0, 10.0, 6))
        self.sweep_width_input.setText("0.03")

        self.nutation_bw_input = QLineEdit()
        self.nutation_bw_input.setPlaceholderText("e.g. 800")
        self.nutation_bw_input.setValidator(QDoubleValidator(0.0, 5000.0, 2))
        self.nutation_bw_input.setText("800")

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
        self.sweep_range_label = QLabel("Field Sweep Range: ---")
        self.nutation_freq_label = QLabel("Frequency Range: ---")
        self.nutation_field_label = QLabel("Field Range: ---")

        # Buttons
        specman_button = QPushButton("Load from SpecMan")
        specman_button.clicked.connect(self.load_from_specman)

        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        default_g_button = QPushButton("Load Default g-Factor")
        default_g_button.clicked.connect(self.load_default_gfactor)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copy_b0_to_clipboard)

        copy_range_button = QPushButton("Copy Range")
        copy_range_button.clicked.connect(self.copy_range_to_clipboard)

        copy_nutation_button = QPushButton("Copy Nutation Info")
        copy_nutation_button.clicked.connect(self.copy_nutation_to_clipboard)

        send_specman_button = QPushButton("Send Field to SpecMan")
        send_specman_button.clicked.connect(self.send_field_to_specman)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Bridge Frequency (GHz):", self.bridge_input)
        form_layout.addRow("IF Frequency (GHz):", self.if_input)
        form_layout.addRow("g-Factor:", self.gfactor_input)
        form_layout.addRow("Field-to-Frequency Ratio (GHz/T):", self.ratio_input)
        form_layout.addRow("Radical:", self.radical_selector)
        form_layout.addRow("Field Sweep Width (T):", self.sweep_width_input)
        form_layout.addRow("Nutation Bandwidth (MHz):", self.nutation_bw_input)

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

        sweep_layout = QHBoxLayout()
        sweep_layout.addWidget(self.sweep_range_label)
        sweep_layout.addWidget(copy_range_button)

        nutation_layout = QVBoxLayout()
        nutation_layout.addWidget(self.nutation_freq_label)
        nutation_layout.addWidget(self.nutation_field_label)
        nutation_layout.addWidget(copy_nutation_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(specman_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(mode_layout)
        main_layout.addWidget(self.operating_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(b0_layout)
        main_layout.addLayout(sweep_layout)
        main_layout.addLayout(nutation_layout)
        main_layout.addWidget(send_specman_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)
        self.b0_value_tesla = None
        self.freq_ghz = None

    def load_default_gfactor(self):
        self.gfactor_input.setText(str(DEFAULT_GFACTOR))

    def calculate_field(self):
        try:
            bridge_freq = float(self.bridge_input.text())
            if_freq = float(self.if_input.text())
            freq_ghz = bridge_freq + if_freq
            self.freq_ghz = freq_ghz
            total_freq_hz = freq_ghz * 1e9

            if freq_ghz <= 0:
                raise ValueError("Total frequency must be positive.")

            self.operating_label.setText(f"Operating Frequency: {freq_ghz:.6f} GHz")

            if self.radio_gfactor.isChecked():
                g = float(self.gfactor_input.text())
                B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)
            elif self.radio_ratio.isChecked():
                ratio = float(self.ratio_input.text())
                B0_Tesla = freq_ghz / ratio
            else:
                if self.radical_selector.currentText() == "Nitroxide":
                    B, spectrum = simulate_nitroxide_spectrum(total_freq_hz)
                    B0_Tesla = B[np.argmax(spectrum)]
                else:
                    g = 2.0026
                    B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)

            self.b0_value_tesla = B0_Tesla
            self.b0_label.setText(f"B₀: {B0_Tesla:.6f} T")

            # Sweep range
            sweep_width = float(self.sweep_width_input.text())
            sweep_start = B0_Tesla - sweep_width / 2
            sweep_end = B0_Tesla + sweep_width / 2
            self.sweep_range_label.setText(f"Field Sweep Range: {sweep_start:.4f} T to {sweep_end:.4f} T")

            # Nutation bandwidth output
            nut_bw_mhz = float(self.nutation_bw_input.text())
            freq_start = freq_ghz - nut_bw_mhz / 2000
            freq_end = freq_ghz + nut_bw_mhz / 2000
            field_start = sweep_start
            field_end = sweep_end
            self.nutation_freq_label.setText(f"Frequency Range: {freq_start:.4f} GHz to {freq_end:.4f} GHz")
            self.nutation_field_label.setText(f"Field Range: {field_start:.4f} T to {field_end:.4f} T")

        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))

    def copy_b0_to_clipboard(self):
        if self.b0_value_tesla is not None:
            QApplication.clipboard().setText(f"{self.b0_value_tesla:.6f} T")

    def copy_range_to_clipboard(self):
        try:
            sweep_width = float(self.sweep_width_input.text())
            start = self.b0_value_tesla - sweep_width / 2
            end = self.b0_value_tesla + sweep_width / 2
            QApplication.clipboard().setText(f"{start:.4f} T to {end:.4f} T")
        except:
            pass

    def copy_nutation_to_clipboard(self):
        try:
            nut_bw_mhz = float(self.nutation_bw_input.text())
            freq_start = self.freq_ghz - nut_bw_mhz / 2000
            freq_end = self.freq_ghz + nut_bw_mhz / 2000
            sweep_width = float(self.sweep_width_input.text())
            field_start = self.b0_value_tesla - sweep_width / 2
            field_end = self.b0_value_tesla + sweep_width / 2
            text = f"{freq_start:.4f} GHz to {freq_end:.4f} GHz\n{field_start:.4f} T to {field_end:.4f} T"
            QApplication.clipboard().setText(text)
        except:
            pass

    def load_from_specman(self):
        self.bridge_input.setText("9.5")
        self.if_input.setText("0.5")

    def send_field_to_specman(self):
        if self.b0_value_tesla is not None:
            print(f"Sending B₀ = {self.b0_value_tesla:.6f} T to SpecMan...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

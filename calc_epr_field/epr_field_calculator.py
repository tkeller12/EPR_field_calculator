import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, QRadioButton, QButtonGroup, QComboBox
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt
import numpy as np

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34      # in J\u00b7s
BOHR_MAGNETON = 9.2740100783e-24      # in J/T
DEFAULT_GFACTOR = 2.0023
DEFAULT_RATIO = 28.0  # GHz/T, approx. for g \u2248 2.0023
DEFAULT_NUTATION_BANDWIDTH = 800.0  # MHz

#def simulate_nitroxide_spectrum(freq_hz):
#    B = np.linspace(1.1, 1.3, 1000)
#    spectrum = np.exp(-((B - 1.2)**2) / 0.0005)
#    return B, spectrum

from sim_nitroxide_spectrum import simulate_nitroxide_spectrum

class EPRCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPR Field Calculator")
        self.setMinimumSize(520, 600)
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
        self.sweep_width_input.setPlaceholderText("e.g. 30")
        self.sweep_width_input.setValidator(QDoubleValidator(0.0, 100.0, 6))

        self.nutation_bw_input = QLineEdit()
        self.nutation_bw_input.setPlaceholderText("e.g. 800")
        self.nutation_bw_input.setValidator(QDoubleValidator(0.0, 5000.0, 2))
        self.nutation_bw_input.setText(str(DEFAULT_NUTATION_BANDWIDTH))

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
        self.b0_label = QLabel("B\u2080: --- T")
        self.sweep_range_label = QLabel("Field Sweep Range: ---")
        self.nutation_freq_label = QLabel("Nutation Frequency Range: ---")
        self.nutation_field_label = QLabel("Nutation Field Range: ---")

        # Buttons
        specman_button = QPushButton("Load from SpecMan")
        specman_button.clicked.connect(self.load_from_specman)

        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_field)

        default_g_button = QPushButton("Load Default g-Factor")
        default_g_button.clicked.connect(self.load_default_gfactor)

        copy_button = QPushButton("Copy B0")
        copy_button.clicked.connect(self.copy_b0_to_clipboard)

        send_specman_button = QPushButton("Send Field to SpecMan")
        send_specman_button.clicked.connect(self.send_field_to_specman)

        copy_sweep_button = QPushButton("Copy Sweep Range")
        copy_sweep_button.clicked.connect(self.copy_sweep_range)

        copy_nut_freq_button = QPushButton("Copy Nutation Frequency Range")
        copy_nut_freq_button.clicked.connect(self.copy_nutation_freq_range)

        copy_nut_field_button = QPushButton("Copy Nutation Field Range")
        copy_nut_field_button.clicked.connect(self.copy_nutation_field_range)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Bridge Frequency (GHz):", self.bridge_input)
        form_layout.addRow("IF Frequency (GHz):", self.if_input)
        form_layout.addRow("g-Factor:", self.gfactor_input)
        form_layout.addRow("Field-to-Frequency Ratio (GHz/T):", self.ratio_input)
        form_layout.addRow("Radical:", self.radical_selector)
        form_layout.addRow("Sweep Width (mT):", self.sweep_width_input)
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
        sweep_layout.addWidget(copy_sweep_button)

        nut_freq_layout = QHBoxLayout()
        nut_freq_layout.addWidget(self.nutation_freq_label)
        nut_freq_layout.addWidget(copy_nut_freq_button)

        nut_field_layout = QHBoxLayout()
        nut_field_layout.addWidget(self.nutation_field_label)
        nut_field_layout.addWidget(copy_nut_field_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(specman_button)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(mode_layout)
        main_layout.addWidget(self.operating_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(b0_layout)
        main_layout.addLayout(sweep_layout)
        main_layout.addLayout(nut_freq_layout)
        main_layout.addLayout(nut_field_layout)
        main_layout.addWidget(send_specman_button)

        self.setLayout(main_layout)
        self.b0_value_tesla = None
        self.freq_range_text = ""
        self.field_range_text = ""

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
                B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)
            elif self.radio_ratio.isChecked():
                ratio = float(self.ratio_input.text())
                B0_Tesla = freq_ghz / ratio
            elif self.radio_sim.isChecked():
                if self.radical_selector.currentText() == "Nitroxide":
                    B, spectrum = simulate_nitroxide_spectrum(total_freq_hz)
                    B0_Tesla = B[np.argmax(spectrum)]
                else:
                    g = 2.0026
                    B0_Tesla = (PLANCK_CONSTANT * total_freq_hz) / (g * BOHR_MAGNETON)
            else:
                raise ValueError("Select a calculation mode.")

            self.b0_label.setText(f"B\u2080: {B0_Tesla:.6f} T")
            self.b0_value_tesla = B0_Tesla

            # Sweep width output
            sweep_width_mT = float(self.sweep_width_input.text())
            delta_T = sweep_width_mT * 1e-3 / 2.0
            sweep_range = (B0_Tesla - delta_T, B0_Tesla + delta_T)
            self.sweep_range_label.setText(f"Field Sweep Range: {sweep_range[0]:.4f} T to {sweep_range[1]:.4f} T")
            self.sweep_range_text = f"{sweep_range[0]:.4f} T to {sweep_range[1]:.4f} T"

            # Nutation bandwidth output
            nut_bw_mhz = float(self.nutation_bw_input.text())
            nut_delta_freq = nut_bw_mhz / 2.0 / 1000.0  # GHz
            freq_range = (freq_ghz - nut_delta_freq, freq_ghz + nut_delta_freq)
            field_range = (freq_range[0] / DEFAULT_RATIO, freq_range[1] / DEFAULT_RATIO)

            self.nutation_freq_label.setText(f"Nutation Frequency Range: {freq_range[0]:.1f} GHz to {freq_range[1]:.1f} GHz")
            self.nutation_field_label.setText(f"Nutation Field Range: {field_range[0]:.3f} T to {field_range[1]:.3f} T")

            self.freq_range_text = f"{freq_range[0]:.1f} GHz to {freq_range[1]:.1f} GHz"
            self.field_range_text = f"{field_range[0]:.3f} T to {field_range[1]:.3f} T"

        except Exception as e:
            QMessageBox.critical(self, "Input Error", str(e))
            self.b0_label.setText("B\u2080: --- T")
            self.sweep_range_label.setText("Field Sweep Range: ---")
            self.nutation_freq_label.setText("Nutation Frequency Range: ---")
            self.nutation_field_label.setText("Nutation Field Range: ---")

    def copy_b0_to_clipboard(self):
        if self.b0_value_tesla is not None:
            QApplication.clipboard().setText(f"{self.b0_value_tesla:.6f} T")

    def copy_sweep_range(self):
        if self.sweep_range_text:
            QApplication.clipboard().setText(self.sweep_range_text)

    def copy_nutation_freq_range(self):
        if self.freq_range_text:
            QApplication.clipboard().setText(self.freq_range_text)

    def copy_nutation_field_range(self):
        if self.field_range_text:
            QApplication.clipboard().setText(self.field_range_text)

    def load_from_specman(self):
        self.bridge_input.setText("9.5")
        self.if_input.setText("0.5")

    def send_field_to_specman(self):
        if self.b0_value_tesla is not None:
            print(f"Sending B\u2080 = {self.b0_value_tesla:.6f} T to SpecMan...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EPRCalculator()
    window.show()
    sys.exit(app.exec())

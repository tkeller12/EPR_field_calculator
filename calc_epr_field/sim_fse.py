
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Physical constants
mu_B = 9.2740100783e-24  # Bohr magneton (J/T)
h = 6.62607015e-34       # Planck's constant (J·s)

# Experimental parameters
frequency = 9.5e9  # Hz (X-band)
g_iso = 2.006      # Isotropic g-factor for nitroxide
A_iso = 100e6      # Hyperfine coupling in Hz (typical for 14N nitroxide, ~30-40 MHz in mT)

# Magnetic field range (Tesla)
B = np.linspace(0.3, 0.38, 1000)  # around 340 mT

# Central resonance field (T)
B0 = h * frequency / (g_iso * mu_B)

# Convert hyperfine to Tesla
A_T = A_iso * h / mu_B  # Hyperfine splitting in Tesla

# Simulate the 3 transitions (m_I = -1, 0, +1) using Lorentzian lines
def lorentzian(x, x0, width):
    return (width/2)**2 / ((x - x0)**2 + (width/2)**2)

linewidth = 0.0005  # Lorentzian linewidth in Tesla (~0.5 mT)

spectrum = (
    lorentzian(B, B0 - A_T, linewidth) +
    lorentzian(B, B0, linewidth) +
    lorentzian(B, B0 + A_T, linewidth)
)

# Normalize and find peak
spectrum /= np.max(spectrum)
peak_index = np.argmax(spectrum)
B_max = B[peak_index]

# Plot
plt.figure(figsize=(8, 4))
plt.plot(B*1e3, spectrum, label="Simulated EPR Spectrum")
plt.axvline(B_max*1e3, color='r', linestyle='--', label=f"Max @ {B_max*1e3:.2f} mT")
plt.xlabel("Magnetic Field (mT)")
plt.ylabel("Absorption (arb. units)")
plt.title("Nitroxide EPR Spectrum (Simulated, CW-like)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

print(f"Maximum signal occurs at B = {B_max*1e3:.2f} mT")

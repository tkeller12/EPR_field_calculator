import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import physical_constants

def estimate_field_sweep(g_tensor, A_tensor, frequency, margin_mT=5.0, points=1000):
    """
    Estimate magnetic field sweep (Tesla) for nitroxide powder EPR.
    
    Parameters:
        g_tensor: array-like, g-values [gx, gy, gz]
        A_tensor: array-like, A-values [Ax, Ay, Az] in Hz
        frequency: microwave frequency in Hz
        margin_mT: extra sweep margin on each side in mT
        points: number of points in B array
        
    Returns:
        B: np.ndarray of magnetic field values (Tesla)
    """
    # Constants
    mu_B = physical_constants['Bohr magneton'][0]  # J/T
    h = physical_constants['Planck constant'][0]   # J·s
    
    g_min = np.min(g_tensor)
    g_max = np.max(g_tensor)
    A_max = np.max(A_tensor)
    
    # Convert A_max to energy (J)
    A_hz = A_max  # A in Hz
    A_J = A_hz * h
    
    # Calculate field limits
    B_min = (h * frequency - A_J) / (g_max * mu_B)
    B_max = (h * frequency + A_J) / (g_min * mu_B)
    
    # Add margin (in Tesla)
    margin = margin_mT * 1e-3
    B_min -= margin
    B_max += margin
    
    B = np.linspace(B_min, B_max, points)
    return B


# Constants
mu_B = physical_constants['Bohr magneton'][0]  # J/T
h = physical_constants['Planck constant'][0]   # J·s

# EPR parameters
#frequency = 9.5e9  # Hz (X-band)
frequency = 34.e9  # Hz (Q-band)
#frequency = 94.e9  # Hz (Q-band)
g_tensor = np.array([2.009, 2.006, 2.002])  # typical nitroxide g-tensor (x, y, z)
A_tensor = np.array([20e6, 20e6, 100e6])    # Hz (x, y, z), ^14N hyperfine

# Simulation parameters
n_orientations = 10000
#B = np.linspace(0.3, 0.39, 2000)  # Tesla
B = estimate_field_sweep(g_tensor, A_tensor, frequency)

#linewidth = 0.0004  # Tesla (~0.4 mT), Lorentzian linewidth
linewidth = 0.0005  # Tesla (~0.4 mT), Lorentzian linewidth

# Generate uniform orientations over the sphere
phi = 2 * np.pi * np.random.rand(n_orientations)
cos_theta = 2 * np.random.rand(n_orientations) - 1
theta = np.arccos(cos_theta)

# Unit vectors for orientations
n = np.vstack((
    np.sin(theta) * np.cos(phi),
    np.sin(theta) * np.sin(phi),
    np.cos(theta)
)).T

# Allocate spectrum
spectrum = np.zeros_like(B)

# Lorentzian lineshape
def lorentzian(x, x0, width):
    return (width/2)**2 / ((x - x0)**2 + (width/2)**2)

# Loop over orientations
for vec in n:
    # g_eff and A_eff: n^T * tensor * n
    g_eff = np.sqrt(np.sum((g_tensor * vec)**2))
    A_eff = np.sqrt(np.sum((A_tensor * vec)**2))
    
    # Three hyperfine transitions: m_I = -1, 0, +1
    for mI in [-1, 0, +1]:
        resonance_field = (h * frequency - mI * A_eff * h) / (g_eff * mu_B)
        spectrum += lorentzian(B, resonance_field, linewidth)

# Normalize
spectrum /= np.max(spectrum)

# Get field at maximum
B_max = B[np.argmax(spectrum)]

# Plot
plt.figure(figsize=(8, 4))
plt.plot(B * 1e3, spectrum, label="Frozen Solution EPR Spectrum")
plt.axvline(B_max * 1e3, color='red', linestyle='--', label=f'Max @ {B_max*1e3:.2f} mT')
plt.xlabel("Magnetic Field (mT)")
plt.ylabel("Absorption (arb. units)")
plt.title("Simulated Nitroxide EPR Spectrum (Frozen, Orientation Averaged)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

print(f"Maximum signal occurs at B = {B_max*1e3:.2f} mT")

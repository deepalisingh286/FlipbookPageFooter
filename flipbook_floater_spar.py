import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PyPDF2 import PdfMerger


# --------------------------------------------------------
# RANDOM WAVE GENERATOR (Fourier-based)
# --------------------------------------------------------
def generate_wave(x, t, n_modes=5, base_amp=0.05):
    """
    x : array of horizontal coordinates
    t : time index (frame number)
    n_modes : number of Fourier wave modes
    base_amp : overall scaling for wave height
    """
    y = np.zeros_like(x)

    rng = np.random.default_rng(seed=123)  # fixed seeds for reproducibility
    amps = rng.uniform(0.5, 1.0, n_modes) * base_amp
    freqs = rng.uniform(1.0, 3.0, n_modes)
    phases = rng.uniform(0, 2*np.pi, n_modes)
    speeds = rng.uniform(0.05, 0.2, n_modes)

    for A, k, phi, c in zip(amps, freqs, phases, speeds):
        y += A * np.sin(k*x + phi + c * t)

    return y


# --------------------------------------------------------
# Catenary-like mooring line generator
# --------------------------------------------------------
def mooring_curve(x0, y0, x1, y1, sag=0.6, n=100):
    """
    Generates a smooth curved mooring line between:
    (x0, y0) = attachment point on spar
    (x1, y1) = anchor point on seabed
    sag = amount of downward curvature (larger = more sag)
    """
    t = np.linspace(0, 1, n)
    # Quadratic Bezier curve
    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2 - sag     # sag downward
    x = (1-t)**2 * x0 + 2*(1-t)*t * xm + t**2 * x1
    y = (1-t)**2 * y0 + 2*(1-t)*t * ym + t**2 * y1
    return x, y

# --------------------------------------------------------
# Heave (bobbing) motion of floater/turbine
# --------------------------------------------------------
def heave_offset(t, amp=0.15, freq=0.02):
    """
    Returns a vertical offset (meters) for time/frame t.
    amp  = amplitude of heave
    freq = frequency in Hz-equivalent (cycles per frame)
    """
    return amp * np.sin(2 * np.pi * freq * t)

# --------------------------------------------------------
# LOAD BLADE DATA (span, chord, pitch-axis fraction)
# --------------------------------------------------------
data = np.loadtxt("turbinePlanform.dat", skiprows=1)
d1z   = data[:, 0]
d1c   = data[:, 1]
d1pax = data[:, 2]

dR = d1z[-1]     # blade radius
dh = 1.5         # hub height above ground

# --------------------------------------------------------
# FLIPBOOK PARAMETERS
# --------------------------------------------------------
n_frames = 200
daz = 5                        # degrees per frame
az_list = (np.arange(n_frames) * daz) % 360

# Tower geometry (same as MATLAB)
tower_x = 0.04 * np.array([1, 0.7, -0.7, -1])
tower_y = -dh  * np.array([1, 0,    0,     1])

# --------------------------------------------------------
# BUILD SIMPLE NO-SWEEP BLADES
# --------------------------------------------------------
npts = len(d1z)
d2x = np.zeros((2*npts, n_frames))
d2y = np.zeros((2*npts, n_frames))

# Straight leading/trailing edges (no sweep)
d1TE = -d1c * d1pax
d1LE =  d1c * (1 - d1pax)

# Blade = radial direction for x, chord offset for y
x_LE = d1z
x_TE = d1z
y_LE = d1LE
y_TE = d1TE

for i in range(n_frames):
    # Leading edge then trailing edge reversed
    d2x[:, i] = np.concatenate([x_LE, x_TE[::-1]])
    d2y[:, i] = np.concatenate([y_LE, y_TE[::-1]])

# --------------------------------------------------------
# SPAR-BUOY GEOMETRY (simple cylinder)
# --------------------------------------------------------
Rf = 0.1   # radius
Df = 2.8    # draft (below hub line)
Ff = -1.2   # freeboard

spar_x = np.array([-Rf, Rf, Rf, -Rf])
spar_y = np.array([-Df, -Df, Ff, Ff])

# Mooring line attachment points (on spar)
attach1 = (-Rf/2, -Df * 0.7)   # left side, 30% down the draft
attach2 = ( Rf/2, -Df * 0.7)   # right side

# Mooring anchor points on seabed
anchor1 = (-dR, -dh - 0.3 - Df)   # left anchor
anchor2 = ( dR, -dh - 0.3 - Df)   # right anchor


# --------------------------------------------------------
# ROTATION MATRIX FUNCTION
# --------------------------------------------------------
def rot(phi_deg):
    phi = np.radians(phi_deg)
    return np.array([[np.cos(phi),  np.sin(phi)],
                     [-np.sin(phi), np.cos(phi)]])

# --------------------------------------------------------
# DRAW FRAMES
# --------------------------------------------------------
color = np.array([0, 166/255, 214/255]) # bright teal
color = np.array([0, 158, 115]) / 255  # darker teal
frame_files = []

for i in range(n_frames):
    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim([-1.618*dR, dR])
    # ax.set_ylim([-dh, dR])
    ax.set_ylim([-(Df + dh), dR])
    z_heave = heave_offset(i)

    tower_y_shifted = tower_y + z_heave
    spar_y_shifted = spar_y + z_heave
    # Tower
    ax.add_patch(Polygon(np.column_stack([tower_x, tower_y_shifted]),
                         closed=True, color=color))

    # Spar buoy
    ax.add_patch(Polygon(np.column_stack([spar_x, spar_y_shifted]),
                         closed=True, color=color))

    # Hub
    ax.scatter([0], [0 + z_heave], s=20, color=color)

    # 3 blades (120° apart)
    for shift in [-90, 30, -210]:
        Rmat = rot(az_list[i] + shift)
        pt = Rmat @ np.vstack([d2x[:, i], d2y[:, i]])
        pt[1, :] += z_heave 
        ax.add_patch(Polygon(pt.T, closed=True, color=color))

    # Bottom circular cap
    ax.scatter([0], [-2.8 + z_heave], s=100, color=color)

    # # Ground line
    # ax.plot([-1*dR, dR], [-dh, -dh], color=color, linewidth=1)

    # ----- Realistic evolving wave pattern -----
    xwave = np.linspace(-dR, dR, 200)
    ywave = generate_wave(xwave, t=i, n_modes=6, base_amp=0.05)

    # shift wave downward to the correct position (-dh)
    ywave = ywave - dh
    ax.plot(xwave, ywave, color=color, linewidth=1.2)

    # Shift mooring attachment points   
    attach1_shifted = (attach1[0], attach1[1] + z_heave)
    attach2_shifted = (attach2[0], attach2[1] + z_heave)

    # --------- Mooring line 1 ---------
    mx1, my1 = mooring_curve(attach1_shifted[0], attach1_shifted[1],
                            anchor1[0], anchor1[1],
                            sag=0.8)
    ax.plot(mx1, my1, color=color, linewidth=1.2)

    # --------- Mooring line 2 ---------
    mx2, my2 = mooring_curve(attach2_shifted[0], attach2_shifted[1],
                            anchor2[0], anchor2[1],
                            sag=0.8)
    ax.plot(mx2, my2, color=color, linewidth=1.2)

    ax.plot([0, 0], [-2, -4], color=color, linewidth=1)


    fname = f"frame_{i:03d}.pdf"
    fig.savefig(fname, transparent=True)
    plt.close(fig)
    frame_files.append(fname)

# --------------------------------------------------------
# MERGE TO FINAL PDF
# --------------------------------------------------------
merger = PdfMerger()
for f in frame_files:
    merger.append(f)
merger.write("Flipbook_Spar.pdf")
merger.close()

# delete individual frames
import os
for f in frame_files:
    os.remove(f)

print("Created Flipbook_Spar.pdf")

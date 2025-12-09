#!/usr/bin/env python3
# mandelbrot.py
# Author: Han de Jong (han@deptofgrowth.com)
# Date: 2024-06-11

"""
This is an animated Matplotlib implementation of the Mandelbrot fractal.

This code will save a .gif or .mp4 of your fractal to the same folder.
"""

# Imports
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from matplotlib.colors import PowerNorm

# Settings
plt.ion()

# Resolution that we'll use
resolution = 1000       # Number of pixels (increase to make it look better, but also decrease the speed)
max_iter = 600          # Maximum number to run the iteration (needs to increase for higher zoom)
steps = 1000            # Number of frames
colormap = 'plasma'
colornorm_gamma = 0.9   # Makes it look slightly more appealing.

# Starting coordinates for the plot
xmin, xmax, ymin, ymax = -2.0, 0.5, -1.25, 1.25
x_initial_width = xmax - xmin

# Zoom target (here we zoom towards)
xtarget, ytarget = (-0.743643887037151, 0.13182590420533)


# NOTE, these are cool coordinates from to zoom into (From ChatGPT):
# Not sure if the low-precision numbers work.
"""
Seahorse Valley: (-0.743643887037151, 0.13182590420533)
Seahorse tail mini-brot: (-0.7435669, 0.1314023)
Elephant Valley: (0.285, 0.01)
Elephant valley detail: (0.285125, 0.0005)
Triple spiral valley: (-0.088, 0.654)
Needle near main antenna tip: (0.25, 0.0), offset at y=±1e-3
Period-2 bulb cusp: (-1.0, 0.0) with slight offset
Misiurewicz point, Seahorse valley head: (-0.10109636384562, -0.95628651080914)
"""

# Zoom derivatives (how much smaller we make the view each step as a fraction of the previous step)
zoom_fraction = 0.95            # Speed at which we zoom
zoom_speed = 0.05               # Speed at which we move laterally towards the target (defined above)

def mandelbrot(c, max_iter = max_iter):
    """
    Iterate the Mandelbrot function and see if it diverges.
    We use a threshold of 2, which apparently is sufficient.

    NOTE: don't use this any more because the Python loop is much too slow.
    Using Numpy instead inside mandelbrot_set. Left the function here to illustrate
    how the algoritm works.

    """
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z**2 + c
    return max_iter

def mandelbrot_set(xmin, xmax, ymin, ymax, resolution = resolution, max_iter = max_iter):
    """
    Create a Mandelbrot image.
    Parameters:
    xmin, xmax, ymin, ymax : float
        The bounds of the region in the complex plane to compute.
    resolution : int
        The number of points along each axis (image will be resolution x resolution).
    max_iter : int
        The maximum number of iterations.
    """
    X = np.linspace(xmin, xmax, resolution, dtype=np.float64) # The real part
    Y = np.linspace(ymin, ymax, resolution, dtype=np.float64) # The imaginary part
    C = X[None, :] + 1j * Y[:, None]
    Z = np.zeros_like(C)
    still_trying = np.ones_like(C, dtype=bool)
    image = np.zeros_like(C, dtype=np.uint16)

    # This is a Numpy (vectorized) implementation of the algoritm. It works on the complete
    # frame instead of on an individual pixel.
    for i in range(max_iter):
        # Only work on values that are still iterating
        Z[still_trying] = Z[still_trying]*Z[still_trying] + C[still_trying]
        escaped = np.abs(Z) > 2
        image[still_trying & escaped] = i
        still_trying[still_trying & escaped] = False

    # If still trying, set to max_iter
    image[still_trying] = max_iter
    return image

def setup_original_view():
    """
    Make the first version of the plot.
    """

    fig, ax = plt.subplots(figsize=(12,12))
    image = mandelbrot_set(-2, 0.5, -1.25, 1.25)
    norm = PowerNorm(gamma=colornorm_gamma, vmin=0, vmax=max_iter*1.1)
    handle = plt.imshow(image, extent=(-2.0, 0.5, -1.25, 1.25), cmap = colormap,
                        origin='lower', interpolation='nearest', norm = norm)
    plt.axis('off')
    plt.show()

    return fig, handle

def global_update(i):
    """
    Updates the plot
    """
    global xmin, xmax, ymin, ymax, c_time

    # Zoom
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    w  = (xmax - xmin) * zoom_fraction
    h  = (ymax - ymin) * zoom_fraction

    # Get the new coordinates
    xmin, xmax = cx - w/2, cx + w/2
    ymin, ymax = cy - h/2, cy + h/2

    # Calculate the errors and move towards the target
    xerror = (xmax + xmin)/2 - xtarget
    yerror = (ymax + ymin)/2 - ytarget
    xmin -= xerror*zoom_speed
    xmax -= xerror*zoom_speed
    ymin -= yerror*zoom_speed
    ymax -= yerror*zoom_speed

    # Make the new image
    max_iter = adaptive_max_iter(xmax - xmin)
    image = mandelbrot_set(xmin, xmax, ymin, ymax, max_iter=max_iter)
    handle.set_data(image)
    norm = PowerNorm(gamma=colornorm_gamma, vmin=0, vmax=max_iter*1.1)
    handle.set_norm(norm)
    handle.set_extent((xmin, xmax, ymin, ymax))

    # Update
    duration = time.time() - c_time
    c_time = time.time()
    print(f'Step: {i}/{steps}, max_iter: {max_iter}, duration: {duration:.4f}s')
    plt.draw()
    plt.pause(0.001)
    
    return [handle]

def adaptive_max_iter(x_width, base=80, slope=75, cap=5000):
    """
    We need to dynamically update max_iter. This is because
    the differences are smaller if you look at a smaller region.

    I kind-off ballparked this. Might be room to make it more detailed at higher
    zoom levels and faster at lower zoom levels.
    """

    scale = max(x_initial_width / x_width, 1.0)
    k = int(base + slope * np.log2(scale))
    return min(cap, max(50, k))

if __name__ == "__main__":
    
    # Setup the original
    fig, handle = setup_original_view()
    c_time = time.time()

    # Run the animation
    ani = FuncAnimation(fig, global_update, frames=steps, blit=True, interval=100, repeat=False)

    # Pick saving as GIF or mp4
    #ani.save("mandelbrot.gif", writer=PillowWriter(fps=10))
    ani.save("mandelbrot.mp4", writer=FFMpegWriter(fps=25, bitrate=100000))

    # Prevent double running
    print('Done!')
    plt.close(fig)

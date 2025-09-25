import py5
import numpy as np

# Dictionary of mathematical functions that can be used in the fractal calculation
functions = {
    'sin': np.sin, 'sinh': np.sinh, 'cos': np.cos, 'sqrt': np.sqrt,
    'cbrt': np.cbrt, 'tan': np.tan, 'tanh': np.tanh, 'atan': np.arctan,
    'acos': np.arccos, 'ceil': np.ceil, 'floor': np.floor, 'exp': np.exp,
    'log': np.log, 'round': np.round, 'trunc': np.trunc,
}

# Function choices for the Julia set calculation
u_mul1 = np.sin
u_mul2 = np.cosh
v_mul1 = np.cos
v_mul2 = np.sinh
avr_ = np.sqrt
r_ = np.sin

reset_on_change = True

# Global variables
yy = 0  # Current y-coordinate being drawn
a = 1  # Parameter affecting Julia set shape
b = 0.2  # Parameter affecting Julia set shape
maxx = maxy = 0  # Maximum x and y values in the complex plane


def setup():
    global maxx, maxy, yy
    py5.size(1112, 834)  # Set canvas size
    avr = avr_(py5.width * py5.height)  # Calculate average dimension
    # Calculate maximum x and y values for the complex plane mapping
    maxx = (avr / py5.height) * py5.PI
    maxy = (avr / py5.width) * py5.PI
    yy = 0  # Initialize current y-coordinate
    py5.background(0)  # Set background to black


def draw():
    global yy
    if yy < py5.height:
        draw_layer()  # Draw one horizontal line of pixels
    else:
        py5.no_loop()  # Stop drawing when the canvas is filled


def draw_layer():
    global yy
    # Map the current y-coordinate to the complex plane
    y = py5.remap(yy, 0, py5.height, -maxy, maxy)
    for xx in range(py5.width):
        # Map the current x-coordinate to the complex plane
        x = py5.remap(xx, 0, py5.width, -maxx, maxx)
        iter = julia(x, y)  # Calculate Julia set iteration for this point
        # Calculate RGB values based on the iteration count
        r = int((r_(iter / 12)**2) * 256)
        g = int((15000 / (iter + 1)) % 256)
        b = int((25000 / np.log(iter + 2)) % 256)
        py5.stroke(r, g, b)  # Set the stroke color
        py5.line(xx, yy, xx, yy + 1)  # Draw a 1-pixel line
    yy += 1  # Move to the next y-coordinate

# Creating a new complex function based on compositions of trigonometric and hyperbolic functions.


def julia(x, y):
    for iter in range(100):  # Maximum of 100 iterations
        # Apply the Julia set transformation
        u = u_mul1(x) * u_mul2(y)
        v = v_mul1(x) * v_mul2(y)
        x = a * u - b * v * 4
        y = b * u + a * v / 1.4
        if abs(y) > 50:  # Check if the point has "escaped"
            return iter
    return 0  # Return 0 if the point never "escapes"


def key_pressed():
    if py5.key == 'r':
        # Save the current frame as an image with a timestamp
        timestamp = f"{py5.month():02d}-{py5.day():02d}_{py5.hour():02d}-{py5.minute():02d}-{py5.second():02d}"
        py5.save_frame(f"img_{timestamp}.jpg")
    elif py5.key == 's':
        global yy
        yy = 0  # Reset the y-coordinate
        py5.background(0)  # Clear the canvas
        py5.loop()  # Restart the drawing loop


py5.run_sketch()  # Run the sketch

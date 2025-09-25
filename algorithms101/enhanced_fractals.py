import py5
import numpy as np
import math
import random
from typing import Tuple, Callable


class FractalRenderer:
    def __init__(self):
        # Canvas settings
        self.width = 1200
        self.height = 900
        self.max_iterations = 256

        # Fractal parameters
        self.zoom = 1.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.julia_c_real = -0.7269
        self.julia_c_imag = 0.1889

        # Current fractal type
        self.fractal_types = [
            "mandelbrot", "julia", "burning_ship", "tricorn",
            "multibrot", "phoenix", "newton", "sierpinski"
        ]
        self.current_fractal = 0

        # Color palettes
        self.color_palettes = [
            "cosmic_fire", "ocean_depths", "aurora_borealis", "volcanic_ash",
            "neon_dreams", "forest_mystique", "sunset_gradient", "ice_crystal"
        ]
        self.current_palette = 0

        # Rendering state
        self.current_row = 0
        self.is_rendering = False
        self.render_complete = False

        # Animation parameters
        self.animate_julia = False
        self.animation_time = 0.0
        self.animation_speed = 0.02

        # Advanced parameters
        self.power = 2.0  # For multibrot sets
        self.escape_radius = 4.0
        self.color_shift = 0.0
        self.color_intensity = 1.0

    def settings(self):
        py5.size(self.width, self.height)

    def setup(self):
        py5.color_mode(py5.RGB, 255)
        py5.background(0)
        self.start_rendering()

        print("🌌 Enhanced Fractal Generator")
        print("=" * 50)
        print("Controls:")
        print("  SPACE: Change fractal type")
        print("  C: Change color palette")
        print("  R: Re-render current fractal")
        print("  S: Save current fractal")
        print("  A: Toggle Julia set animation")
        print("  +/-: Zoom in/out")
        print("  Arrow keys: Pan view")
        print("  1-8: Select specific fractal")
        print("  Mouse: Click to center view")
        print("  I/O: Increase/decrease iterations")
        print("  P/L: Increase/decrease power (multibrot)")
        print("=" * 50)

    def draw(self):
        if self.animate_julia and self.fractal_types[self.current_fractal] == "julia":
            self.animation_time += self.animation_speed
            self.julia_c_real = 0.7885 * py5.cos(self.animation_time)
            self.julia_c_imag = 0.7885 * py5.sin(self.animation_time)
            self.start_rendering()

        if self.is_rendering and not self.render_complete:
            self.render_progressive()

        self.draw_ui()

    def start_rendering(self):
        """Start or restart the fractal rendering process"""
        self.current_row = 0
        self.is_rendering = True
        self.render_complete = False
        py5.background(0)

    def render_progressive(self):
        """Render the fractal progressively, one row at a time"""
        if self.current_row >= self.height:
            self.render_complete = True
            self.is_rendering = False
            return

        # Render multiple rows per frame for better performance
        rows_per_frame = max(1, self.height // 100)

        for _ in range(rows_per_frame):
            if self.current_row >= self.height:
                break

            self.render_row(self.current_row)
            self.current_row += 1

    def render_row(self, row: int):
        """Render a single row of the fractal"""
        fractal_func = self.get_fractal_function()

        for col in range(self.width):
            # Map pixel coordinates to complex plane
            x, y = self.pixel_to_complex(col, row)

            # Calculate fractal value
            iterations = fractal_func(x, y)

            # Apply coloring
            color = self.get_color(iterations, x, y)

            # Draw pixel
            py5.stroke(*color)
            py5.point(col, row)

    def pixel_to_complex(self, px: int, py: int) -> Tuple[float, float]:
        """Convert pixel coordinates to complex plane coordinates"""
        # Calculate the range based on zoom and center
        range_x = 4.0 / self.zoom
        range_y = 3.0 / self.zoom

        # Map pixel to complex coordinates
        real = self.center_x + (px - self.width/2) * range_x / self.width
        imag = self.center_y + (py - self.height/2) * range_y / self.height

        return real, imag

    def get_fractal_function(self) -> Callable:
        """Get the fractal calculation function for the current fractal type"""
        fractal_name = self.fractal_types[self.current_fractal]

        if fractal_name == "mandelbrot":
            return self.mandelbrot
        elif fractal_name == "julia":
            return self.julia
        elif fractal_name == "burning_ship":
            return self.burning_ship
        elif fractal_name == "tricorn":
            return self.tricorn
        elif fractal_name == "multibrot":
            return self.multibrot
        elif fractal_name == "phoenix":
            return self.phoenix
        elif fractal_name == "newton":
            return self.newton
        elif fractal_name == "sierpinski":
            return self.sierpinski
        else:
            return self.mandelbrot

    def mandelbrot(self, x: float, y: float) -> int:
        """Calculate Mandelbrot set iterations"""
        c = complex(x, y)
        z = complex(0, 0)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z = z**self.power + c

        return self.max_iterations

    def julia(self, x: float, y: float) -> int:
        """Calculate Julia set iterations"""
        z = complex(x, y)
        c = complex(self.julia_c_real, self.julia_c_imag)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z = z**self.power + c

        return self.max_iterations

    def burning_ship(self, x: float, y: float) -> int:
        """Calculate Burning Ship fractal iterations"""
        c = complex(x, y)
        z = complex(0, 0)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z = complex(abs(z.real), abs(z.imag))**self.power + c

        return self.max_iterations

    def tricorn(self, x: float, y: float) -> int:
        """Calculate Tricorn (Mandelbar) fractal iterations"""
        c = complex(x, y)
        z = complex(0, 0)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z = z.conjugate()**self.power + c

        return self.max_iterations

    def multibrot(self, x: float, y: float) -> int:
        """Calculate Multibrot set with variable power"""
        c = complex(x, y)
        z = complex(0, 0)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z = z**self.power + c

        return self.max_iterations

    def phoenix(self, x: float, y: float) -> int:
        """Calculate Phoenix fractal iterations"""
        z = complex(x, y)
        z_prev = complex(0, 0)
        c = complex(0.5667, 0.0)
        p = complex(-0.5, 0.0)

        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                return i
            z_new = z**2 + c + p * z_prev
            z_prev = z
            z = z_new

        return self.max_iterations

    def newton(self, x: float, y: float) -> int:
        """Calculate Newton fractal iterations (z^3 - 1 = 0)"""
        z = complex(x, y)
        tolerance = 1e-6

        # Roots of z^3 - 1 = 0
        roots = [
            complex(1, 0),
            complex(-0.5, math.sqrt(3)/2),
            complex(-0.5, -math.sqrt(3)/2)
        ]

        for i in range(self.max_iterations):
            # Newton's method: z = z - f(z)/f'(z)
            # For f(z) = z^3 - 1, f'(z) = 3z^2
            if abs(z) < tolerance:
                return i

            z_cubed = z**3
            if abs(z_cubed) < tolerance:
                return i

            z = z - (z_cubed - 1) / (3 * z**2)

            # Check convergence to roots
            for j, root in enumerate(roots):
                if abs(z - root) < tolerance:
                    return i + j * 85  # Different colors for different roots

        return self.max_iterations

    def sierpinski(self, x: float, y: float) -> int:
        """Calculate Sierpinski carpet-like fractal"""
        # Scale and translate coordinates
        x = (x + 2) * 3
        y = (y + 1.5) * 3

        iterations = 0

        while iterations < self.max_iterations and x > 0 and y > 0 and x < 3 and y < 3:
            # Check if point is in the "hole" of current level
            x_mod = x % 1
            y_mod = y % 1

            if 0.33 < x_mod < 0.66 and 0.33 < y_mod < 0.66:
                return iterations

            x *= 3
            y *= 3
            iterations += 1

        return self.max_iterations

    def get_color(self, iterations: int, x: float, y: float) -> Tuple[int, int, int]:
        """Generate color based on iterations and current palette"""
        if iterations >= self.max_iterations:
            return (0, 0, 0)  # Black for points in the set

        palette_name = self.color_palettes[self.current_palette]

        # Normalize iterations
        t = (iterations + self.color_shift) / self.max_iterations
        t = (t * self.color_intensity) % 1.0

        if palette_name == "cosmic_fire":
            return self.cosmic_fire_palette(t, iterations)
        elif palette_name == "ocean_depths":
            return self.ocean_depths_palette(t, iterations)
        elif palette_name == "aurora_borealis":
            return self.aurora_borealis_palette(t, iterations)
        elif palette_name == "volcanic_ash":
            return self.volcanic_ash_palette(t, iterations)
        elif palette_name == "neon_dreams":
            return self.neon_dreams_palette(t, iterations)
        elif palette_name == "forest_mystique":
            return self.forest_mystique_palette(t, iterations)
        elif palette_name == "sunset_gradient":
            return self.sunset_gradient_palette(t, iterations)
        elif palette_name == "ice_crystal":
            return self.ice_crystal_palette(t, iterations)
        else:
            return self.cosmic_fire_palette(t, iterations)

    def cosmic_fire_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Cosmic fire color palette with deep reds, oranges, and yellows"""
        r = int(255 * (0.5 + 0.5 * math.sin(t * math.pi * 3)))
        g = int(255 * (t**0.5) * (0.7 + 0.3 * math.sin(t * math.pi * 5)))
        b = int(255 * (t**2) * (0.3 + 0.7 * math.sin(t * math.pi * 7)))
        return (r, g, b)

    def ocean_depths_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Ocean depths palette with blues, teals, and deep greens"""
        r = int(255 * (t**3) * (0.2 + 0.3 * math.sin(t * math.pi * 4)))
        g = int(255 * (0.3 + 0.7 * t) * (0.6 + 0.4 * math.sin(t * math.pi * 6)))
        b = int(255 * (0.7 + 0.3 * math.sin(t * math.pi * 2)))
        return (r, g, b)

    def aurora_borealis_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Aurora borealis palette with greens, purples, and blues"""
        r = int(255 * (0.4 + 0.6 * math.sin(t * math.pi * 8)) * (t**0.7))
        g = int(255 * (0.6 + 0.4 * math.sin(t * math.pi * 3)))
        b = int(255 * (0.5 + 0.5 * math.sin(t * math.pi * 5)) * (0.7 + 0.3 * t))
        return (r, g, b)

    def volcanic_ash_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Volcanic ash palette with grays, reds, and oranges"""
        base_gray = 0.3 + 0.4 * t
        r = int(255 * (base_gray + 0.3 * math.sin(t * math.pi * 4)))
        g = int(255 * (base_gray * 0.7 + 0.2 * math.sin(t * math.pi * 6)))
        b = int(255 * (base_gray * 0.5 + 0.1 * math.sin(t * math.pi * 8)))
        return (r, g, b)

    def neon_dreams_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Neon dreams palette with bright, saturated colors"""
        r = int(255 * abs(math.sin(t * math.pi * 7)))
        g = int(255 * abs(math.sin(t * math.pi * 5 + math.pi/3)))
        b = int(255 * abs(math.sin(t * math.pi * 3 + 2*math.pi/3)))
        return (r, g, b)

    def forest_mystique_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Forest mystique palette with greens, browns, and golds"""
        r = int(255 * (0.2 + 0.3 * t) * (0.8 + 0.2 * math.sin(t * math.pi * 6)))
        g = int(255 * (0.4 + 0.6 * t) * (0.7 + 0.3 * math.sin(t * math.pi * 4)))
        b = int(255 * (0.1 + 0.2 * t) * (0.6 + 0.4 * math.sin(t * math.pi * 8)))
        return (r, g, b)

    def sunset_gradient_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Sunset gradient palette with warm colors"""
        r = int(255 * (0.8 + 0.2 * math.sin(t * math.pi * 2)))
        g = int(255 * (0.3 + 0.5 * t) * (0.7 + 0.3 * math.sin(t * math.pi * 4)))
        b = int(255 * (t**2) * (0.5 + 0.5 * math.sin(t * math.pi * 6)))
        return (r, g, b)

    def ice_crystal_palette(self, t: float, iterations: int) -> Tuple[int, int, int]:
        """Ice crystal palette with cool blues and whites"""
        base = 0.6 + 0.4 * t
        r = int(255 * base * (0.8 + 0.2 * math.sin(t * math.pi * 8)))
        g = int(255 * base * (0.9 + 0.1 * math.sin(t * math.pi * 6)))
        b = int(255 * (0.9 + 0.1 * math.sin(t * math.pi * 4)))
        return (r, g, b)

    def draw_ui(self):
        """Draw user interface information"""
        # py5.fill(255, 255, 255, 200)
        # py5.no_stroke()
        # py5.rect(10, 10, 300, 120, 5)

        # py5.fill(0)
        # py5.text_size(14)
        # py5.text(f"Fractal: {self.fractal_types[self.current_fractal].title()}", 20, 30)
        # py5.text(f"Palette: {self.color_palettes[self.current_palette].replace('_', ' ').title()}", 20, 50)
        # py5.text(f"Zoom: {self.zoom:.2f}x", 20, 70)
        # py5.text(f"Iterations: {self.max_iterations}", 20, 90)
        # py5.text(f"Power: {self.power:.1f}", 20, 110)

        # if self.is_rendering:
        #     progress = (self.current_row / self.height) * 100
        #     py5.text(f"Rendering: {progress:.1f}%", 150, 110)

    def key_pressed(self):
        """Handle keyboard input"""
        if py5.key == ' ':
            self.current_fractal = (
                self.current_fractal + 1) % len(self.fractal_types)
            self.start_rendering()
            print(
                f"Switched to: {self.fractal_types[self.current_fractal].title()}")

        elif py5.key == 'c' or py5.key == 'C':
            self.current_palette = (
                self.current_palette + 1) % len(self.color_palettes)
            self.start_rendering()
            print(
                f"Switched to: {self.color_palettes[self.current_palette].replace('_', ' ').title()}")

        elif py5.key == 'r' or py5.key == 'R':
            self.start_rendering()
            print("Re-rendering fractal...")

        elif py5.key == 's' or py5.key == 'S':
            timestamp = f"{py5.month():02d}-{py5.day():02d}_{py5.hour():02d}-{py5.minute():02d}-{py5.second():02d}"
            filename = f"fractal_{self.fractal_types[self.current_fractal]}_{self.color_palettes[self.current_palette]}_{timestamp}.png"
            py5.save_frame(filename)
            print(f"Saved: {filename}")

        elif py5.key == 'a' or py5.key == 'A':
            self.animate_julia = not self.animate_julia
            print(f"Julia animation: {'ON' if self.animate_julia else 'OFF'}")

        elif py5.key == '+' or py5.key == '=':
            self.zoom *= 1.5
            self.start_rendering()
            print(f"Zoomed in: {self.zoom:.2f}x")

        elif py5.key == '-' or py5.key == '_':
            self.zoom /= 1.5
            self.start_rendering()
            print(f"Zoomed out: {self.zoom:.2f}x")

        elif py5.key == 'i' or py5.key == 'I':
            self.max_iterations = min(1000, self.max_iterations + 50)
            self.start_rendering()
            print(f"Iterations: {self.max_iterations}")

        elif py5.key == 'o' or py5.key == 'O':
            self.max_iterations = max(50, self.max_iterations - 50)
            self.start_rendering()
            print(f"Iterations: {self.max_iterations}")

        elif py5.key == 'p' or py5.key == 'P':
            self.power = min(10.0, self.power + 0.5)
            self.start_rendering()
            print(f"Power: {self.power:.1f}")

        elif py5.key == 'l' or py5.key == 'L':
            self.power = max(1.0, self.power - 0.5)
            self.start_rendering()
            print(f"Power: {self.power:.1f}")

        # Direct fractal selection
        elif py5.key in '12345678':
            fractal_index = int(py5.key) - 1
            if fractal_index < len(self.fractal_types):
                self.current_fractal = fractal_index
                self.start_rendering()
                print(
                    f"Selected: {self.fractal_types[self.current_fractal].title()}")

    def key_pressed_special(self):
        """Handle special key input (arrow keys)"""
        pan_amount = 0.1 / self.zoom

        if py5.key_code == py5.UP:
            self.center_y -= pan_amount
            self.start_rendering()
        elif py5.key_code == py5.DOWN:
            self.center_y += pan_amount
            self.start_rendering()
        elif py5.key_code == py5.LEFT:
            self.center_x -= pan_amount
            self.start_rendering()
        elif py5.key_code == py5.RIGHT:
            self.center_x += pan_amount
            self.start_rendering()

    def mouse_pressed(self):
        """Handle mouse clicks for centering view"""
        if py5.mouse_x > 0 and py5.mouse_x < self.width and py5.mouse_y > 0 and py5.mouse_y < self.height:
            # Convert mouse position to complex coordinates
            new_center_x, new_center_y = self.pixel_to_complex(
                py5.mouse_x, py5.mouse_y)
            self.center_x = new_center_x
            self.center_y = new_center_y
            self.start_rendering()
            print(f"Centered at: ({new_center_x:.4f}, {new_center_y:.4f})")


# Global fractal renderer instance
fractal_renderer = FractalRenderer()


def settings():
    fractal_renderer.settings()


def setup():
    fractal_renderer.setup()


def draw():
    fractal_renderer.draw()


def key_pressed():
    if py5.key_code in [py5.UP, py5.DOWN, py5.LEFT, py5.RIGHT]:
        fractal_renderer.key_pressed_special()
    else:
        fractal_renderer.key_pressed()


def mouse_pressed():
    fractal_renderer.mouse_pressed()


if __name__ == "__main__":
    py5.run_sketch()

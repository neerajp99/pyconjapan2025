import py5
import math
import random

# Japanese-inspired Perlin noise textile pattern generator
# Based on traditional Japanese color palettes and organic textures
# Perfect for kimono patterns, obi designs, and modern Japanese fashion

# Traditional Japanese color palette (converted from hex)
japanese_palette = [
    (255, 128, 3),    # Persimmon (Kaki)
    (254, 249, 230),  # Ivory (Zōge-iro)
    (252, 184, 117),  # Apricot (Anzu-iro)
    (31, 130, 173),   # Indigo Blue (Ai-iro)
    (1, 2, 0),        # Sumi Black (Sumi-iro)
    (185, 101, 73)    # Burnt Sienna (Beni-gara)
]

# Additional Japanese-inspired palettes for variety
japanese_palettes = {
    "traditional": [(255, 128, 3), (254, 249, 230), (252, 184, 117), (31, 130, 173), (1, 2, 0), (185, 101, 73)],
    "sakura": [(255, 182, 193), (255, 240, 245), (255, 105, 180), (34, 139, 34), (25, 25, 112), (139, 69, 19)],
    "autumn": [(220, 20, 60), (255, 140, 0), (255, 215, 0), (128, 0, 0), (139, 69, 19), (160, 82, 45)],
    "ocean": [(0, 191, 255), (176, 224, 230), (70, 130, 180), (25, 25, 112), (0, 0, 139), (72, 61, 139)],
    "bamboo": [(154, 205, 50), (240, 255, 240), (107, 142, 35), (85, 107, 47), (34, 139, 34), (0, 100, 0)]
}

# Global variables
tz = 0.0
current_palette_name = "traditional"
current_palette = japanese_palettes[current_palette_name]
canvas_width = 1112
canvas_height = 834
noise_detail_octaves = 3
noise_detail_falloff = 0.5
textile_mode = 0  # 0: flowing, 1: geometric, 2: organic, 3: traditional


class JapaneseTile:
    def __init__(self, x, y, diameter, tx, ty, tz):
        self.position = [x, y]
        self.diameter = diameter
        self.my_tx = tx
        self.my_ty = ty
        self.my_tz = tz
        self.mini_pic = None
        self.resolution_scale = 500.0

    def get_right_color(self, angle):
        """Convert angle (0-360) to interpolated color from Japanese palette"""
        # Normalize angle to 0-360
        angle = angle % 360
        if angle < 0:
            angle += 360

        # Calculate which colors to interpolate between
        sect = angle / 60.0
        sect1 = int(sect)
        tune = sect - sect1
        sect2 = sect1 + 1

        if sect1 >= 6:
            sect1 = sect1 - 6
        if sect2 >= 6:
            sect2 = sect2 - 6

        # Get colors from current palette
        color1 = current_palette[sect1 % len(current_palette)]
        color2 = current_palette[sect2 % len(current_palette)]

        # Interpolate between colors
        red = (1 - tune) * color1[0] + tune * color2[0]
        green = (1 - tune) * color1[1] + tune * color2[1]
        blue = (1 - tune) * color1[2] + tune * color2[2]

        return (int(red), int(green), int(blue))

    def create_mini_pic(self):
        """Generate the Perlin noise texture with Japanese aesthetics"""
        # Use a more efficient drawing approach
        py5.no_stroke()

        # Draw with rectangles for better performance
        step = 2  # Pixel step size for performance

        for i in range(0, canvas_height, step):
            for j in range(0, canvas_width, step):
                # Multi-octave Perlin noise for organic texture
                v0 = py5.noise((j / self.resolution_scale + self.my_tx) * 0.5,
                               (i / self.resolution_scale + self.my_ty) * 0.5,
                               self.my_tz + 50) * 60

                v1 = py5.noise((j / self.resolution_scale + self.my_tx) * 5,
                               (i / self.resolution_scale + self.my_ty) * 5,
                               self.my_tz) * 60

                v2 = py5.noise((j / self.resolution_scale + self.my_tx) * 5,
                               (i / self.resolution_scale + self.my_ty) * 5,
                               self.my_tz + 20) * 60

                # Create swirling pattern (traditional Japanese wave motif)
                w = 360 * (v1 / 1.5 - math.floor(v1 / 1.5))

                # Rotation vector for organic flow
                omega_x = math.cos(math.radians(1.5 * w))
                shift = omega_x * 20

                # Japanese-inspired color calculation
                if textile_mode == 0:  # Flowing
                    base_hue = py5.remap(0.3 * v2 + 0.9 * v0, 0, 60, -60, 420)
                elif textile_mode == 1:  # Geometric
                    base_hue = py5.remap(v1 + v2 * 0.5, 0, 60, 0, 360)
                elif textile_mode == 2:  # Organic
                    base_hue = py5.remap(v0 * 1.2 + v2 * 0.3, 0, 60, -90, 450)
                else:  # Traditional
                    base_hue = py5.remap(v0 + v1 * 0.7, 0, 60, 0, 360)

                final_hue = (360 + 3 * base_hue + shift) % 360
                color = self.get_right_color(final_hue)

                # Apply Japanese aesthetic modifications
                if textile_mode == 3:  # Traditional mode - add subtle texture
                    texture_noise = py5.noise(
                        j * 0.01, i * 0.01, self.my_tz * 0.1)
                    color = (
                        int(color[0] * (0.8 + 0.4 * texture_noise)),
                        int(color[1] * (0.8 + 0.4 * texture_noise)),
                        int(color[2] * (0.8 + 0.4 * texture_noise))
                    )

                # Draw the pixel as a small rectangle
                py5.fill(color[0], color[1], color[2])
                py5.rect(j, i, step, step)


def setup():
    global canvas_width, canvas_height
    py5.size(canvas_width, canvas_height)
    py5.no_stroke()
    py5.color_mode(py5.RGB, 255)
    py5.noise_detail(noise_detail_octaves, noise_detail_falloff)

    print("Japanese Perlin Noise Textile Generator")
    print("Controls:")
    print("- Mouse: Navigate texture space")
    print("- Click: Randomize palette")
    print("- SPACE: Change textile mode")
    print("- C: Change color palette")
    print("- S: Save current pattern")
    print("- R: Reset parameters")


def draw():
    global tz

    py5.background(0)

    # Calculate texture coordinates based on mouse position
    tx = py5.mouse_x / 100.0
    ty = py5.mouse_y / 100.0

    # Create and render the Japanese textile pattern
    tester = JapaneseTile(0, 0, 50, tx, ty, tz)
    tester.create_mini_pic()

    # Draw pattern information overlay
    draw_info_overlay()

    # Animate the texture
    tz += 0.01


def draw_info_overlay():
    """Draw information about current settings"""
    # Semi-transparent background for text
    # py5.fill(0, 0, 0, 150)
    # py5.rect(10, 10, 400, 120)

    # # Text information
    # py5.fill(255, 255, 255)
    # py5.text_size(14)
    # py5.text_align(py5.LEFT)

    # mode_names = ["Flowing", "Geometric", "Organic", "Traditional"]
    # py5.text(f"Japanese Perlin Noise Textile", 20, 30)
    # py5.text(f"Mode: {mode_names[textile_mode]}", 20, 50)
    # py5.text(f"Palette: {current_palette_name.title()}", 20, 70)
    # py5.text(f"Time: {tz:.2f}", 20, 90)
    # py5.text("Mouse to explore • Click for new colors", 20, 110)


def mouse_pressed():
    """Randomize the current palette colors"""
    global current_palette
    new_palette = []
    for _ in range(6):
        new_palette.append((
            int(py5.random(255)),
            int(py5.random(255)),
            int(py5.random(255))
        ))
    current_palette = new_palette
    print("Palette randomized!")


def key_pressed():
    global textile_mode, current_palette_name, current_palette, tz

    if py5.key == ' ':
        textile_mode = (textile_mode + 1) % 4
        mode_names = ["Flowing", "Geometric", "Organic", "Traditional"]
        print(f"Textile mode changed to: {mode_names[textile_mode]}")

    elif py5.key == 'c' or py5.key == 'C':
        palette_names = list(japanese_palettes.keys())
        current_index = palette_names.index(current_palette_name)
        current_palette_name = palette_names[(
            current_index + 1) % len(palette_names)]
        current_palette = japanese_palettes[current_palette_name]
        print(f"Color palette changed to: {current_palette_name}")

    elif py5.key == 's' or py5.key == 'S':
        filename = f"japanese_perlin_{current_palette_name}_{textile_mode}_####.png"
        py5.save_frame(filename)
        print(f"Japanese textile pattern saved as: {filename}")

    elif py5.key == 'r' or py5.key == 'R':
        tz = 0.0
        current_palette_name = "traditional"
        current_palette = japanese_palettes[current_palette_name]
        textile_mode = 0
        print("Parameters reset to defaults")


if __name__ == "__main__":
    py5.run_sketch()

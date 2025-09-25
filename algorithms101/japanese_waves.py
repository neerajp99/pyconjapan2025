import py5
import math
import random

# Japanese-inspired color palettes
# Traditional Japanese colors (darker, more sophisticated)
dark_colors = [
    "#1a1a2e",  # Deep indigo (kon)
    "#16213e",  # Navy blue (kon-ai)
    "#0f3460",  # Deep blue (ai-iro)
    "#533a71",  # Purple (murasaki)
    "#2c5530",  # Forest green (midori)
    "#8b4513",  # Brown (chairo)
    "#2f4f4f",  # Dark slate gray
    "#191970"   # Midnight blue
]

light_colors = [
    "#e6f3ff",  # Pale blue (mizuiro)
    "#f0f8ff",  # Alice blue
    "#e0e6f8",  # Lavender mist
    "#f5f5dc",  # Beige (kinari)
    "#fff8dc",  # Cornsilk (kinu-iro)
    "#faf0e6",  # Linen
    "#f8f8ff",  # Ghost white
    "#fffacd"   # Lemon chiffon
]

# Traditional Japanese background colors
bg_colors = [
    "#fdf5e6",  # Old lace (kinari)
    "#f5f5dc",  # Beige
    "#fff8dc",  # Cornsilk
    "#faf0e6",  # Linen
    "#f0f8ff",  # Alice blue
    "#f8f8ff"   # Ghost white
]

# Japanese accent colors for borders and details
accent_colors = [
    "#8b0000",  # Dark red (aka)
    "#b8860b",  # Dark goldenrod (kin-iro)
    "#2f4f4f",  # Dark slate gray
    "#191970",  # Midnight blue
    "#800080",  # Purple (murasaki)
    "#556b2f"   # Dark olive green
]

# Global variables
bg_color = None
border_color = None
sep = 0.6
num_layers = 3
frame_counter = 0

# Japanese-inspired parameters
wave_intensity = 1.2
layer_opacity_base = 40
stroke_weight_base = 0.8
time_speed = 0.03


def setup():
    py5.size(1200, 600)
    py5.pixel_density(1)
    py5.frame_rate(30)
    regenerate_scene()


def draw():
    global frame_counter
    frame_counter += 1

    # Background with subtle gradient effect
    py5.background(255, 255, 255)
    py5.fill(bg_color)
    py5.no_stroke()
    py5.rect(0, 0, py5.width, py5.height)

    # Add subtle texture overlay for Japanese paper effect
    draw_paper_texture()

    py5.curve_tightness(0.85)  # Slightly tighter curves for more elegant flow

    W = py5.width + 100
    resolution = 1
    steps = 8000
    w_num = 0

    for k in range(num_layers):
        offset_t = k * 0.18  # Slightly more spacing between layers

        # Alternate between dark and light palettes with Japanese aesthetic
        if k % 2 == 1:
            palette = dark_colors
        else:
            palette = light_colors

        # More sophisticated color selection
        color_index = int(
            py5.remap(py5.noise(w_num * 0.3, k * 0.7), 0, 1, 0, len(palette)))
        color_index = py5.constrain(color_index, 0, len(palette) - 1)

        fill_color = py5.color(palette[color_index])
        alpha_value = layer_opacity_base + 25 * k
        fill_color = py5.color(
            palette[color_index] + str(hex(alpha_value))[2:].zfillulia(2))
        py5.fill(fill_color)

        py5.stroke(palette[color_index])
        py5.stroke_weight(stroke_weight_base + 0.15 * k)

        py5.begin_shape()
        previous_j = -1
        is_new_line = True

        for step in range(0, steps + 1, resolution):
            T = step / W / 3
            T = T / sep + offset_t

            _j = step % W
            j = W / 4 + _j

            X = j
            Y = 0
            time_falloff = 1 - T / 5
            wave_size = 5 / time_falloff * wave_intensity

            if _j < previous_j:
                # Close previous wave with Japanese-style ending
                py5.vertex(py5.width + 200, Y + wave_size +
                           5000 / j - py5.height / 4)
                py5.vertex(py5.width + 200, py5.height + 200)
                py5.vertex(-200, py5.height + 200)
                py5.end_shape(py5.CLOSE)
                py5.begin_shape()
                is_new_line = True
                w_num += 1

            previous_j = _j

            # Enhanced wave algorithm with Japanese flow characteristics
            while wave_size < W / 5 / time_falloff:
                A = ((X / wave_size + T + frame_counter * time_speed) %
                     1) * wave_size - wave_size / 2
                deform = 1 - ((A * A) / (wave_size * wave_size)) * 4

                # Add subtle Japanese-style wave modulation
                japanese_modulation = py5.sin(T * 2 + k * 0.5) * 0.1
                deform += japanese_modulation

                C = py5.cos(deform)
                S = py5.sin(deform)

                X += A * C + Y * S - A - 20
                Y = Y * C - A * S

                wave_size /= 0.62  # Slightly different ratio for more organic feel

            final_y = Y + wave_size + 5000 / j - py5.height / 4

            if is_new_line:
                py5.vertex(-200, final_y)
                py5.vertex(X - W / 7, final_y)
                is_new_line = False
            else:
                py5.vertex(X - W / 7, final_y)

        py5.end_shape()

    # Japanese-style border with traditional thickness and color
    draw_japanese_border()

    # Add subtle Japanese design elements
    draw_japanese_accents()


def draw_paper_texture():
    """Add subtle texture to simulate Japanese paper (washi)"""
    py5.push_style()
    py5.no_fill()
    py5.stroke(200, 200, 200, 15)
    py5.stroke_weight(0.5)

    # Create subtle horizontal lines like paper grain
    for i in range(0, py5.height, 8):
        if py5.random(1) > 0.7:  # Random gaps
            py5.line(0, i, py5.width, i + py5.random(-2, 2))

    py5.pop_style()


def draw_japanese_border():
    """Draw border with Japanese aesthetic"""
    py5.push_style()
    py5.no_fill()
    py5.stroke(border_color)
    py5.stroke_weight(12)
    py5.rect(6, 6, py5.width - 12, py5.height - 12)

    # Inner border for depth
    py5.stroke_weight(2)
    py5.stroke(0, 0, 0, 50)
    py5.rect(15, 15, py5.width - 30, py5.height - 30)
    py5.pop_style()


def draw_japanese_accents():
    """Add subtle Japanese design accents"""
    py5.push_style()

    # Corner decorations inspired by Japanese mon (family crests)
    corner_size = 30
    py5.fill(border_color + "3C")  # Add transparency
    py5.no_stroke()

    # Top-left corner accent
    py5.push_matrix()
    py5.translate(corner_size, corner_size)
    draw_simple_mon()
    py5.pop_matrix()

    # Bottom-right corner accent
    py5.push_matrix()
    py5.translate(py5.width - corner_size, py5.height - corner_size)
    py5.rotate(py5.PI)
    draw_simple_mon()
    py5.pop_matrix()

    py5.pop_style()


def draw_simple_mon():
    """Draw a simple Japanese mon (family crest) design"""
    py5.push_style()
    py5.no_fill()
    py5.stroke(border_color + "50")  # Add transparency
    py5.stroke_weight(1.5)

    # Simple circular mon with inner pattern
    py5.circle(0, 0, 20)
    py5.circle(0, 0, 12)

    # Cross pattern inside
    py5.line(-6, 0, 6, 0)
    py5.line(0, -6, 0, 6)

    py5.pop_style()


def mouse_pressed():
    regenerate_scene()


def key_pressed():
    if py5.key == 'r' or py5.key == 'R':
        regenerate_scene()
    elif py5.key == 's' or py5.key == 'S':
        py5.save_frame("japanese_waves_####.png")
        print("Japanese waves saved!")


def regenerate_scene():
    """Regenerate scene with Japanese aesthetic parameters"""
    global bg_color, border_color, sep, num_layers, wave_intensity

    bg_color = py5.random_choice(bg_colors)
    border_color = py5.random_choice(accent_colors)
    sep = py5.random(0.5, 0.9)
    num_layers = py5.random_choice([2, 3, 4])
    wave_intensity = py5.random(0.8, 1.5)

    print(
        f"New Japanese wave scene generated - Layers: {num_layers}, Intensity: {wave_intensity:.2f}")


if __name__ == "__main__":
    py5.run_sketch()

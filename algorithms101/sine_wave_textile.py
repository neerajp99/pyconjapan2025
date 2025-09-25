import py5
import math

# Textile-focused sine wave pattern generator
# Perfect for fabric prints, dress hems, scarf patterns, and garment contours

# Color palettes for different textile applications
fabric_palettes = {
    "elegant_evening": ["#2C1810", "#8B4513", "#D2691E", "#F4A460", "#FFF8DC"],
    "spring_floral": ["#228B22", "#32CD32", "#98FB98", "#F0FFF0", "#FFFFE0"],
    "ocean_breeze": ["#191970", "#4169E1", "#87CEEB", "#E0F6FF", "#F0F8FF"],
    "sunset_warmth": ["#8B0000", "#FF4500", "#FF8C00", "#FFD700", "#FFFACD"],
    "monochrome_chic": ["#000000", "#2F2F2F", "#696969", "#C0C0C0", "#F5F5F5"]
}

# Global variables
current_palette = "elegant_evening"
wave_layers = 5
amplitude_base = 50
frequency_base = 0.02
phase_shift = 0
time_offset = 0
# 0: horizontal waves, 1: vertical waves, 2: diagonal waves, 3: circular waves
pattern_mode = 0
textile_resolution = 2  # Higher values = more detailed patterns


def setup():
    py5.size(1200, 800)
    py5.background(255)
    py5.color_mode(py5.RGB)
    regenerate_pattern()


def draw():
    global time_offset
    time_offset += 0.01

    py5.background(255, 255, 255)

    # Draw title and info
    draw_pattern_info()

    # Main pattern area
    pattern_area_y = 80
    pattern_height = py5.height - 160

    py5.push_matrix()
    py5.translate(0, pattern_area_y)

    if pattern_mode == 0:
        draw_horizontal_waves(pattern_height)
    elif pattern_mode == 1:
        draw_vertical_waves(pattern_height)
    elif pattern_mode == 2:
        draw_diagonal_waves(pattern_height)
    elif pattern_mode == 3:
        draw_circular_waves(pattern_height)

    py5.pop_matrix()

    # Draw textile application examples
    draw_textile_applications()


def draw_horizontal_waves(pattern_height):
    """Horizontal sine waves - perfect for dress hems and horizontal stripes"""
    colors = fabric_palettes[current_palette]

    for layer in range(wave_layers):
        # Calculate wave parameters for this layer
        amplitude = amplitude_base * (0.5 + 0.5 * layer / wave_layers)
        frequency = frequency_base * (1 + layer * 0.3)
        phase = phase_shift + layer * py5.PI / 4
        y_offset = pattern_height * (layer + 1) / (wave_layers + 1)

        # Color with transparency for layering effect
        color_index = layer % len(colors)
        color_hex = colors[color_index]
        py5.fill(color_hex + "78")  # 120 alpha in hex
        py5.stroke(color_hex + "C8")  # 200 alpha in hex
        py5.stroke_weight(2)

        # Draw filled wave shape
        py5.begin_shape()
        py5.vertex(0, pattern_height)

        for x in range(0, py5.width + 1, textile_resolution):
            wave_y = y_offset + amplitude * \
                py5.sin(frequency * x + phase + time_offset)
            # Add secondary wave for complexity
            wave_y += amplitude * 0.3 * \
                py5.sin(frequency * 2.5 * x + phase * 1.5 + time_offset * 1.2)
            py5.vertex(x, wave_y)

        py5.vertex(py5.width, pattern_height)
        py5.end_shape(py5.CLOSE)


def draw_vertical_waves(pattern_height):
    """Vertical sine waves - perfect for side seams and vertical patterns"""
    colors = fabric_palettes[current_palette]

    for layer in range(wave_layers):
        amplitude = amplitude_base * (0.5 + 0.5 * layer / wave_layers)
        frequency = frequency_base * (1 + layer * 0.3)
        phase = phase_shift + layer * py5.PI / 4
        x_offset = py5.width * (layer + 1) / (wave_layers + 1)

        color_index = layer % len(colors)
        color_hex = colors[color_index]
        py5.fill(color_hex + "78")  # 120 alpha in hex
        py5.stroke(color_hex + "C8")  # 200 alpha in hex
        py5.stroke_weight(2)

        py5.begin_shape()
        py5.vertex(0, 0)

        for y in range(0, int(pattern_height) + 1, textile_resolution):
            wave_x = x_offset + amplitude * \
                py5.sin(frequency * y + phase + time_offset)
            wave_x += amplitude * 0.3 * \
                py5.sin(frequency * 2.5 * y + phase * 1.5 + time_offset * 1.2)
            py5.vertex(wave_x, y)

        py5.vertex(0, pattern_height)
        py5.end_shape(py5.CLOSE)


def draw_diagonal_waves(pattern_height):
    """Diagonal sine waves - perfect for bias cuts and dynamic patterns"""
    colors = fabric_palettes[current_palette]

    for layer in range(wave_layers):
        amplitude = amplitude_base * 0.5
        frequency = frequency_base * 2
        phase = phase_shift + layer * py5.PI / 3

        color_index = layer % len(colors)
        color_hex = colors[color_index]
        py5.fill(color_hex + "64")  # 100 alpha in hex
        py5.stroke(color_hex + "B4")  # 180 alpha in hex
        py5.stroke_weight(3)

        # Draw diagonal wave bands
        for offset in range(-py5.width, py5.width + int(pattern_height), 100):
            py5.begin_shape()
            py5.no_fill()

            for t in range(0, int(py5.width + pattern_height), textile_resolution):
                x = t + offset
                y = t * 0.5

                if 0 <= x <= py5.width and 0 <= y <= pattern_height:
                    wave_offset = amplitude * \
                        py5.sin(frequency * t + phase +
                                time_offset + layer * 0.5)
                    py5.vertex(x + wave_offset, y + wave_offset * 0.5)

            py5.end_shape()


def draw_circular_waves(pattern_height):
    """Circular sine waves - perfect for medallion patterns and radial designs"""
    colors = fabric_palettes[current_palette]
    center_x = py5.width / 2
    center_y = pattern_height / 2

    for layer in range(wave_layers):
        radius_base = 50 + layer * 40
        frequency = 0.05 + layer * 0.02
        phase = phase_shift + layer * py5.PI / 4

        color_index = layer % len(colors)
        color_hex = colors[color_index]
        py5.fill(color_hex + "50")  # 80 alpha in hex
        py5.stroke(color_hex + "A0")  # 160 alpha in hex
        py5.stroke_weight(2)

        py5.begin_shape()

        for angle in range(0, 361, 5):
            rad = py5.radians(angle)
            radius = radius_base + amplitude_base * 0.5 * \
                py5.sin(frequency * angle * 3 + phase + time_offset)
            x = center_x + radius * py5.cos(rad)
            y = center_y + radius * py5.sin(rad)
            py5.vertex(x, y)

        py5.end_shape(py5.CLOSE)


def draw_pattern_info():
    """Display pattern information and controls"""
    py5.fill(0)
    py5.text_size(16)
    py5.text_align(py5.LEFT)

    mode_names = ["Horizontal Waves", "Vertical Waves",
                  "Diagonal Waves", "Circular Waves"]
    py5.text(
        f"Sine Wave Textile Pattern - Mode: {mode_names[pattern_mode]}", 20, 25)
    py5.text(f"Palette: {current_palette.replace('_', ' ').title()}", 20, 45)
    py5.text(
        "Controls: SPACE=Change Mode, C=Change Colors, S=Save, R=Regenerate", 20, 65)


def draw_textile_applications():
    """Show how patterns would look on different textile applications"""
    py5.fill(100)
    py5.text_size(12)
    py5.text_align(py5.LEFT)

    app_y = py5.height - 60
    applications = [
        "Dress Hem", "Scarf Pattern", "Fabric Print", "Garment Seam", "Decorative Border"
    ]

    py5.text("Textile Applications:", 20, app_y)
    for i, app in enumerate(applications):
        py5.text(f"• {app}", 20 + i * 120, app_y + 20)


def regenerate_pattern():
    """Generate new random pattern parameters"""
    global amplitude_base, frequency_base, phase_shift, wave_layers

    amplitude_base = py5.random(30, 80)
    frequency_base = py5.random(0.01, 0.05)
    phase_shift = py5.random(0, py5.TWO_PI)
    wave_layers = int(py5.random(3, 7))

    print(
        f"New pattern generated - Amplitude: {amplitude_base:.1f}, Frequency: {frequency_base:.3f}, Layers: {wave_layers}")


def key_pressed():
    global pattern_mode, current_palette

    if py5.key == ' ':
        pattern_mode = (pattern_mode + 1) % 4
        print(f"Pattern mode changed to: {pattern_mode}")
    elif py5.key == 'c' or py5.key == 'C':
        palette_names = list(fabric_palettes.keys())
        current_index = palette_names.index(current_palette)
        current_palette = palette_names[(
            current_index + 1) % len(palette_names)]
        print(f"Color palette changed to: {current_palette}")
    elif py5.key == 'r' or py5.key == 'R':
        regenerate_pattern()
    elif py5.key == 's' or py5.key == 'S':
        filename = f"sine_textile_{pattern_mode}_{current_palette}_####.png"
        py5.save_frame(filename)
        print(f"Textile pattern saved as: {filename}")


def mouse_pressed():
    regenerate_pattern()


if __name__ == "__main__":
    py5.run_sketch()

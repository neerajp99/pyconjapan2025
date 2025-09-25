import py5
import math
import random

# Enhanced color palettes for sophisticated textile applications
floral_palettes = {
    "rose_garden": {"bg": "#1a0d0d", "petals": ["#ff6b9d", "#ffa8cc", "#ffcce5"], "centers": "#8b0000", "accent": "#ff1744"},
    "lavender_fields": {"bg": "#2d1b3d", "petals": ["#9c88ff", "#c8b5ff", "#e1d4ff"], "centers": "#4a148c", "accent": "#7c4dff"},
    "coral_reef": {"bg": "#2d1810", "petals": ["#ff7043", "#ffab91", "#ffccbc"], "centers": "#bf360c", "accent": "#ff5722"},
    "emerald_forest": {"bg": "#0d2818", "petals": ["#66bb6a", "#a5d6a7", "#c8e6c9"], "centers": "#1b5e20", "accent": "#4caf50"},
    "sunset_bloom": {"bg": "#3d1a00", "petals": ["#ff8a65", "#ffcc02", "#ffd54f"], "centers": "#e65100", "accent": "#ff9800"},
    "cherry_blossom": {"bg": "#2d1a1a", "petals": ["#f8bbd9", "#f48fb1", "#f06292"], "centers": "#880e4f", "accent": "#e91e63"},
    "vintage_gold": {"bg": "#2d2416", "petals": ["#ffd700", "#ffecb3", "#fff8e1"], "centers": "#ff8f00", "accent": "#ffc107"}
}

# Global variables
centroids = []
centroids_idx = 0
n_flowers = 18
n_petals = 12
margin = 100
petal_ends = []
current_palette = "rose_garden"
pattern_scale = 1.0
animation_speed = 0.02
time_offset = 0
show_construction = False
# 0: classic flowers, 1: geometric flowers, 2: sine wave flowers, 3: mandala flowers
textile_mode = 0


class FlowerCentroid:
    def __init__(self, x0, y0, flower_id):
        self.x0 = x0
        self.y0 = y0
        self.theta0 = random.uniform(0, py5.TWO_PI)
        self.id = flower_id
        self.arcs_left = list(range(n_petals))
        random.shuffle(self.arcs_left)
        self.petal_size_variation = random.uniform(0.8, 1.2)
        self.sine_frequency = random.uniform(0.5, 2.0)
        self.sine_amplitude = random.uniform(0.3, 0.8)


def setup():
    py5.size(1200, 800)
    py5.pixel_density(2)
    py5.color_mode(py5.RGB)
    generate_flower_field()
    print("Enhanced Floral Sine Wave Textile Generator")
    print("Comprehensive sine wave integration throughout all elements")
    print("Controls:")
    print("- SPACE: Change textile mode")
    print("- C: Change color palette")
    print("- R: Regenerate flower field")
    print("- S: Save pattern")
    print("- T: Toggle construction lines")
    print("- +/-: Adjust flower count")
    print("- A: Adjust animation speed")
    print("- F: Change sine frequency")


def draw():
    global centroids_idx, time_offset
    time_offset += animation_speed

    # Set background with sine-based subtle texture
    colors = floral_palettes[current_palette]
    py5.background(colors["bg"])

    # Add sine-wave background texture
    draw_sine_background(colors)

    py5.no_stroke()

    # Draw interface
    draw_interface()

    # Main drawing area
    py5.push_matrix()
    py5.translate(0, 80)

    # Draw one petal per frame for organic growth animation
    if centroids_idx < len(centroids):
        draw_next_petal()
    else:
        # All flowers complete - show final result
        draw_complete_flowers()

    py5.pop_matrix()

    # Draw textile application info
    draw_textile_info()


def draw_next_petal():
    """Draw the next petal in the sequence"""
    global centroids_idx

    if centroids_idx >= len(centroids):
        return

    c = centroids[centroids_idx]
    colors = floral_palettes[current_palette]

    if len(c.arcs_left) > 0:
        # Draw next petal
        petal_index = c.arcs_left.pop()
        theta = py5.TWO_PI * petal_index / n_petals + c.theta0

        if textile_mode == 0:
            draw_classic_petal(c, theta, colors)
        elif textile_mode == 1:
            draw_geometric_petal(c, theta, colors)
        elif textile_mode == 2:
            draw_sine_wave_petal(c, theta, colors)
        else:
            draw_mandala_petal(c, theta, colors)
    else:
        # Draw flower center
        draw_flower_center(c, colors)
        centroids_idx += 1


def draw_classic_petal(c, theta, colors):
    """Draw classic petal with sine wave modulation for organic edges and natural variation"""
    r_max = longest_possible_radius(c, theta)

    # Use multiple petal colors for depth and beauty
    petal_colors = colors["petals"]

    x, y, d = 0, 0, 0
    r = 0

    while r + d/2 < r_max:
        # Sine wave modulation for organic petal edges
        edge_wave = py5.sin(r * c.sine_frequency * 0.3 +
                            theta * 3 + time_offset) * c.sine_amplitude * 8
        size_wave = py5.sin(r * 0.1 + time_offset * 0.5) * 0.15 + 1.0

        # Apply sine modulation to position
        modulated_r = r + edge_wave
        x = c.x0 + modulated_r * py5.cos(theta) * size_wave
        y = c.y0 + modulated_r * py5.sin(theta) * size_wave

        # Sine-modulated petal size for organic texture
        d = r * py5.sin(py5.TWO_PI / n_petals) * c.petal_size_variation
        d += py5.sin(r * 0.25 + theta * 2 + time_offset) * 3

        # Choose color based on distance from center for gradient effect
        color_index = min(len(petal_colors) - 1,
                          int((r / r_max) * len(petal_colors)))
        py5.fill(petal_colors[color_index])

        # Add subtle stroke with sine variation
        py5.stroke(colors["accent"])
        py5.stroke_weight(0.5 + 0.3 * py5.sin(r * 0.15 + time_offset))

        if d > 1.5:
            py5.circle(x, y, d - 1.5)

            # Add secondary sine-based texture dots
            if r % 8 == 0:
                texture_x = x + py5.sin(theta * 5 + time_offset) * 4
                texture_y = y + py5.cos(theta * 5 + time_offset) * 4
                py5.fill(colors["accent"])
                py5.circle(texture_x, texture_y, 2)
                py5.fill(petal_colors[color_index])  # Reset fill

        if (x < margin/2 or x > py5.width - margin/2 or
                y < margin/2 or y > py5.height - 160):
            break

        if check_petal_intersection(x, y, d, c.id):
            break

        r += 1

    petal_ends.append({"x": x, "y": y, "d": d, "id": c.id})


def draw_geometric_petal(c, theta, colors):
    """Draw geometric petal with sine-modulated angular shapes and dynamic colors"""
    r_max = longest_possible_radius(c, theta)

    petal_colors = colors["petals"]
    r = 0

    while r < r_max:
        # Sine wave modulation for dynamic positioning
        wave_x = py5.sin(r * c.sine_frequency + time_offset) * \
            c.sine_amplitude * 5
        wave_y = py5.cos(r * c.sine_frequency * 0.7 +
                         time_offset) * c.sine_amplitude * 3

        x = c.x0 + r * py5.cos(theta) + wave_x
        y = c.y0 + r * py5.sin(theta) + wave_y

        # Sine-modulated geometric shape size
        size = r * py5.sin(py5.TWO_PI / n_petals) * c.petal_size_variation
        size += py5.sin(r * 0.3 + theta * 4 + time_offset) * 4

        # Choose color based on distance for layered effect
        color_index = min(len(petal_colors) - 1,
                          int((r / r_max) * len(petal_colors)))
        py5.fill(petal_colors[color_index])

        # Sine-modulated accent stroke
        py5.stroke(colors["accent"])
        py5.stroke_weight(0.8 + 0.4 * py5.sin(r * 0.2 + time_offset))

        if size > 2:
            py5.push_matrix()
            py5.translate(x, y)
            # Sine-based rotation for organic movement
            rotation = theta + time_offset * 0.1 + \
                py5.sin(r * 0.1 + time_offset) * 0.5
            py5.rotate(rotation)

            # Draw diamond/square shapes with sine-modulated corners
            corner_radius = size/4 + py5.sin(r * 0.4 + time_offset) * size/8
            py5.rect(-size/2, -size/2, size, size, corner_radius)

            # Add sine-based inner geometric details
            if r % 10 == 0:
                py5.fill(colors["accent"])
                inner_size = size * 0.3 * (1 + 0.3 * py5.sin(time_offset * 2))
                py5.circle(0, 0, inner_size)
                py5.fill(petal_colors[color_index])  # Reset fill

            py5.pop_matrix()

        if (x < margin/2 or x > py5.width - margin/2 or
                y < margin/2 or y > py5.height - 160):
            break

        if check_petal_intersection(x, y, size, c.id):
            break

        r += 2

    petal_ends.append({"x": x, "y": y, "d": size, "id": c.id})


def draw_sine_wave_petal(c, theta, colors):
    """Draw petal using sine wave modulation with beautiful color gradients"""
    r_max = longest_possible_radius(c, theta)

    petal_colors = colors["petals"]

    # Draw sine wave petal outline
    py5.stroke(colors["accent"])
    py5.stroke_weight(2)
    py5.no_fill()

    py5.begin_shape()

    for r in range(0, int(r_max), 2):
        # Modulate radius with sine wave
        wave_offset = c.sine_amplitude * \
            py5.sin(r * c.sine_frequency + time_offset)
        actual_r = r + wave_offset * 10

        x = c.x0 + actual_r * py5.cos(theta)
        y = c.y0 + actual_r * py5.sin(theta)

        if r == 0:
            py5.vertex(x, y)
        else:
            py5.curve_vertex(x, y)

        if (x < margin/2 or x > py5.width - margin/2 or
                y < margin/2 or y > py5.height - 160):
            break

    py5.end_shape()

    # Add filled circles along the wave with color gradients
    py5.no_stroke()
    for r in range(0, int(r_max), 6):
        wave_offset = c.sine_amplitude * \
            py5.sin(r * c.sine_frequency + time_offset)
        actual_r = r + wave_offset * 10

        x = c.x0 + actual_r * py5.cos(theta)
        y = c.y0 + actual_r * py5.sin(theta)

        # Choose color based on position along petal
        color_index = min(len(petal_colors) - 1,
                          int((r / r_max) * len(petal_colors)))
        py5.fill(petal_colors[color_index])

        size = 4 + abs(wave_offset) * 3
        py5.circle(x, y, size)

        # Add smaller accent dots
        py5.fill(colors["accent"])
        py5.circle(x, y, size * 0.3)

    petal_ends.append({"x": x, "y": y, "d": 5, "id": c.id})


def draw_sine_background(colors):
    """Draw subtle sine wave background texture for textile effect"""
    py5.stroke(colors["accent"])
    py5.stroke_weight(0.3)

    # Horizontal sine waves
    for y in range(0, py5.height, 40):
        py5.begin_shape()
        py5.no_fill()
        for x in range(0, py5.width, 8):
            wave_y = y + 15 * py5.sin(x * 0.02 + time_offset * 0.5)
            py5.vertex(x, wave_y)
        py5.end_shape()

    # Vertical sine waves
    for x in range(0, py5.width, 60):
        py5.begin_shape()
        py5.no_fill()
        for y in range(0, py5.height, 8):
            wave_x = x + 10 * py5.sin(y * 0.03 + time_offset * 0.3)
            py5.vertex(wave_x, y)
        py5.end_shape()


def draw_mandala_petal(c, theta, colors):
    """Draw mandala-style petal with concentric patterns and multiple colors"""
    r_max = longest_possible_radius(c, theta)

    petal_colors = colors["petals"]

    py5.stroke(colors["accent"])
    py5.stroke_weight(1.5)
    py5.no_fill()

    # Draw concentric arcs with color variations
    for ring in range(1, int(r_max/8)):
        radius = ring * 8

        # Choose color for this ring
        color_index = min(len(petal_colors) - 1, ring % len(petal_colors))
        py5.stroke(petal_colors[color_index])

        # Modulate with sine wave
        wave_mod = py5.sin(ring * 0.5 + time_offset) * 3
        actual_radius = radius + wave_mod

        start_angle = theta - py5.PI / n_petals
        end_angle = theta + py5.PI / n_petals

        py5.arc(c.x0, c.y0, actual_radius * 2, actual_radius * 2,
                start_angle, end_angle)

    # Add decorative dots with gradient colors
    py5.no_stroke()
    for r in range(8, int(r_max), 12):
        x = c.x0 + r * py5.cos(theta)
        y = c.y0 + r * py5.sin(theta)

        # Choose color based on distance
        color_index = min(len(petal_colors) - 1,
                          int((r / r_max) * len(petal_colors)))
        py5.fill(petal_colors[color_index])
        py5.circle(x, y, 4)

        # Add center accent
        py5.fill(colors["accent"])
        py5.circle(x, y, 1.5)

    petal_ends.append({"x": x, "y": y, "d": 3, "id": c.id})


def draw_flower_center(c, colors):
    """Draw the flower center with sine-based pulsing and texture"""
    # Calculate average petal size for this flower
    d_sum = 0
    petal_count = 0

    for p in petal_ends:
        if p["id"] == c.id:
            d_sum += p["d"]
            petal_count += 1

    if petal_count > 0:
        base_size = d_sum / n_petals

        # Sine-based pulsing center
        pulse = 1 + 0.2 * py5.sin(time_offset * 3 + c.id * 0.5)
        center_size = base_size * pulse

        # Main center with sine-modulated color intensity
        py5.fill(colors["centers"])
        py5.stroke(colors["accent"])
        py5.stroke_weight(1 + 0.5 * py5.sin(time_offset * 2 + c.id))
        py5.circle(c.x0, c.y0, center_size)

        # Add sine-based inner texture rings
        py5.no_stroke()
        for ring in range(1, 4):
            ring_size = center_size * (0.7 - ring * 0.15)
            ring_alpha = 100 + 50 * py5.sin(time_offset * 4 + ring + c.id)
            py5.fill(colors["accent"] + hex(int(ring_alpha))[-2:])

            # Sine-modulated ring positions
            ring_x = c.x0 + py5.sin(time_offset + ring) * 2
            ring_y = c.y0 + py5.cos(time_offset + ring) * 2
            py5.circle(ring_x, ring_y, ring_size)


def draw_complete_flowers():
    """Draw all flowers when animation is complete with sine-enhanced final effects"""
    colors = floral_palettes[current_palette]
    petal_colors = colors["petals"]

    # Draw all petals with sine-enhanced colors and positions
    for i, p in enumerate(petal_ends):
        # Sine-based color shifting
        color_index = p["id"] % len(petal_colors)

        # Add subtle sine-based position variation
        sine_x = p["x"] + py5.sin(time_offset * 0.5 + i * 0.1) * 1.5
        sine_y = p["y"] + py5.cos(time_offset * 0.3 + i * 0.15) * 1.0

        py5.fill(petal_colors[color_index])
        py5.stroke(colors["accent"])
        py5.stroke_weight(0.5 + 0.2 * py5.sin(time_offset + i * 0.2))

        # Sine-modulated petal size for breathing effect
        breathing_size = p["d"] * \
            (1 + 0.1 * py5.sin(time_offset * 2 + i * 0.3))
        py5.circle(sine_x, sine_y, breathing_size)

    # Draw all centers with enhanced sine-based styling
    for c in centroids:
        d_sum = sum(p["d"] for p in petal_ends if p["id"] == c.id)
        base_center_size = d_sum / n_petals if d_sum > 0 else 10

        # Sine-based pulsing center
        pulse = 1 + 0.15 * py5.sin(time_offset * 3 + c.id * 0.8)
        center_size = base_center_size * pulse

        # Draw center with sine-enhanced gradient effect
        py5.fill(colors["centers"])
        py5.stroke(colors["accent"])
        py5.stroke_weight(1 + 0.3 * py5.sin(time_offset * 1.5 + c.id))

        # Slight sine-based center movement
        center_x = c.x0 + py5.sin(time_offset * 0.8 + c.id) * 0.8
        center_y = c.y0 + py5.cos(time_offset * 0.6 + c.id) * 0.6
        py5.circle(center_x, center_y, center_size)

        # Add sine-animated inner highlight
        py5.fill(colors["accent"])
        py5.no_stroke()
        highlight_size = center_size * 0.4 * \
            (1 + 0.2 * py5.sin(time_offset * 4 + c.id))
        py5.circle(center_x, center_y, highlight_size)


def generate_flower_field():
    """Generate flower positions using Voronoi relaxation with sine-based organic distribution"""
    global centroids, centroids_idx, petal_ends

    centroids = []
    petal_ends = []
    centroids_idx = 0

    # Generate initial positions with sine-based organic clustering
    for i in range(n_flowers):
        # Use sine waves to create natural clustering patterns
        cluster_x = py5.width/2 + py5.sin(i * 0.8) * (py5.width/3)
        cluster_y = (py5.height - 240)/2 + \
            py5.cos(i * 0.6) * ((py5.height - 240)/3)

        # Add sine-based variation around clusters
        variation_x = py5.sin(i * 2.3 + time_offset) * 80
        variation_y = py5.cos(i * 1.7 + time_offset) * 60

        x0 = py5.constrain(cluster_x + variation_x, margin, py5.width - margin)
        y0 = py5.constrain(cluster_y + variation_y, margin, py5.height - 240)

        centroids.append(FlowerCentroid(x0, y0, i))

    # Apply Voronoi relaxation for better distribution
    for _ in range(3):
        voronoi_relaxation()

    print(
        f"Generated {n_flowers} flowers with sine-enhanced Voronoi relaxation")


def voronoi_relaxation():
    """Apply Voronoi relaxation to improve flower distribution"""
    n = 20
    s = py5.width / n
    voronoi = [[] for _ in range(n_flowers)]

    for i in range(n):
        x = (i + 0.5) * s
        for j in range(n):
            y = (j + 0.5) * s
            if y < py5.height - 240:  # Stay within drawing area
                cid = closest_centroid_id(x, y)
                if cid >= 0:
                    voronoi[cid].append([x, y])

    # Update centroid positions
    for i, c in enumerate(centroids):
        cell_points = voronoi[i]
        if cell_points:
            x_sum = sum(p[0] for p in cell_points)
            y_sum = sum(p[1] for p in cell_points)

            new_x = py5.constrain(x_sum / len(cell_points),
                                  margin, py5.width - margin)
            new_y = py5.constrain(y_sum / len(cell_points),
                                  margin, py5.height - 240)

            c.x0 = new_x
            c.y0 = new_y


def longest_possible_radius(centroid, theta):
    """Calculate the longest possible radius for a petal"""
    x0, y0 = centroid.x0, centroid.y0
    r_max = min(min(x0, py5.width - x0), min(y0, py5.height - 160 - y0))
    r_step = 2
    r = 0

    while True:
        r += r_step
        x = x0 + r * py5.cos(theta)
        y = y0 + r * py5.sin(theta)

        if closest_centroid_id(x, y) != centroid.id:
            break
        if x < 0 or x > py5.width or y < 0 or y > py5.height - 160:
            break

    return r - r_step


def closest_centroid_id(x, y):
    """Find the closest centroid to given coordinates"""
    if not centroids:
        return -1

    min_dist = float('inf')
    id_min = -1

    for c in centroids:
        d = (c.x0 - x) ** 2 + (c.y0 - y) ** 2
        if d < min_dist:
            min_dist = d
            id_min = c.id

    return id_min


def check_petal_intersection(x, y, d, flower_id):
    """Check if petal intersects with existing petals"""
    for p in petal_ends:
        if p["id"] != flower_id:
            distance = math.sqrt((x - p["x"])**2 + (y - p["y"])**2)
            if distance < d/2 + p["d"]/2 + 6:
                return True
    return False


def draw_interface():
    """Draw the user interface"""
    # py5.fill(255)
    # py5.text_size(16)
    # py5.text_align(py5.LEFT)

    # mode_names = ["Classic Flowers", "Geometric Flowers", "Sine Wave Flowers", "Mandala Flowers"]
    # py5.text(f"Floral Sine Wave Textile - Mode: {mode_names[textile_mode]}", 20, 25)
    # py5.text(f"Palette: {current_palette.replace('_', ' ').title()}", 20, 45)
    # py5.text(f"Flowers: {n_flowers} | Progress: {centroids_idx}/{len(centroids)}", 20, 65)


def draw_textile_info():
    """Show textile applications"""
    # py5.fill(255, 200)
    # py5.text_size(12)
    # py5.text_align(py5.LEFT)

    # app_y = py5.height - 40
    # applications = [
    #     "Fashion Prints", "Dress Patterns", "Scarf Designs", "Wallpaper", "Decorative Textiles"
    # ]

    # py5.text("Textile Applications:", 20, app_y)
    # for i, app in enumerate(applications):
    #     py5.text(f"• {app}", 20 + i * 120, app_y + 20)


def key_pressed():
    global textile_mode, current_palette, n_flowers, show_construction

    if py5.key == ' ':
        textile_mode = (textile_mode + 1) % 4
        generate_flower_field()  # Regenerate for new mode
        mode_names = ["Classic Flowers", "Geometric Flowers",
                      "Sine Wave Flowers", "Mandala Flowers"]
        print(f"Textile mode: {mode_names[textile_mode]}")

    elif py5.key == 'c' or py5.key == 'C':
        palettes = list(floral_palettes.keys())
        current_index = palettes.index(current_palette)
        current_palette = palettes[(current_index + 1) % len(palettes)]
        print(f"Color palette: {current_palette}")

    elif py5.key == 'r' or py5.key == 'R':
        generate_flower_field()

    elif py5.key == 's' or py5.key == 'S':
        filename = f"floral_sine_{current_palette}_{textile_mode}_####.png"
        py5.save_frame(filename)
        print(f"Sine-enhanced floral pattern saved as: {filename}")

    elif py5.key == 't' or py5.key == 'T':
        show_construction = not show_construction
        print(f"Construction lines: {'ON' if show_construction else 'OFF'}")

    elif py5.key == '+' or py5.key == '=':
        n_flowers = min(30, n_flowers + 3)
        generate_flower_field()

    elif py5.key == '-' or py5.key == '_':
        n_flowers = max(6, n_flowers - 3)
        generate_flower_field()

    elif py5.key == 'a' or py5.key == 'A':
        global animation_speed
        animation_speed = 0.005 if animation_speed > 0.01 else 0.02
        print(
            f"Animation speed: {'Slow' if animation_speed < 0.01 else 'Normal'}")

    elif py5.key == 'f' or py5.key == 'F':
        # Regenerate with new sine frequencies
        for c in centroids:
            c.sine_frequency = random.uniform(0.3, 3.0)
            c.sine_amplitude = random.uniform(0.2, 1.0)
        print("Sine frequencies randomized")


def mouse_pressed():
    """Reset animation on mouse click"""
    generate_flower_field()


if __name__ == "__main__":
    py5.run_sketch()

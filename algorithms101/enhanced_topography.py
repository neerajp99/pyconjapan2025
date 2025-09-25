import py5
import random
import math

# Canvas settings
canvas_width = 800
canvas_height = 800

# Topography settings
rings = 32
dim_init = 0
spacing = -15
magnitude = 120
noise_delta = 18
noise_radius = 0.45

# Enhanced fill settings
flow_field_density = 12
dust_particle_count = 200
perlin_texture_density = 15
line_texture_density = 8

# Global variables
THE_SEED = None
ox, oy, oz = 0, 0, 0
arr = []
contour_shapes = []

# Enhanced diverse and darker color palettes
elevation_colors = [
    (45, 25, 15, 200),      # Dark brown - deep valleys
    (65, 35, 25, 190),      # Rich brown - lower slopes
    (85, 45, 35, 180),      # Medium brown - mid elevations
    (105, 65, 45, 170),     # Warm brown - upper slopes
    (125, 85, 65, 160),     # Light brown - high peaks
    (25, 35, 45, 200),      # Dark blue-grey - water areas
    (35, 45, 55, 190),      # Blue-grey - wetlands
    (55, 65, 75, 180),      # Medium grey - rocky areas
    (75, 85, 95, 170),      # Light grey - exposed rock
    (95, 105, 115, 160),    # Pale grey - snow line
    (15, 25, 35, 200),      # Very dark - deep shadows
    (25, 45, 35, 190),      # Dark green - dense forest
    (35, 55, 45, 180),      # Forest green - woodland
    (45, 65, 55, 170),      # Medium green - grassland
    (55, 75, 65, 160),      # Light green - meadows
    (65, 25, 35, 200),      # Dark red - mineral deposits
    (75, 35, 45, 190),      # Red-brown - iron rich soil
    (85, 45, 55, 180),      # Rust color - oxidized areas
    (95, 55, 65, 170),      # Pink-brown - sandstone
    (105, 65, 75, 160)      # Light pink - limestone
]

# Fill pattern types for varied elevation zones
fill_patterns = [
    'flow_field',      # Dynamic flow patterns
    'dust_particles',  # Scattered organic particles
    'perlin_lines',    # Organic noise-based textures
    'cross_hatch',     # Structured line patterns
    'stippling',       # Dotted organic patterns
    'wave_lines',      # Flowing wave patterns
    'spiral_lines',    # Spiral organic patterns
    'organic_mesh',    # Mesh-like organic patterns
    'noise_dots',      # Noise-based dot patterns
    'curved_lines'     # Curved organic line patterns
]


class FlowField:
    def __init__(self, bounds, density=12):
        self.bounds = bounds  # (x, y, w, h)
        self.density = density
        self.vectors = []
        self.generate_field()

    def generate_field(self):
        x, y, w, h = self.bounds
        cols = int(w / self.density)
        rows = int(h / self.density)

        for row in range(rows):
            for col in range(cols):
                px = x + col * self.density
                py = y + row * self.density

                # Create more random flow based on multiple noise layers
                angle = py5.noise(px * 0.008, py * 0.008) * py5.TAU * 3
                angle = angle + \
                    py5.noise(px * 0.003, py * 0.003,
                              py5.frame_count * 0.02) * py5.PI
                angle = angle + py5.noise(px * 0.015, py * 0.015) * 0.8

                self.vectors.append({
                    'x': px,
                    'y': py,
                    'angle': angle,
                    'magnitude': py5.noise(px * 0.006, py * 0.006) * 0.8 + 0.2
                })

    def draw(self, color):
        py5.stroke(*color)
        py5.stroke_weight(random.uniform(0.5, 1.2))

        for vec in self.vectors:
            length = vec['magnitude'] * self.density * random.uniform(0.5, 1.2)
            end_x = vec['x'] + py5.cos(vec['angle']) * length
            end_y = vec['y'] + py5.sin(vec['angle']) * length

            py5.line(vec['x'], vec['y'], end_x, end_y)


def draw_dust_particles(bounds, color, count=150):
    """Draw scattered organic dust particles within bounds"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.fill(*color)

    for i in range(count):
        px = x + random.uniform(0, w)
        py_coord = y + random.uniform(0, h)

        # More varied particle types with organic randomness
        particle_type = random.choice(['dot', 'line', 'curve', 'organic_dot'])

        if particle_type == 'dot':
            py5.stroke_weight(random.uniform(0.3, 2.5))
            py5.point(px, py_coord)
        elif particle_type == 'line':
            py5.stroke_weight(random.uniform(0.2, 1.2))
            angle = py5.noise(px * 0.01, py_coord * 0.01) * py5.TAU
            length = random.uniform(1, 8)
            py5.line(px, py_coord,
                     px + py5.cos(angle) * length,
                     py_coord + py5.sin(angle) * length)
        elif particle_type == 'curve':
            py5.stroke_weight(0.6)
            py5.no_fill()
            py5.begin_shape()
            for j in range(3):
                curve_x = px + random.uniform(-3, 3)
                curve_y = py_coord + random.uniform(-3, 3)
                py5.vertex(curve_x, curve_y)
            py5.end_shape()
        else:  # organic_dot
            py5.stroke_weight(0.4)
            size = random.uniform(0.5, 4)
            py5.ellipse(px, py_coord, size, size)


def draw_perlin_lines(bounds, color, density=15):
    """Draw organic lines based on Perlin noise"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.4, 1.0))
    py5.no_fill()

    # Draw more organic perlin-based curves
    for i in range(density):
        py5.begin_shape()
        py5.no_fill()

        start_x = x + random.uniform(0, w)
        start_y = y + random.uniform(0, h)

        current_x = start_x
        current_y = start_y

        for step in range(random.randint(15, 35)):
            if current_x < x or current_x > x + w or current_y < y or current_y > y + h:
                break

            py5.vertex(current_x, current_y)

            # More complex movement based on multiple noise layers
            angle = py5.noise(current_x * 0.008, current_y *
                              0.008, i * 0.1) * py5.TAU
            angle = angle + py5.noise(current_x * 0.015,
                                      current_y * 0.015) * py5.PI * 0.5
            step_size = random.uniform(2, 5)
            current_x = current_x + py5.cos(angle) * step_size
            current_y = current_y + py5.sin(angle) * step_size

        py5.end_shape()


def draw_cross_hatch(bounds, color, spacing=6):
    """Draw organic cross-hatched pattern"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.3, 0.8))

    # More organic diagonal lines
    for i in range(0, int(w + h), spacing):
        offset1 = py5.noise(i * 0.01) * 10
        offset2 = py5.noise(i * 0.01 + 100) * 10
        py5.line(x + i + offset1, y, x + offset2, y + i)
        if i < w:
            py5.line(x + i + offset1, y + h, x + w + offset2, y + h - (w - i))

    # Organic lines other direction
    for i in range(0, int(w + h), spacing * 2):
        offset1 = py5.noise(i * 0.008 + 200) * 8
        offset2 = py5.noise(i * 0.008 + 300) * 8
        py5.line(x + offset1, y + i, x + i + offset2, y)
        if i < w:
            py5.line(x + w - i + offset1, y + h, x + w + offset2, y + h - i)


def draw_stippling(bounds, color, density=120):
    """Draw organic stippled dot pattern"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.fill(*color)

    for i in range(density):
        px = x + random.uniform(0, w)
        py_coord = y + random.uniform(0, h)

        # Organic cluster dots using multiple noise layers
        cluster_factor = py5.noise(px * 0.015, py_coord * 0.015)
        cluster_factor = cluster_factor + \
            py5.noise(px * 0.03, py_coord * 0.03) * 0.5
        if cluster_factor > 0.3:
            dot_size = random.uniform(0.3, 2.5) * cluster_factor
            py5.stroke_weight(dot_size)
            py5.point(px, py_coord)


def draw_wave_lines(bounds, color, wave_count=8):
    """Draw organic flowing wave-like lines"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.6, 1.2))
    py5.no_fill()

    for i in range(wave_count):
        py5.begin_shape()
        py5.no_fill()

        wave_y = y + (i + 1) * h / (wave_count + 1)
        amplitude = random.uniform(8, 25)
        frequency = random.uniform(0.015, 0.08)

        for px in range(int(x), int(x + w), 2):
            wave_offset = py5.sin((px - x) * frequency + i) * amplitude
            wave_offset = wave_offset + \
                py5.noise(px * 0.008, wave_y * 0.008, i * 0.1) * 15
            wave_offset = wave_offset + py5.noise(px * 0.02, wave_y * 0.02) * 5
            py5.vertex(px, wave_y + wave_offset)

        py5.end_shape()


def draw_spiral_lines(bounds, color, spiral_count=5):
    """Draw organic spiral patterns"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.4, 0.9))
    py5.no_fill()

    for i in range(spiral_count):
        center_x = x + random.uniform(w * 0.2, w * 0.8)
        center_y = y + random.uniform(h * 0.2, h * 0.8)

        py5.begin_shape()
        py5.no_fill()

        for angle in range(0, 720, 5):
            rad = py5.radians(angle)
            radius = angle * 0.05 + py5.noise(angle * 0.01, i) * 10
            spiral_x = center_x + py5.cos(rad) * radius
            spiral_y = center_y + py5.sin(rad) * radius

            if x <= spiral_x <= x + w and y <= spiral_y <= y + h:
                py5.vertex(spiral_x, spiral_y)

        py5.end_shape()


def draw_organic_mesh(bounds, color, mesh_density=8):
    """Draw organic mesh patterns"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.3, 0.7))

    for i in range(0, int(w), mesh_density):
        for j in range(0, int(h), mesh_density):
            px = x + i
            py_coord = y + j

            # Organic connections based on noise
            if py5.noise(px * 0.01, py_coord * 0.01) > 0.4:
                end_x = px + py5.noise(px * 0.008,
                                       py_coord * 0.008) * mesh_density
                end_y = py_coord + \
                    py5.noise(px * 0.008 + 100, py_coord * 0.008) * \
                    mesh_density
                py5.line(px, py_coord, end_x, end_y)


def draw_noise_dots(bounds, color, dot_count=100):
    """Draw noise-based dot patterns"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.fill(*color)

    for i in range(dot_count):
        px = x + random.uniform(0, w)
        py_coord = y + random.uniform(0, h)

        noise_val = py5.noise(px * 0.02, py_coord * 0.02)
        if noise_val > 0.35:
            size = noise_val * 4
            py5.stroke_weight(size)
            py5.point(px, py_coord)


def draw_curved_lines(bounds, color, curve_count=10):
    """Draw organic curved line patterns"""
    x, y, w, h = bounds
    py5.stroke(*color)
    py5.stroke_weight(random.uniform(0.5, 1.0))
    py5.no_fill()

    for i in range(curve_count):
        py5.begin_shape()
        py5.no_fill()

        start_x = x + random.uniform(0, w)
        start_y = y + random.uniform(0, h)

        control_points = []
        for j in range(4):
            ctrl_x = start_x + random.uniform(-w*0.3, w*0.3)
            ctrl_y = start_y + random.uniform(-h*0.3, h*0.3)
            control_points.append((ctrl_x, ctrl_y))

        py5.vertex(start_x, start_y)
        for j in range(0, len(control_points)-2, 2):
            py5.bezier_vertex(control_points[j][0], control_points[j][1],
                              control_points[j+1][0], control_points[j+1][1],
                              control_points[j+2][0] if j +
                              2 < len(control_points) else control_points[-1][0],
                              control_points[j+2][1] if j+2 < len(control_points) else control_points[-1][1])

        py5.end_shape()


def get_noise(radian, dim):
    """Enhanced noise function with more organic variation"""
    r = radian % py5.TAU
    if r < 0.0:
        r = r + py5.TAU

    # Multiple noise layers for more organic results
    base_noise = py5.noise(ox + py5.cos(r) * (noise_radius + dim / 150),
                           oy + py5.sin(r) * (noise_radius + dim / 150), dim)
    detail_noise = py5.noise(ox + py5.cos(r) * (noise_radius + dim / 80),
                             oy + py5.sin(r) * (noise_radius + dim / 80), dim * 2) * 0.3
    fine_noise = py5.noise(ox + py5.cos(r) * (noise_radius + dim / 40),
                           oy + py5.sin(r) * (noise_radius + dim / 40), dim * 4) * 0.1

    return base_noise + detail_noise + fine_noise


def create_contour_shape(ring_index):
    """Create highly randomized contour ring with organic variations"""
    new_arr = []

    for ang in range(360):
        rad = py5.radians(ang)
        base_radius = spacing + arr[ang]

        # More complex noise with multiple layers for organic randomness
        noise_offset = get_noise(rad, ring_index * noise_delta) * magnitude
        random_variation = random.uniform(-15, 15) * (ring_index / rings)
        organic_variation = py5.noise(ang * 0.05, ring_index * 0.1) * 30

        new_radius = base_radius + noise_offset + random_variation + organic_variation
        new_arr.append(new_radius)

    return new_arr


def draw_filled_contour(ring_index, inner_radius_arr, outer_radius_arr):
    """Draw a contour ring with enhanced organic fill patterns"""
    # More random pattern and color selection
    pattern_index = random.randint(0, len(fill_patterns) - 1)
    color_index = random.randint(0, len(elevation_colors) - 1)

    pattern = fill_patterns[pattern_index]
    color = elevation_colors[color_index]

    # Create the organic contour shape
    py5.fill(*color)
    py5.stroke(0, 0, 0, random.randint(80, 150))
    py5.stroke_weight(random.uniform(0.5, 2.0))

    # Draw the main contour shape
    py5.begin_shape()
    for ang in range(360):
        rad = py5.radians(ang)
        x = outer_radius_arr[ang] * py5.cos(rad)
        y = outer_radius_arr[ang] * py5.sin(rad)
        py5.vertex(x, y)

    # Create hole (inner contour)
    py5.begin_contour()
    for ang in range(359, -1, -1):
        rad = py5.radians(ang)
        x = inner_radius_arr[ang] * py5.cos(rad)
        y = inner_radius_arr[ang] * py5.sin(rad)
        py5.vertex(x, y)
    py5.end_contour()
    py5.end_shape(py5.CLOSE)

    # Calculate bounds for fill pattern
    max_outer = max(outer_radius_arr)
    min_inner = min(inner_radius_arr) if inner_radius_arr else 0

    bounds = (-max_outer, -max_outer, max_outer * 2, max_outer * 2)

    # Apply organic fill pattern
    py5.push()

    # Draw fill pattern with more organic colors
    fill_color = (color[0], color[1], color[2], random.randint(60, 120))

    if pattern == 'flow_field':
        flow_field = FlowField(bounds, flow_field_density)
        flow_field.draw(fill_color)
    elif pattern == 'dust_particles':
        draw_dust_particles(bounds, fill_color, dust_particle_count)
    elif pattern == 'perlin_lines':
        draw_perlin_lines(bounds, fill_color, perlin_texture_density)
    elif pattern == 'cross_hatch':
        draw_cross_hatch(bounds, fill_color)
    elif pattern == 'stippling':
        draw_stippling(bounds, fill_color)
    elif pattern == 'wave_lines':
        draw_wave_lines(bounds, fill_color)
    elif pattern == 'spiral_lines':
        draw_spiral_lines(bounds, fill_color)
    elif pattern == 'organic_mesh':
        draw_organic_mesh(bounds, fill_color)
    elif pattern == 'noise_dots':
        draw_noise_dots(bounds, fill_color)
    elif pattern == 'curved_lines':
        draw_curved_lines(bounds, fill_color)

    py5.pop()


def display_enhanced_topography():
    """Display the enhanced organic topography with varied fills"""
    previous_arr = None

    for i in range(rings):
        current_arr = create_contour_shape(i)

        if previous_arr is not None:
            draw_filled_contour(i, previous_arr, current_arr)

        previous_arr = current_arr.copy()
        arr[:] = current_arr


def display_organic_marks():
    """Display organic reference marks instead of crosses"""
    py5.stroke(0, 0, 0, 40)
    py5.stroke_weight(0.6)

    for i in range(60):
        x = random.uniform(20, canvas_width - 20)
        y = random.uniform(20, canvas_height - 20)

        py5.push()
        py5.translate(x, y)

        # Organic marks instead of rigid crosses
        angle1 = random.uniform(0, py5.TAU)
        angle2 = angle1 + py5.PI/2 + random.uniform(-0.3, 0.3)
        size = random.uniform(2, 6)

        py5.line(-size * py5.cos(angle1), -size * py5.sin(angle1),
                 size * py5.cos(angle1), size * py5.sin(angle1))
        py5.line(-size * py5.cos(angle2), -size * py5.sin(angle2),
                 size * py5.cos(angle2), size * py5.sin(angle2))
        py5.pop()


def display_organic_grid():
    """Display organic reference grid"""
    py5.stroke(0, 0, 0, 25)
    py5.stroke_weight(0.3)

    grid_space = random.randint(100, 140)
    for i in range(grid_space, canvas_height, grid_space):
        offset = py5.noise(i * 0.01) * 20
        py5.line(0, i + offset, canvas_width, i + offset)
    for j in range(grid_space, canvas_width, grid_space):
        offset = py5.noise(j * 0.01 + 100) * 20
        py5.line(j + offset, 0, j + offset, canvas_height)


def setup():
    global THE_SEED, ox, oy, oz, arr

    py5.size(canvas_width, canvas_height)
    THE_SEED = random.randint(0, 9999999)
    random.seed(THE_SEED)
    py5.noise_seed(THE_SEED)

    # Initialize noise offsets with more variation
    ox = random.uniform(0, 20000)
    oy = random.uniform(0, 20000)
    oz = random.uniform(0, 20000)

    # Initialize radius array
    arr = [dim_init for _ in range(360)]

    # Darker background
    py5.background(35, 32, 28)

    print(f"Enhanced organic topography generated with seed: {THE_SEED}")
    print("Features:")
    print("- Organic flow field fills")
    print("- Diverse dust particle textures")
    print("- Complex Perlin noise patterns")
    print("- Organic cross-hatch patterns")
    print("- Random stippling effects")
    print("- Flowing wave patterns")
    print("- Spiral organic patterns")
    print("- Mesh-like textures")
    print("- Noise-based dot patterns")
    print("- Curved organic lines")
    print("Controls:")
    print("- Press 'R' to regenerate")
    print("- Press 'S' to save image")


def draw():
    # Clear with darker background
    py5.background(35, 32, 28)

    # Center the topography with more randomness
    py5.push()
    center_x = py5.random_gaussian(canvas_width / 2, 200)
    center_y = py5.random_gaussian(canvas_height / 2, 200)
    py5.translate(center_x, center_y)

    # Draw enhanced organic topography
    display_enhanced_topography()
    py5.pop()

    # Add organic reference elements
    display_organic_marks()
    display_organic_grid()

    # Stop after one frame
    py5.no_loop()


def key_pressed():
    global THE_SEED, ox, oy, oz, arr

    if py5.key == 'r' or py5.key == 'R':
        # Regenerate everything with more randomness
        THE_SEED = random.randint(0, 9999999)
        random.seed(THE_SEED)
        py5.noise_seed(THE_SEED)

        ox = random.uniform(0, 20000)
        oy = random.uniform(0, 20000)
        oz = random.uniform(0, 20000)

        arr = [dim_init for _ in range(360)]

        py5.loop()  # Trigger redraw
        print(f"New organic topography generated with seed: {THE_SEED}")

    elif py5.key == 's' or py5.key == 'S':
        filename = f"organic_topography_{THE_SEED}.png"
        py5.save_frame(filename)
        print(f"Saved organic topography as {filename}")


if __name__ == "__main__":
    py5.run_sketch()

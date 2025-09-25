import py5
import math
import random

# Voronoi Textile Pattern Generator
# Creates cellular structures perfect for:
# - Laser-cut fabric patterns
# - Breathable garment designs
# - Organic jewelry patterns
# - Modular fashion panels
# - 3D-printable accessories

# Color schemes for different textile applications
textile_color_schemes = {
    "laser_cut": [(0, 0, 0), (255, 255, 255), (128, 128, 128)],
    "organic_jewelry": [(139, 69, 19), (218, 165, 32), (255, 215, 0), (255, 248, 220)],
    "breathable_fabric": [(70, 130, 180), (176, 224, 230), (240, 248, 255), (255, 255, 255)],
    "fashion_panel": [(128, 0, 128), (255, 20, 147), (255, 182, 193), (255, 240, 245)],
    "nature_inspired": [(34, 139, 34), (154, 205, 50), (240, 255, 240), (255, 255, 255)],
    "monochrome_chic": [(0, 0, 0), (64, 64, 64), (128, 128, 128), (192, 192, 192), (255, 255, 255)]
}

# Global variables
voronoi_points = []
num_points = 25
current_scheme = "organic_jewelry"
pattern_mode = 0  # 0: filled cells, 1: outlined cells, 2: gradient cells, 3: textured cells
cell_thickness = 2
animate_points = False
animation_speed = 0.02
time_offset = 0
show_points = True
cell_size_variation = True


class VoronoiPoint:
    def __init__(self, x, y):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.color_index = random.randint(
            0, len(textile_color_schemes[current_scheme]) - 1)
        self.animation_offset = random.uniform(0, py5.TWO_PI)
        self.animation_radius = random.uniform(10, 30)

    def update_position(self, time):
        if animate_points:
            self.x = self.original_x + self.animation_radius * \
                py5.cos(time * animation_speed + self.animation_offset)
            self.y = self.original_y + self.animation_radius * \
                py5.sin(time * animation_speed + self.animation_offset)
        else:
            self.x = self.original_x
            self.y = self.original_y


def setup():
    py5.size(1200, 800)
    py5.background(255)
    generate_voronoi_points()
    print("Voronoi Textile Pattern Generator")
    print("Controls:")
    print("- SPACE: Change pattern mode")
    print("- C: Change color scheme")
    print("- A: Toggle animation")
    print("- P: Toggle point visibility")
    print("- R: Regenerate points")
    print("- S: Save pattern")
    print("- +/-: Adjust number of points")
    print("- Mouse: Add new point")


def draw():
    global time_offset
    time_offset += 1

    # Update point positions if animating
    for point in voronoi_points:
        point.update_position(time_offset)

    py5.background(255)

    # Draw title and controls
    draw_interface()

    # Main pattern area
    pattern_y = 100
    pattern_height = py5.height - 150

    py5.push_matrix()
    py5.translate(0, pattern_y)

    # Draw Voronoi diagram
    if pattern_mode == 0:
        draw_filled_cells(pattern_height)
    elif pattern_mode == 1:
        draw_outlined_cells(pattern_height)
    elif pattern_mode == 2:
        draw_gradient_cells(pattern_height)
    elif pattern_mode == 3:
        draw_textured_cells(pattern_height)

    # Draw seed points if enabled
    if show_points:
        draw_seed_points(pattern_height)

    py5.pop_matrix()

    # Draw textile applications info
    draw_applications_info()


def draw_filled_cells(pattern_height):
    """Draw filled Voronoi cells - perfect for solid fabric patterns"""
    colors = textile_color_schemes[current_scheme]

    # Sample the Voronoi diagram by checking each pixel
    py5.load_pixels()

    for y in range(int(pattern_height)):
        for x in range(py5.width):
            closest_point = find_closest_point(x, y)
            if closest_point:
                color = colors[closest_point.color_index % len(colors)]

                # Add subtle variation for textile texture
                if cell_size_variation:
                    distance = get_distance_to_closest(x, y)
                    variation = py5.sin(
                        distance * 0.1 + time_offset * 0.05) * 20
                    color = (
                        max(0, min(255, color[0] + variation)),
                        max(0, min(255, color[1] + variation)),
                        max(0, min(255, color[2] + variation))
                    )

                pixel_index = x + y * py5.width
                if 0 <= pixel_index < len(py5.pixels):
                    py5.pixels[pixel_index] = py5.color(
                        color[0], color[1], color[2])

    py5.update_pixels()


def draw_outlined_cells(pattern_height):
    """Draw outlined Voronoi cells - perfect for laser-cut patterns"""
    py5.background(255)
    py5.stroke(0)
    py5.stroke_weight(cell_thickness)
    py5.no_fill()

    # Draw cell boundaries by finding edges
    for y in range(0, int(pattern_height), 2):
        for x in range(0, py5.width, 2):
            closest_point = find_closest_point(x, y)

            # Check neighboring pixels for boundaries
            neighbors = [
                find_closest_point(x + 2, y),
                find_closest_point(x, y + 2),
                find_closest_point(x - 2, y),
                find_closest_point(x, y - 2)
            ]

            for neighbor in neighbors:
                if neighbor and neighbor != closest_point:
                    py5.point(x, y)
                    break


def draw_gradient_cells(pattern_height):
    """Draw gradient-filled cells - perfect for organic jewelry patterns"""
    colors = textile_color_schemes[current_scheme]

    py5.load_pixels()

    for y in range(int(pattern_height)):
        for x in range(py5.width):
            closest_point = find_closest_point(x, y)
            if closest_point:
                distance = math.sqrt((x - closest_point.x)
                                     ** 2 + (y - closest_point.y)**2)

                # Create gradient based on distance to center
                max_distance = 100  # Adjust for gradient spread
                gradient_factor = max(0, min(1, distance / max_distance))

                base_color = colors[closest_point.color_index % len(colors)]
                white = (255, 255, 255)

                # Interpolate between base color and white
                color = (
                    int(base_color[0] * (1 - gradient_factor) +
                        white[0] * gradient_factor),
                    int(base_color[1] * (1 - gradient_factor) +
                        white[1] * gradient_factor),
                    int(base_color[2] * (1 - gradient_factor) +
                        white[2] * gradient_factor)
                )

                pixel_index = x + y * py5.width
                if 0 <= pixel_index < len(py5.pixels):
                    py5.pixels[pixel_index] = py5.color(
                        color[0], color[1], color[2])

    py5.update_pixels()


def draw_textured_cells(pattern_height):
    """Draw textured cells - perfect for breathable fabric designs"""
    colors = textile_color_schemes[current_scheme]

    py5.load_pixels()

    for y in range(int(pattern_height)):
        for x in range(py5.width):
            closest_point = find_closest_point(x, y)
            if closest_point:
                # Create texture using noise
                texture = py5.noise(x * 0.02, y * 0.02, time_offset * 0.01)
                distance = math.sqrt((x - closest_point.x)
                                     ** 2 + (y - closest_point.y)**2)

                # Combine texture with distance for organic feel
                texture_factor = texture * (1 - min(1, distance / 80))

                base_color = colors[closest_point.color_index % len(colors)]

                # Apply texture
                color = (
                    int(base_color[0] * (0.5 + 0.5 * texture_factor)),
                    int(base_color[1] * (0.5 + 0.5 * texture_factor)),
                    int(base_color[2] * (0.5 + 0.5 * texture_factor))
                )

                pixel_index = x + y * py5.width
                if 0 <= pixel_index < len(py5.pixels):
                    py5.pixels[pixel_index] = py5.color(
                        color[0], color[1], color[2])

    py5.update_pixels()


def draw_seed_points(pattern_height):
    """Draw the Voronoi seed points"""
    py5.fill(255, 0, 0)
    py5.stroke(255)
    py5.stroke_weight(2)

    for point in voronoi_points:
        if 0 <= point.y <= pattern_height:
            py5.circle(point.x, point.y, 8)


def find_closest_point(x, y):
    """Find the closest Voronoi point to given coordinates"""
    if not voronoi_points:
        return None

    closest_point = voronoi_points[0]
    min_distance = math.sqrt((x - closest_point.x) **
                             2 + (y - closest_point.y)**2)

    for point in voronoi_points[1:]:
        distance = math.sqrt((x - point.x)**2 + (y - point.y)**2)
        if distance < min_distance:
            min_distance = distance
            closest_point = point

    return closest_point


def get_distance_to_closest(x, y):
    """Get distance to closest point"""
    closest_point = find_closest_point(x, y)
    if closest_point:
        return math.sqrt((x - closest_point.x)**2 + (y - closest_point.y)**2)
    return 0


def generate_voronoi_points():
    """Generate random Voronoi seed points"""
    global voronoi_points
    voronoi_points = []

    pattern_height = py5.height - 150

    for _ in range(num_points):
        x = random.uniform(50, py5.width - 50)
        y = random.uniform(50, pattern_height - 50)
        voronoi_points.append(VoronoiPoint(x, y))

    print(f"Generated {num_points} Voronoi points")


def draw_interface():
    """Draw the user interface"""
    py5.fill(0)
    py5.text_size(16)
    py5.text_align(py5.LEFT)

    mode_names = ["Filled Cells", "Outlined Cells",
                  "Gradient Cells", "Textured Cells"]
    py5.text(
        f"Voronoi Textile Pattern - Mode: {mode_names[pattern_mode]}", 20, 25)
    py5.text(
        f"Color Scheme: {current_scheme.replace('_', ' ').title()}", 20, 45)
    py5.text(
        f"Points: {num_points} | Animation: {'ON' if animate_points else 'OFF'}", 20, 65)
    py5.text("SPACE=Mode, C=Colors, A=Animate, P=Points, R=Regenerate, S=Save", 20, 85)


def draw_applications_info():
    """Show textile applications"""
    py5.fill(100)
    py5.text_size(12)
    py5.text_align(py5.LEFT)

    app_y = py5.height - 40
    applications = [
        "Laser-Cut Fabric", "Breathable Garments", "Jewelry Patterns", "Fashion Panels", "3D Accessories"
    ]

    py5.text("Textile Applications:", 20, app_y)
    for i, app in enumerate(applications):
        py5.text(f"• {app}", 20 + i * 140, app_y + 20)


def key_pressed():
    global pattern_mode, current_scheme, animate_points, show_points, num_points

    if py5.key == ' ':
        pattern_mode = (pattern_mode + 1) % 4
        mode_names = ["Filled Cells", "Outlined Cells",
                      "Gradient Cells", "Textured Cells"]
        print(f"Pattern mode: {mode_names[pattern_mode]}")

    elif py5.key == 'c' or py5.key == 'C':
        schemes = list(textile_color_schemes.keys())
        current_index = schemes.index(current_scheme)
        current_scheme = schemes[(current_index + 1) % len(schemes)]
        print(f"Color scheme: {current_scheme}")

    elif py5.key == 'a' or py5.key == 'A':
        animate_points = not animate_points
        print(f"Animation: {'ON' if animate_points else 'OFF'}")

    elif py5.key == 'p' or py5.key == 'P':
        show_points = not show_points
        print(f"Show points: {'ON' if show_points else 'OFF'}")

    elif py5.key == 'r' or py5.key == 'R':
        generate_voronoi_points()

    elif py5.key == 's' or py5.key == 'S':
        filename = f"voronoi_textile_{current_scheme}_{pattern_mode}_####.png"
        py5.save_frame(filename)
        print(f"Voronoi pattern saved as: {filename}")

    elif py5.key == '+' or py5.key == '=':
        num_points = min(50, num_points + 5)
        generate_voronoi_points()

    elif py5.key == '-' or py5.key == '_':
        num_points = max(5, num_points - 5)
        generate_voronoi_points()


def mouse_pressed():
    """Add new Voronoi point at mouse position"""
    pattern_y = 100
    pattern_height = py5.height - 150

    if pattern_y <= py5.mouse_y <= pattern_y + pattern_height:
        new_point = VoronoiPoint(py5.mouse_x, py5.mouse_y - pattern_y)
        voronoi_points.append(new_point)
        print(f"Added point at ({py5.mouse_x}, {py5.mouse_y - pattern_y})")


if __name__ == "__main__":
    py5.run_sketch()

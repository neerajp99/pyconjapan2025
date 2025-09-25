#!/usr/bin/env python3
"""
3D Voronoi Flower Earring Designer
Based on Roni Kaufman's Voronoi flowers algorithm
Generates 3D printable earring designs with organic flower patterns
"""

from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import math
import json
import io
import base64
from datetime import datetime
import uuid
import trimesh
from scipy.spatial.distance import cdist
from scipy.spatial import Voronoi, voronoi_plot_2d
import random

app = Flask(__name__, template_folder='../templates',
            static_folder='../static')
app.config['SECRET_KEY'] = 'voronoi-3d-flowers-key'


class Voronoi3DFlowers:
    """Generate 3D Voronoi flower patterns for earring designs"""

    def __init__(self):
        self.golden_ratio = (1 + math.sqrt(5)) / 2

        # Default parameters based on original JS code
        self.n_flowers = 18
        self.n_petals = 12
        self.margin = 0.1  # 10% margin in normalized coordinates

        # 3D specific parameters
        self.base_thickness = 2.0  # mm
        self.petal_height = 1.5    # mm
        self.center_height = 2.5   # mm

        # Earring dimensions (in mm)
        self.earring_sizes = {
            'small': {'width': 15, 'height': 20, 'thickness': 3},
            'medium': {'width': 20, 'height': 25, 'thickness': 4},
            'large': {'width': 25, 'height': 30, 'thickness': 5}
        }

        # Material properties for 3D printing
        self.materials = {
            'PLA': {'min_thickness': 0.8, 'detail_level': 0.2},
            'PETG': {'min_thickness': 1.0, 'detail_level': 0.3},
            'Resin': {'min_thickness': 0.4, 'detail_level': 0.1}
        }

    def generate_centroids(self, width, height, n_flowers=None):
        """Generate initial random centroids for flowers"""
        if n_flowers is None:
            n_flowers = self.n_flowers

        centroids = []
        margin_x = width * self.margin
        margin_y = height * self.margin

        for i in range(n_flowers):
            x0 = random.uniform(margin_x, width - margin_x)
            y0 = random.uniform(margin_y, height - margin_y)
            theta0 = random.uniform(0, 2 * math.pi)

            # Create list of petal angles (arcs_left equivalent)
            petal_indices = list(range(self.n_petals))
            random.shuffle(petal_indices)

            centroids.append({
                'x0': x0,
                'y0': y0,
                'theta0': theta0,
                'id': i,
                'arcs_left': petal_indices.copy(),
                'petal_ends': []
            })

        return centroids

    def voronoi_relaxation(self, centroids, width, height, iterations=3):
        """Apply Lloyd's relaxation to distribute centroids more evenly"""
        for _ in range(iterations):
            # Create grid for sampling
            n_samples = 20
            step_x = width / n_samples
            step_y = height / n_samples

            # Initialize voronoi cells
            voronoi_cells = [[] for _ in range(len(centroids))]

            # Sample points and assign to closest centroid
            for i in range(n_samples):
                x = (i + 0.5) * step_x
                for j in range(n_samples):
                    y = (j + 0.5) * step_y
                    closest_id = self.closest_centroid_id(x, y, centroids)
                    voronoi_cells[closest_id].append([x, y])

            # Update centroid positions to cell centers
            margin_x = width * self.margin
            margin_y = height * self.margin

            for i, centroid in enumerate(centroids):
                cell_points = voronoi_cells[i]
                if cell_points:
                    x_sum = sum(p[0] for p in cell_points)
                    y_sum = sum(p[1] for p in cell_points)

                    new_x = np.clip(x_sum / len(cell_points),
                                    margin_x, width - margin_x)
                    new_y = np.clip(y_sum / len(cell_points),
                                    margin_y, height - margin_y)

                    centroid['x0'] = new_x
                    centroid['y0'] = new_y

    def closest_centroid_id(self, x, y, centroids):
        """Find the closest centroid to a given point"""
        min_dist = float('inf')
        closest_id = 0

        for centroid in centroids:
            dist_sq = (centroid['x0'] - x) ** 2 + (centroid['y0'] - y) ** 2
            if dist_sq < min_dist:
                min_dist = dist_sq
                closest_id = centroid['id']

        return closest_id

    def longest_possible_radius(self, centroid, theta, centroids, width, height):
        """Calculate the longest possible radius for a petal in given direction"""
        x0, y0 = centroid['x0'], centroid['y0']
        r = 0
        r_step = 0.5  # Smaller step for more precision

        # Maximum possible radius based on canvas bounds
        r_max = min(
            min(x0, width - x0),
            min(y0, height - y0)
        )

        while r < r_max:
            r += r_step
            x = x0 + r * math.cos(theta)
            y = y0 + r * math.sin(theta)

            # Check if we've left the canvas
            if x < 0 or x > width or y < 0 or y > height:
                break

            # Check if we've entered another centroid's territory
            if self.closest_centroid_id(x, y, centroids) != centroid['id']:
                break

        return max(0, r - r_step)

    def generate_flower_petals(self, centroids, width, height):
        """Generate all flower petals following the original algorithm"""
        petal_ends = []

        # Process each centroid
        for centroid in centroids:
            while centroid['arcs_left']:
                # Get next petal angle
                petal_idx = centroid['arcs_left'].pop()
                theta = (2 * math.pi * petal_idx / self.n_petals) + \
                    centroid['theta0']

                # Calculate maximum radius for this direction
                r_max = self.longest_possible_radius(
                    centroid, theta, centroids, width, height)

                # Generate petal circles along the radius
                r = 0
                petal_circles = []

                while r < r_max:
                    x = centroid['x0'] + r * math.cos(theta)
                    y = centroid['y0'] + r * math.sin(theta)

                    # Calculate circle diameter based on radius and petal angle
                    d = r * math.sin(2 * math.pi / self.n_petals)

                    # Check bounds
                    margin = min(width, height) * self.margin * 0.5
                    if (x < margin or x > width - margin or
                            y < margin or y > height - margin):
                        break

                    # Check intersection with other petal ends
                    intersects = False
                    for p in petal_ends:
                        if (p['id'] != centroid['id'] and
                                math.sqrt((x - p['x'])**2 + (y - p['y'])**2) < (d/2 + p['d']/2 + 1.5)):
                            intersects = True
                            break

                    if intersects:
                        break

                    petal_circles.append({'x': x, 'y': y, 'd': d, 'r': r})
                    r += 1

                # Store the end of this petal
                if petal_circles:
                    last_circle = petal_circles[-1]
                    petal_ends.append({
                        'x': last_circle['x'],
                        'y': last_circle['y'],
                        'd': last_circle['d'],
                        'id': centroid['id']
                    })

                    # Store petal data in centroid
                    centroid['petal_ends'].extend(petal_circles)

        return petal_ends

    def create_3d_flower_geometry(self, centroids, petal_ends, size_config):
        """Convert 2D flower pattern to 3D geometry"""
        vertices = []
        faces = []
        vertex_offset = 0

        width = size_config['width']
        height = size_config['height']
        thickness = size_config['thickness']

        # Create base plate
        base_verts, base_faces = self._create_base_plate(
            width, height, thickness)
        vertices.extend(base_verts)
        faces.extend(base_faces)
        vertex_offset += len(base_verts)

        # Create 3D petals
        for centroid in centroids:
            # Create flower center
            center_verts, center_faces = self._create_flower_center(
                centroid, petal_ends, width, height, thickness, vertex_offset
            )
            vertices.extend(center_verts)
            faces.extend([[f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset]
                         for f in center_faces])
            vertex_offset += len(center_verts)

            # Create petals and connections
            center_petals = [
                p for p in petal_ends if p['id'] == centroid['id']]
            if center_petals:
                avg_diameter = sum(p['d']
                                   for p in center_petals) / len(center_petals)
                center_radius = avg_diameter / self.n_petals

                for petal_circle in centroid['petal_ends']:
                    # Create the petal
                    petal_verts, petal_faces = self._create_3d_petal(
                        petal_circle, width, height, thickness, vertex_offset
                    )
                    vertices.extend(petal_verts)
                    faces.extend([[f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset]
                                 for f in petal_faces])
                    vertex_offset += len(petal_verts)

                    # Create connection between center and petal
                    connection_verts, connection_faces = self._create_petal_connection(
                        centroid['x0'], centroid['y0'], center_radius,
                        petal_circle['x'], petal_circle['y'], petal_circle['d'] / 2,
                        thickness, self.petal_height
                    )
                    vertices.extend(connection_verts)
                    faces.extend([[f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset]
                                 for f in connection_faces])
                    vertex_offset += len(connection_verts)

        return np.array(vertices), np.array(faces)

    def _create_base_plate(self, width, height, thickness):
        """Create the base plate for the earring"""
        vertices = [
            [0, 0, 0],
            [width, 0, 0],
            [width, height, 0],
            [0, height, 0],
            [0, 0, thickness],
            [width, 0, thickness],
            [width, height, thickness],
            [0, height, thickness]
        ]

        faces = [
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ]

        return vertices, faces

    def _create_flower_center(self, centroid, petal_ends, width, height, thickness, vertex_offset):
        """Create 3D geometry for flower center"""
        # Calculate center size based on petal ends
        center_petals = [p for p in petal_ends if p['id'] == centroid['id']]
        if not center_petals:
            return [], []

        avg_diameter = sum(p['d'] for p in center_petals) / len(center_petals)
        center_radius = avg_diameter / self.n_petals

        # Create cylinder for flower center
        return self._create_cylinder(
            centroid['x0'], centroid['y0'], center_radius,
            thickness, thickness + self.center_height, 12
        )

    def _create_3d_petal(self, petal_circle, width, height, thickness, vertex_offset):
        """Create 3D geometry for a single petal circle"""
        return self._create_cylinder(
            petal_circle['x'], petal_circle['y'], petal_circle['d'] / 2,
            thickness, thickness + self.petal_height, 8
        )

    def _create_petal_connection(self, center_x, center_y, center_radius, petal_x, petal_y, petal_radius, thickness, height):
        """Create connecting geometry between flower center and petal"""
        vertices = []
        faces = []

        # Calculate connection points
        dx = petal_x - center_x
        dy = petal_y - center_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            return vertices, faces

        # Normalize direction vector
        dx_norm = dx / distance
        dy_norm = dy / distance

        # Calculate connection points on center and petal circumferences
        center_connect_x = center_x + center_radius * dx_norm
        center_connect_y = center_y + center_radius * dy_norm
        petal_connect_x = petal_x - petal_radius * dx_norm
        petal_connect_y = petal_y - petal_radius * dy_norm

        # Create connecting beam with rectangular cross-section
        beam_width = min(center_radius, petal_radius) * 0.6
        beam_height = height * 0.8

        # Calculate perpendicular vector for beam width
        perp_x = -dy_norm * beam_width / 2
        perp_y = dx_norm * beam_width / 2

        # Create vertices for the connecting beam
        z_bottom = thickness
        z_top = thickness + beam_height

        # Bottom face vertices
        vertices.extend([
            [center_connect_x + perp_x, center_connect_y + perp_y, z_bottom],  # 0
            [center_connect_x - perp_x, center_connect_y - perp_y, z_bottom],  # 1
            [petal_connect_x - perp_x, petal_connect_y - perp_y, z_bottom],    # 2
            [petal_connect_x + perp_x, petal_connect_y + perp_y, z_bottom]     # 3
        ])

        # Top face vertices
        vertices.extend([
            [center_connect_x + perp_x, center_connect_y + perp_y, z_top],     # 4
            [center_connect_x - perp_x, center_connect_y - perp_y, z_top],     # 5
            [petal_connect_x - perp_x, petal_connect_y - perp_y, z_top],       # 6
            [petal_connect_x + perp_x, petal_connect_y + perp_y, z_top]        # 7
        ])

        # Create faces for the connecting beam
        faces.extend([
            # Bottom face
            [0, 2, 1], [0, 3, 2],
            # Top face
            [4, 5, 6], [4, 6, 7],
            # Side faces
            [0, 1, 5], [0, 5, 4],  # Left side
            [2, 3, 7], [2, 7, 6],  # Right side
            [1, 2, 6], [1, 6, 5],  # Front side
            [3, 0, 4], [3, 4, 7]   # Back side
        ])

        return vertices, faces

    def _create_cylinder(self, x, y, radius, z_bottom, z_top, segments=12):
        """Create a cylinder at given position"""
        vertices = []
        faces = []

        # Create vertices
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # Bottom circle
            vertices.append([x + radius * cos_a, y + radius * sin_a, z_bottom])
            # Top circle
            vertices.append([x + radius * cos_a, y + radius * sin_a, z_top])

        # Center vertices
        vertices.append([x, y, z_bottom])  # bottom center
        vertices.append([x, y, z_top])     # top center

        bottom_center = len(vertices) - 2
        top_center = len(vertices) - 1

        # Create faces
        for i in range(segments):
            next_i = (i + 1) % segments

            # Side faces (two triangles per segment)
            faces.append([i * 2, next_i * 2, i * 2 + 1])
            faces.append([next_i * 2, next_i * 2 + 1, i * 2 + 1])

            # Bottom face
            faces.append([bottom_center, next_i * 2, i * 2])

            # Top face
            faces.append([top_center, i * 2 + 1, next_i * 2 + 1])

        return vertices, faces

    def create_earring_design(self, size='medium', n_flowers=None, material='PLA'):
        """Create complete 3D earring design"""
        if n_flowers is None:
            n_flowers = self.n_flowers

        size_config = self.earring_sizes[size]
        width, height = size_config['width'], size_config['height']

        # Generate and relax centroids
        centroids = self.generate_centroids(width, height, n_flowers)
        self.voronoi_relaxation(centroids, width, height)

        # Generate flower petals
        petal_ends = self.generate_flower_petals(centroids, width, height)

        # Create 3D geometry
        vertices, faces = self.create_3d_flower_geometry(
            centroids, petal_ends, size_config)

        return {
            'vertices': vertices.tolist(),
            'faces': faces.tolist(),
            'centroids': centroids,
            'petal_ends': petal_ends,
            'size_config': size_config,
            'material': material
        }


# Global instance
voronoi_designer = Voronoi3DFlowers()


@app.route('/')
def index():
    return render_template('voronoi_designer.html')


@app.route('/generate_earring', methods=['POST'])
def generate_earring():
    try:
        data = request.json
        size = data.get('size', 'medium')
        n_flowers = data.get('n_flowers', 18)
        material = data.get('material', 'PLA')

        print(
            f"Generating earring: size={size}, n_flowers={n_flowers}, material={material}")

        design = voronoi_designer.create_earring_design(
            size, n_flowers, material)

        print(
            f"Generated design with {len(design['vertices'])} vertices and {len(design['faces'])} faces")

        return jsonify({
            'success': True,
            'design': design
        })
    except Exception as e:
        print(f"Error generating earring: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/export_stl', methods=['POST'])
def export_stl():
    try:
        data = request.json
        vertices = np.array(data['vertices'])
        faces = np.array(data['faces'])

        # Create trimesh object
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voronoi_earring_{timestamp}.stl"

        # Export to STL
        stl_data = mesh.export(file_type='stl')

        # Save to output directory
        output_path = f"/Users/neeraj/Desktop/pyconjp25/voronoi/output/stl/{filename}"
        with open(output_path, 'wb') as f:
            f.write(stl_data)

        return send_file(
            io.BytesIO(stl_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("🌸 3D Voronoi Flower Earring Designer")
    print("=" * 50)
    print("🎨 Based on Roni Kaufman's algorithm")
    print("💎 3D printable earring designs")
    print("🌺 Organic Voronoi flower patterns")
    print("🖨️  STL export for 3D printing")
    print("📱 Open: http://localhost:8081")
    print("=" * 50)

    app.run(host='0.0.0.0', port=8081, debug=True)

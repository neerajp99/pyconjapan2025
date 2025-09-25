#!/usr/bin/env python3
"""
Modern 3D Printable Cap & Hat Designer
Realistic headwear with contemporary patterns and comfort features
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
from scipy.optimize import minimize

app = Flask(__name__)
app.config['SECRET_KEY'] = 'modern-cap-designer-key'

class ModernCapDesigner:
    """Generate realistic 3D printable caps and hats with modern patterns"""
    
    def __init__(self):
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        
        # Standard cap dimensions (in cm)
        self.cap_dimensions = {
            'baseball': {'crown_height': 11, 'crown_diameter': 18, 'brim_width': 7, 'brim_curve': 0.3},
            'beanie': {'crown_height': 20, 'crown_diameter': 18, 'brim_width': 2, 'brim_curve': 0.1},
            'bucket': {'crown_height': 12, 'crown_diameter': 18, 'brim_width': 6, 'brim_curve': -0.2},
            'snapback': {'crown_height': 12, 'crown_diameter': 18, 'brim_width': 7, 'brim_curve': 0.2}
        }
        
        # Pattern packing densities
        self.packing_types = {
            'close_packed': {'density': 0.85, 'hole_ratio': 0.3, 'spacing': 0.8},
            'medium_packed': {'density': 0.65, 'hole_ratio': 0.5, 'spacing': 1.2},
            'loose_packed': {'density': 0.45, 'hole_ratio': 0.7, 'spacing': 1.8}
        }
        
        # Material properties for 3D printing
        self.materials = {
            'PLA': {'flexibility': 0.2, 'strength': 0.8, 'breathability': 0.3},
            'PETG': {'flexibility': 0.5, 'strength': 0.7, 'breathability': 0.4},
            'TPU': {'flexibility': 0.9, 'strength': 0.4, 'breathability': 0.8}
        }
    
    def create_cap_base_geometry(self, cap_style='baseball', head_circumference=58):
        """Create realistic cap base geometry that follows natural head shape"""
        dims = self.cap_dimensions[cap_style]
        
        # Calculate scaling factor based on head circumference
        scale_factor = head_circumference / 58.0  # 58cm is average
        head_radius = (head_circumference / (2 * math.pi)) * scale_factor
        
        vertices = []
        faces = []
        
        if cap_style == 'baseball':
            vertices, faces = self._create_baseball_cap_geometry(head_radius, scale_factor)
        elif cap_style == 'beanie':
            vertices, faces = self._create_beanie_geometry(head_radius, scale_factor)
        elif cap_style == 'bucket':
            vertices, faces = self._create_bucket_hat_geometry(head_radius, scale_factor)
        elif cap_style == 'snapback':
            vertices, faces = self._create_snapback_geometry(head_radius, scale_factor)
        else:
            vertices, faces = self._create_baseball_cap_geometry(head_radius, scale_factor)
        
        return np.array(vertices), np.array(faces)
    
    def _create_baseball_cap_geometry(self, head_radius, scale_factor):
        """Create realistic baseball cap following head contour"""
        vertices = []
        faces = []
        
        # Parameters for realistic baseball cap
        crown_height = 6 * scale_factor  # Much lower profile
        brim_length = 7 * scale_factor
        brim_curve = 0.4  # Natural curve
        
        # Create crown that follows head shape
        phi_steps = 48  # Higher resolution for smooth curves
        theta_steps = 20
        
        # Crown follows elliptical head shape, not sphere
        for i in range(theta_steps + 1):
            # Use elliptical profile instead of circular
            t = i / theta_steps
            
            # Create natural head-following curve
            if t < 0.7:  # Main crown area
                height_factor = math.sin(t * math.pi * 0.7) * 0.8
                radius_factor = 1.0 - (t * 0.2)  # Slight taper
            else:  # Transition to brim
                height_factor = 0.1 + (1 - t) * 0.5
                radius_factor = 1.0
            
            current_radius = head_radius * radius_factor
            current_height = crown_height * height_factor
            
            for j in range(phi_steps):
                phi = (j / phi_steps) * 2 * math.pi
                
                x = current_radius * math.cos(phi)
                y = current_radius * math.sin(phi)
                z = current_height
                
                vertices.append([x, y, z])
        
        # Generate crown faces
        for i in range(theta_steps):
            for j in range(phi_steps):
                v1 = i * phi_steps + j
                v2 = i * phi_steps + ((j + 1) % phi_steps)
                v3 = (i + 1) * phi_steps + ((j + 1) % phi_steps)
                v4 = (i + 1) * phi_steps + j
                
                faces.extend([[v1, v2, v3], [v1, v3, v4]])
        
        # Create realistic curved brim (front only for baseball cap)
        brim_vertices, brim_faces = self._create_realistic_brim(
            head_radius, brim_length, brim_curve, len(vertices), 'baseball'
        )
        vertices.extend(brim_vertices)
        faces.extend(brim_faces)
        
        return vertices, faces
    
    def _create_beanie_geometry(self, head_radius, scale_factor):
        """Create form-fitting beanie geometry"""
        vertices = []
        faces = []
        
        # Beanie parameters - close fitting
        crown_height = 12 * scale_factor
        phi_steps = 40
        theta_steps = 25
        
        for i in range(theta_steps + 1):
            t = i / theta_steps
            
            # Beanie follows head closely then tapers
            if t < 0.6:  # Head-fitting portion
                height_factor = t * 0.3
                radius_factor = 1.0 - (t * 0.05)  # Very slight taper
            else:  # Tapering crown
                height_factor = 0.18 + (t - 0.6) * 2.0
                radius_factor = 1.0 - ((t - 0.6) * 1.5)  # Taper to point
            
            current_radius = head_radius * max(0.1, radius_factor)
            current_height = crown_height * height_factor
            
            for j in range(phi_steps):
                phi = (j / phi_steps) * 2 * math.pi
                
                x = current_radius * math.cos(phi)
                y = current_radius * math.sin(phi)
                z = current_height
                
                vertices.append([x, y, z])
        
        # Generate faces
        for i in range(theta_steps):
            for j in range(phi_steps):
                v1 = i * phi_steps + j
                v2 = i * phi_steps + ((j + 1) % phi_steps)
                v3 = (i + 1) * phi_steps + ((j + 1) % phi_steps)
                v4 = (i + 1) * phi_steps + j
                
                faces.extend([[v1, v2, v3], [v1, v3, v4]])
        
        return vertices, faces
    
    def _create_bucket_hat_geometry(self, head_radius, scale_factor):
        """Create bucket hat with wide, angled brim"""
        vertices = []
        faces = []
        
        # Bucket hat parameters
        crown_height = 8 * scale_factor
        brim_width = 6 * scale_factor
        brim_angle = -0.3  # Downward angle
        
        # Create cylindrical crown
        phi_steps = 40
        height_steps = 15
        
        for i in range(height_steps + 1):
            t = i / height_steps
            current_height = crown_height * t
            
            # Slight taper for natural look
            radius_factor = 1.0 - (t * 0.1)
            current_radius = head_radius * radius_factor
            
            for j in range(phi_steps):
                phi = (j / phi_steps) * 2 * math.pi
                
                x = current_radius * math.cos(phi)
                y = current_radius * math.sin(phi)
                z = current_height
                
                vertices.append([x, y, z])
        
        # Generate crown faces
        for i in range(height_steps):
            for j in range(phi_steps):
                v1 = i * phi_steps + j
                v2 = i * phi_steps + ((j + 1) % phi_steps)
                v3 = (i + 1) * phi_steps + ((j + 1) % phi_steps)
                v4 = (i + 1) * phi_steps + j
                
                faces.extend([[v1, v2, v3], [v1, v3, v4]])
        
        # Create wide angled brim
        brim_vertices, brim_faces = self._create_realistic_brim(
            head_radius, brim_width, brim_angle, len(vertices), 'bucket'
        )
        vertices.extend(brim_vertices)
        faces.extend(brim_faces)
        
        return vertices, faces
    
    def _create_snapback_geometry(self, head_radius, scale_factor):
        """Create structured snapback cap"""
        vertices = []
        faces = []
        
        # Snapback parameters - more structured
        crown_height = 7 * scale_factor
        brim_length = 7.5 * scale_factor
        
        # Create structured crown with panels
        phi_steps = 48
        theta_steps = 18
        
        for i in range(theta_steps + 1):
            t = i / theta_steps
            
            # More structured, less curved than baseball
            if t < 0.8:
                height_factor = t * 0.9
                radius_factor = 1.0 - (t * 0.15)
            else:
                height_factor = 0.72 + (t - 0.8) * 0.5
                radius_factor = 0.85
            
            current_radius = head_radius * radius_factor
            current_height = crown_height * height_factor
            
            for j in range(phi_steps):
                phi = (j / phi_steps) * 2 * math.pi
                
                x = current_radius * math.cos(phi)
                y = current_radius * math.sin(phi)
                z = current_height
                
                vertices.append([x, y, z])
        
        # Generate faces
        for i in range(theta_steps):
            for j in range(phi_steps):
                v1 = i * phi_steps + j
                v2 = i * phi_steps + ((j + 1) % phi_steps)
                v3 = (i + 1) * phi_steps + ((j + 1) % phi_steps)
                v4 = (i + 1) * phi_steps + j
                
                faces.extend([[v1, v2, v3], [v1, v3, v4]])
        
        # Create flat brim
        brim_vertices, brim_faces = self._create_realistic_brim(
            head_radius, brim_length, 0.1, len(vertices), 'snapback'
        )
        vertices.extend(brim_vertices)
        faces.extend(brim_faces)
        
        return vertices, faces
    
    def _create_realistic_brim(self, head_radius, brim_length, curve_factor, vertex_offset, cap_style):
        """Create realistic thin brim with natural curvature"""
        vertices = []
        faces = []
        
        if cap_style == 'baseball':
            # Baseball cap - front brim only (120 degrees)
            angle_start = -math.pi/3
            angle_end = math.pi/3
            segments = 32
        elif cap_style == 'bucket':
            # Bucket hat - full circular brim
            angle_start = 0
            angle_end = 2 * math.pi
            segments = 64
        elif cap_style == 'snapback':
            # Snapback - front brim only, flatter
            angle_start = -math.pi/3
            angle_end = math.pi/3
            segments = 32
        else:
            # Default to baseball style
            angle_start = -math.pi/3
            angle_end = math.pi/3
            segments = 32
        
        radial_segments = 6  # Thin brim
        
        # Create brim vertices
        for i in range(radial_segments + 1):
            radius_factor = i / radial_segments
            current_radius = head_radius + (brim_length * radius_factor)
            
            # Natural brim curve - more pronounced at edges
            curve_height = curve_factor * (radius_factor ** 1.5) * brim_length * 0.2
            
            for j in range(segments + 1):
                if cap_style in ['baseball', 'snapback']:
                    # Front brim only
                    angle = angle_start + (j / segments) * (angle_end - angle_start)
                else:
                    # Full circular brim
                    angle = (j / segments) * 2 * math.pi
                
                x = current_radius * math.cos(angle)
                y = current_radius * math.sin(angle)
                z = curve_height
                
                vertices.append([x, y, z])
        
        # Generate brim faces
        for i in range(radial_segments):
            for j in range(segments):
                v1 = vertex_offset + i * (segments + 1) + j
                v2 = vertex_offset + i * (segments + 1) + (j + 1)
                v3 = vertex_offset + (i + 1) * (segments + 1) + (j + 1)
                v4 = vertex_offset + (i + 1) * (segments + 1) + j
                
                faces.extend([[v1, v2, v3], [v1, v3, v4]])
        
        return vertices, faces
    
    def apply_modern_pattern(self, vertices, faces, pattern_type='mesh', packing='medium_packed'):
        """Apply contemporary patterns with different packing densities"""
        packing_config = self.packing_types[packing]
        
        if pattern_type == 'mesh':
            return self._create_mesh_pattern(vertices, faces, packing_config)
        elif pattern_type == 'perforated':
            return self._create_perforated_pattern(vertices, faces, packing_config)
        elif pattern_type == 'geometric':
            return self._create_geometric_pattern(vertices, faces, packing_config)
        elif pattern_type == 'organic':
            return self._create_organic_pattern(vertices, faces, packing_config)
        else:
            return vertices, faces
    
    def _create_mesh_pattern(self, vertices, faces, packing_config):
        """Create modern mesh pattern like athletic caps"""
        new_vertices = []
        new_faces = []
        
        # Create diamond/hexagonal mesh openings
        mesh_size = 3.0 * packing_config['spacing']  # mm
        wall_thickness = 0.8  # mm
        
        # Sample points on the surface for mesh placement
        for face in faces:
            face_vertices = vertices[face]
            center = np.mean(face_vertices, axis=0)
            
            # Only apply mesh to crown area (z > 2)
            if center[2] > 2:
                # Create mesh opening
                mesh_verts, mesh_faces = self._create_mesh_cell(
                    center, mesh_size, wall_thickness, len(new_vertices)
                )
                new_vertices.extend(mesh_verts)
                new_faces.extend(mesh_faces)
        
        return np.array(new_vertices), np.array(new_faces)
    
    def _create_perforated_pattern(self, vertices, faces, packing_config):
        """Create perforated pattern with circular holes"""
        new_vertices = list(vertices)
        new_faces = []
        
        hole_diameter = 2.0 * packing_config['hole_ratio']  # mm
        hole_spacing = 4.0 * packing_config['spacing']  # mm
        
        # Create regular grid of holes
        for face in faces:
            face_vertices = vertices[face]
            center = np.mean(face_vertices, axis=0)
            
            # Check if this area should have holes
            if self._should_place_hole(center, hole_spacing, packing_config['density']):
                # Create circular hole
                hole_verts, hole_faces = self._create_circular_hole(
                    center, hole_diameter/2, len(new_vertices)
                )
                new_vertices.extend(hole_verts)
                new_faces.extend(hole_faces)
            else:
                # Keep original face
                new_faces.append(face)
        
        return np.array(new_vertices), np.array(new_faces)
    
    def _create_geometric_pattern(self, vertices, faces, packing_config):
        """Create modern geometric patterns"""
        new_vertices = list(vertices)
        new_faces = []
        
        # Create triangular or hexagonal cutouts
        pattern_size = 3.0 * packing_config['spacing']
        
        for face in faces:
            face_vertices = vertices[face]
            center = np.mean(face_vertices, axis=0)
            
            if self._should_place_pattern(center, pattern_size, packing_config['density']):
                # Create geometric cutout
                pattern_verts, pattern_faces = self._create_geometric_cutout(
                    center, pattern_size, len(new_vertices)
                )
                new_vertices.extend(pattern_verts)
                new_faces.extend(pattern_faces)
            else:
                new_faces.append(face)
        
        return np.array(new_vertices), np.array(new_faces)
    
    def _create_organic_pattern(self, vertices, faces, packing_config):
        """Create organic, flowing patterns"""
        new_vertices = list(vertices)
        new_faces = []
        
        # Create flowing, organic openings
        for face in faces:
            face_vertices = vertices[face]
            center = np.mean(face_vertices, axis=0)
            
            # Use noise function for organic placement
            if self._organic_pattern_placement(center, packing_config):
                organic_verts, organic_faces = self._create_organic_opening(
                    center, packing_config, len(new_vertices)
                )
                new_vertices.extend(organic_verts)
                new_faces.extend(organic_faces)
            else:
                new_faces.append(face)
        
        return np.array(new_vertices), np.array(new_faces)
    
    def _create_mesh_cell(self, center, size, thickness, vertex_offset):
        """Create a single mesh cell"""
        vertices = []
        faces = []
        
        # Create diamond-shaped opening
        half_size = size / 2
        
        # Outer vertices
        outer_points = [
            [center[0] + half_size, center[1], center[2]],
            [center[0], center[1] + half_size, center[2]],
            [center[0] - half_size, center[1], center[2]],
            [center[0], center[1] - half_size, center[2]]
        ]
        
        # Inner vertices (for wall thickness)
        inner_points = []
        for point in outer_points:
            direction = np.array(point) - np.array(center)
            direction = direction / np.linalg.norm(direction)
            inner_point = np.array(center) + direction * (half_size - thickness)
            inner_points.append(inner_point.tolist())
        
        vertices.extend(outer_points)
        vertices.extend(inner_points)
        
        # Create faces for the mesh structure
        for i in range(4):
            next_i = (i + 1) % 4
            # Outer to inner connections
            faces.extend([
                [vertex_offset + i, vertex_offset + next_i, vertex_offset + 4 + next_i],
                [vertex_offset + i, vertex_offset + 4 + next_i, vertex_offset + 4 + i]
            ])
        
        return vertices, faces
    
    def _create_circular_hole(self, center, radius, vertex_offset):
        """Create a circular hole"""
        vertices = []
        faces = []
        
        segments = 12
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
            vertices.append([x, y, z])
        
        # Create faces around the hole
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([vertex_offset + i, vertex_offset + next_i, vertex_offset + segments])
        
        # Add center vertex
        vertices.append(center)
        
        return vertices, faces
    
    def _create_geometric_cutout(self, center, size, vertex_offset):
        """Create geometric cutout pattern"""
        vertices = []
        faces = []
        
        # Create hexagonal cutout
        segments = 6
        radius = size / 2
        
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
            vertices.append([x, y, z])
        
        # Create triangular faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([vertex_offset + i, vertex_offset + next_i, vertex_offset + segments])
        
        vertices.append(center)
        return vertices, faces
    
    def _create_organic_opening(self, center, packing_config, vertex_offset):
        """Create organic, flowing opening"""
        vertices = []
        faces = []
        
        # Create irregular organic shape
        segments = 8
        base_radius = 2.0 * packing_config['hole_ratio']
        
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            # Add organic variation
            radius_variation = 0.3 * math.sin(3 * angle) + 0.2 * math.cos(5 * angle)
            radius = base_radius * (1 + radius_variation)
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
            vertices.append([x, y, z])
        
        # Create faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([vertex_offset + i, vertex_offset + next_i, vertex_offset + segments])
        
        vertices.append(center)
        return vertices, faces
    
    def _should_place_hole(self, center, spacing, density):
        """Determine if a hole should be placed at this location"""
        # Use position-based pseudo-random placement
        hash_val = hash((round(center[0], 1), round(center[1], 1))) % 100
        return hash_val < (density * 100)
    
    def _should_place_pattern(self, center, spacing, density):
        """Determine if a pattern should be placed at this location"""
        return self._should_place_hole(center, spacing, density)
    
    def _organic_pattern_placement(self, center, packing_config):
        """Use organic noise for pattern placement"""
        # Simple noise function based on position
        noise = (math.sin(center[0] * 0.5) * math.cos(center[1] * 0.3) + 1) / 2
        return noise < packing_config['density']
    
    def add_comfort_features(self, vertices, faces, cap_style):
        """Add comfort features like ventilation and sweatband area"""
        new_vertices = list(vertices)
        new_faces = list(faces)
        
        # Add ventilation holes in strategic locations
        if cap_style in ['baseball', 'snapback']:
            vent_positions = [
                [8, 0, 8],   # Side vents
                [-8, 0, 8],
                [0, 8, 8],   # Back vent
                [0, -8, 8]   # Front vent
            ]
            
            for pos in vent_positions:
                vent_verts, vent_faces = self._create_circular_hole(
                    pos, 1.5, len(new_vertices)  # 3mm diameter vents
                )
                new_vertices.extend(vent_verts)
                new_faces.extend(vent_faces)
        
        # Add sweatband groove (inner rim)
        sweatband_verts, sweatband_faces = self._create_sweatband_groove(
            len(new_vertices)
        )
        new_vertices.extend(sweatband_verts)
        new_faces.extend(sweatband_faces)
        
        return np.array(new_vertices), np.array(new_faces)
    
    def _create_sweatband_groove(self, vertex_offset):
        """Create groove for sweatband attachment"""
        vertices = []
        faces = []
        
        # Create inner groove around the cap opening
        radius = 8.5  # Slightly smaller than head opening
        groove_depth = 1.0
        segments = 32
        
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = -groove_depth
            vertices.append([x, y, z])
        
        # Create groove faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([vertex_offset + i, vertex_offset + next_i, vertex_offset + segments])
        
        # Add center point
        vertices.append([0, 0, -groove_depth])
        
        return vertices, faces
    
    def create_cap_geometry(self, cap_style='baseball', pattern_type='mesh', packing_type='medium_packed', head_circumference=58):
        """Create complete cap geometry with patterns and features"""
        # Step 1: Create base cap geometry
        vertices, faces = self.create_cap_base_geometry(cap_style, head_circumference)
        
        # Step 2: Apply modern pattern
        vertices, faces = self.apply_modern_pattern(vertices, faces, pattern_type, packing_type)
        
        # Step 3: Add comfort features
        vertices, faces = self.add_comfort_features(vertices, faces, cap_style)
        
        # Convert to format expected by frontend
        vertices_array = np.array(vertices)
        faces_array = np.array(faces)
        
        return {
            'vertices': vertices_array.flatten().tolist(),
            'faces': faces_array.flatten().tolist()
        }

    def calculate_comfort_metrics(self, geometry, material, packing_type):
        """Calculate comprehensive comfort metrics for the cap"""
        # Extract vertices and faces from geometry
        vertices = np.array(geometry['vertices']).reshape(-1, 3)
        faces = np.array(geometry['faces']).reshape(-1, 3)
        
        surface_area = self._calculate_surface_area(vertices, faces)
        material_props = self.materials.get(material, self.materials['PLA'])
        packing_config = self.packing_types.get(packing_type, self.packing_types['medium_packed'])
        
        # Breathability based on hole density and material
        hole_area_ratio = packing_config['hole_ratio']
        breathability = min(100, (hole_area_ratio * 100 + material_props['breathability'] * 50))
        
        # Flexibility based on material and geometry
        flexibility = material_props['flexibility'] * 100
        
        # Fit quality based on surface area and design
        fit_quality = min(100, 85 + (packing_config['density'] * 15))
        
        # Overall comfort score
        comfort_score = (breathability * 0.4 + flexibility * 0.3 + fit_quality * 0.3)
        
        # Estimated weight (simplified calculation)
        volume_estimate = surface_area * 0.2  # Assume 2mm thickness
        density = 1.25 if material == 'PLA' else 1.27 if material == 'PETG' else 1.2  # g/cm³
        estimated_weight = volume_estimate * density
        
        return {
            'comfort_score': round(comfort_score),
            'breathability': round(breathability),
            'flexibility': round(flexibility),
            'fit_quality': round(fit_quality),
            'estimated_weight': round(estimated_weight)
        }
    
    def _calculate_surface_area(self, vertices, faces):
        """Calculate total surface area"""
        total_area = 0
        for face in faces:
            if len(face) >= 3:
                v1, v2, v3 = vertices[face[:3]]
                # Cross product for triangle area
                cross = np.cross(v2 - v1, v3 - v1)
                area = np.linalg.norm(cross) / 2
                total_area += area
        return total_area

# Initialize the cap designer
cap_designer = ModernCapDesigner()

@app.route('/')
def index():
    return render_template('modern_cap_designer.html')

@app.route('/generate_cap', methods=['POST'])
def generate_cap():
    try:
        data = request.json
        cap_style = data.get('cap_style', 'baseball')
        pattern_type = data.get('pattern_type', 'mesh')
        packing_type = data.get('packing_type', 'medium_packed')
        head_circumference = float(data.get('head_circumference', 58))
        material = data.get('material', 'PLA')
        
        designer = ModernCapDesigner()
        geometry = designer.create_cap_geometry(cap_style, pattern_type, packing_type, head_circumference)
        comfort_metrics = designer.calculate_comfort_metrics(geometry, material, packing_type)
        
        return jsonify({
            'success': True,
            'geometry': {
                'vertices': geometry['vertices'],
                'faces': geometry['faces'],
                'comfort_metrics': comfort_metrics
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_stl', methods=['POST'])
def export_stl():
    try:
        data = request.json
        vertices = data['vertices']
        faces = data['faces']
        
        # Create STL content
        stl_content = "solid ModernCap\n"
        
        # Process faces (assuming triangular faces)
        for i in range(0, len(faces), 3):
            if i + 2 < len(faces):
                v1_idx, v2_idx, v3_idx = faces[i], faces[i+1], faces[i+2]
                
                # Ensure indices are within bounds
                if (v1_idx*3+2 < len(vertices) and 
                    v2_idx*3+2 < len(vertices) and 
                    v3_idx*3+2 < len(vertices)):
                    
                    # Get vertices
                    v1 = [vertices[v1_idx*3], vertices[v1_idx*3+1], vertices[v1_idx*3+2]]
                    v2 = [vertices[v2_idx*3], vertices[v2_idx*3+1], vertices[v2_idx*3+2]]
                    v3 = [vertices[v3_idx*3], vertices[v3_idx*3+1], vertices[v3_idx*3+2]]
                    
                    # Calculate normal vector
                    import numpy as np
                    v1_arr = np.array(v1)
                    v2_arr = np.array(v2)
                    v3_arr = np.array(v3)
                    
                    edge1 = v2_arr - v1_arr
                    edge2 = v3_arr - v1_arr
                    normal = np.cross(edge1, edge2)
                    
                    # Normalize
                    norm_length = np.linalg.norm(normal)
                    if norm_length > 0:
                        normal = normal / norm_length
                    else:
                        normal = np.array([0, 0, 1])
                    
                    stl_content += f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n"
                    stl_content += "    outer loop\n"
                    stl_content += f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n"
                    stl_content += f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n"
                    stl_content += f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n"
                    stl_content += "    endloop\n"
                    stl_content += "  endfacet\n"
        
        stl_content += "endsolid ModernCap\n"
        
        from flask import Response
        return Response(
            stl_content,
            mimetype='application/octet-stream',
            headers={'Content-Disposition': 'attachment; filename=modern_cap.stl'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🧢 Modern 3D Cap & Hat Designer")
    print("=" * 50)
    print("👒 Realistic headwear designs")
    print("🎨 Contemporary patterns & styles")
    print("💨 Comfort & breathability focus")
    print("🖨️  3D printable STL export")
    print("📱 Open: http://localhost:8080")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
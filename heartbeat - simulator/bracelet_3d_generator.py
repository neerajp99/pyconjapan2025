import numpy as np
from scipy.interpolate import interp1d
from scipy.spatial.distance import cdist
import struct

class Bracelet3DGenerator:
    def __init__(self):
        self.resolution = 360  # Points around the bracelet
        
    def generate_from_heartbeat(self, heartbeat_data, radius=30, thickness=5, 
                               height_variation=0.8, pattern_intensity=1.0, 
                               smoothness=0.7):
        """
        Generate 3D bracelet geometry from heartbeat data
        
        Parameters:
        - heartbeat_data: 1D array of heartbeat values
        - radius: Base radius of bracelet (mm)
        - thickness: Base thickness (mm)
        - height_variation: How much heartbeat affects height (0-1)
        - pattern_intensity: Overall pattern strength (0-2)
        - smoothness: Smoothing factor (0-1)
        """
        
        # Resample heartbeat data to match bracelet resolution
        heartbeat_resampled = self._resample_heartbeat(heartbeat_data, self.resolution)
        
        # Apply smoothing
        if smoothness > 0:
            heartbeat_resampled = self._smooth_data(heartbeat_resampled, smoothness)
        
        # Generate base bracelet geometry
        vertices, faces = self._generate_base_bracelet(
            radius, thickness, heartbeat_resampled, 
            height_variation, pattern_intensity
        )
        
        # Create model data for Three.js visualization
        model_data = self._create_model_data(vertices, faces)
        
        return vertices, faces, model_data
    
    def _resample_heartbeat(self, heartbeat_data, target_length):
        """Resample heartbeat data to target length"""
        if len(heartbeat_data) < 2:
            return np.ones(target_length) * 0.5
            
        # Ensure input data has no NaN values
        heartbeat_data = np.nan_to_num(heartbeat_data, nan=0.5, posinf=1.0, neginf=0.0)
            
        x_old = np.linspace(0, 1, len(heartbeat_data))
        x_new = np.linspace(0, 1, target_length)
        
        try:
            # Try cubic interpolation first
            interpolator = interp1d(x_old, heartbeat_data, kind='cubic', 
                                   bounds_error=False, fill_value='extrapolate')
            result = interpolator(x_new)
            
            # Check for NaN values and clean them
            if np.any(np.isnan(result)):
                print("Warning: NaN values detected in cubic interpolation, falling back to linear")
                interpolator = interp1d(x_old, heartbeat_data, kind='linear', 
                                       bounds_error=False, fill_value='extrapolate')
                result = interpolator(x_new)
                
            # Final NaN cleanup
            result = np.nan_to_num(result, nan=0.5, posinf=1.0, neginf=0.0)
            return result
            
        except Exception as e:
            print(f"Interpolation failed: {e}, using simple resampling")
            # Fallback to simple resampling
            indices = np.linspace(0, len(heartbeat_data)-1, target_length)
            indices = np.round(indices).astype(int)
            indices = np.clip(indices, 0, len(heartbeat_data)-1)
            return heartbeat_data[indices]
    
    def _smooth_data(self, data, smoothness):
        """Apply smoothing to data"""
        # Ensure input data has no NaN values
        data = np.nan_to_num(data, nan=0.5, posinf=1.0, neginf=0.0)
        
        window_size = max(3, int(len(data) * smoothness * 0.1))
        if window_size % 2 == 0:
            window_size += 1
            
        # Simple moving average
        padded_data = np.pad(data, window_size//2, mode='wrap')
        smoothed = np.convolve(padded_data, np.ones(window_size)/window_size, mode='valid')
        
        # Final NaN cleanup
        smoothed = np.nan_to_num(smoothed, nan=0.5, posinf=1.0, neginf=0.0)
        return smoothed
    
    def _generate_base_bracelet(self, radius, thickness, heartbeat_data, 
                               height_variation, pattern_intensity):
        """Generate the base bracelet geometry"""
        
        # Angular positions around the bracelet
        angles = np.linspace(0, 2*np.pi, self.resolution, endpoint=False)
        
        # Normalize heartbeat data with proper NaN handling
        heartbeat_min = np.min(heartbeat_data)
        heartbeat_max = np.max(heartbeat_data)
        heartbeat_range = heartbeat_max - heartbeat_min
        
        # Handle edge case where all values are the same
        if heartbeat_range < 1e-8 or np.isnan(heartbeat_range):
            heartbeat_norm = np.full_like(heartbeat_data, 0.5)  # Default to middle value
        else:
            heartbeat_norm = (heartbeat_data - heartbeat_min) / heartbeat_range
            
        # Ensure no NaN values
        heartbeat_norm = np.nan_to_num(heartbeat_norm, nan=0.5, posinf=1.0, neginf=0.0)
        
        # Apply pattern intensity
        heartbeat_norm = heartbeat_norm * pattern_intensity
        
        # Generate vertices
        vertices = []
        
        # Inner and outer rings
        for ring_idx, ring_radius_factor in enumerate([0.8, 1.2]):  # Inner and outer
            for i, angle in enumerate(angles):
                # Base position
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                
                # Height variation based on heartbeat
                z_base = 0
                z_variation = heartbeat_norm[i] * height_variation * thickness
                
                # Ensure z_variation is valid
                if np.isnan(z_variation) or not np.isfinite(z_variation):
                    z_variation = 0
                    
                z = z_base + z_variation
                
                # Ensure z is valid
                if np.isnan(z) or not np.isfinite(z):
                    z = 0
                
                # Radial variation (make bracelet "breathe" with heartbeat)
                radial_variation = 1 + (heartbeat_norm[i] - 0.5) * 0.2
                
                # Ensure radial_variation is valid
                if np.isnan(radial_variation) or radial_variation <= 0 or not np.isfinite(radial_variation):
                    radial_variation = 1.0
                    
                current_radius = radius * ring_radius_factor * radial_variation
                
                # Ensure current_radius is valid
                if np.isnan(current_radius) or current_radius <= 0 or not np.isfinite(current_radius):
                    current_radius = radius * ring_radius_factor
                
                x = current_radius * np.cos(angle)
                y = current_radius * np.sin(angle)
                
                # Final validation of coordinates
                if np.isnan(x) or not np.isfinite(x):
                    x = radius * ring_radius_factor * np.cos(angle)
                if np.isnan(y) or not np.isfinite(y):
                    y = radius * ring_radius_factor * np.sin(angle)
                if np.isnan(z) or not np.isfinite(z):
                    z = 0
                
                vertices.append([x, y, z])
                
                # Add thickness layers
                for layer in range(1, 4):  # 3 layers for thickness
                    layer_multiplier = 1 + heartbeat_norm[i] * 0.3
                    
                    # Ensure layer_multiplier is valid
                    if np.isnan(layer_multiplier) or not np.isfinite(layer_multiplier):
                        layer_multiplier = 1.0
                        
                    z_layer = z + (layer * thickness / 3) * layer_multiplier
                    
                    # Ensure z_layer is valid
                    if np.isnan(z_layer) or not np.isfinite(z_layer):
                        z_layer = z + (layer * thickness / 3)
                        
                    vertices.append([x, y, z_layer])
        
        vertices = np.array(vertices)
        
        # Final comprehensive NaN cleanup for the entire vertices array
        vertices = np.nan_to_num(vertices, nan=0.0, posinf=1000.0, neginf=-1000.0)
        
        # Additional check: replace any remaining invalid values
        mask = ~np.isfinite(vertices)
        vertices[mask] = 0.0
        
        print(f"Generated {len(vertices)} vertices")
        print(f"Vertices shape: {vertices.shape}")
        print(f"Any NaN in vertices: {np.any(np.isnan(vertices))}")
        print(f"Any Inf in vertices: {np.any(np.isinf(vertices))}")
        
        # Generate faces (triangles)
        faces = self._generate_faces(len(angles))
        
        return vertices, faces
    
    def _generate_faces(self, num_angles):
        """Generate triangular faces for the bracelet mesh"""
        faces = []
        
        # Number of layers per ring
        layers_per_ring = 4  # base + 3 thickness layers
        
        # Connect vertices to form triangles
        for ring in range(2):  # Inner and outer rings
            for i in range(num_angles):
                next_i = (i + 1) % num_angles
                
                # Base indices for current and next position
                base_curr = ring * num_angles * layers_per_ring + i * layers_per_ring
                base_next = ring * num_angles * layers_per_ring + next_i * layers_per_ring
                
                # Connect layers vertically
                for layer in range(layers_per_ring - 1):
                    # Triangle 1
                    faces.append([
                        base_curr + layer,
                        base_curr + layer + 1,
                        base_next + layer
                    ])
                    
                    # Triangle 2
                    faces.append([
                        base_next + layer,
                        base_curr + layer + 1,
                        base_next + layer + 1
                    ])
        
        # Connect inner and outer rings
        for i in range(num_angles):
            next_i = (i + 1) % num_angles
            
            # Indices for inner and outer rings
            inner_base = i * layers_per_ring
            outer_base = num_angles * layers_per_ring + i * layers_per_ring
            inner_next = next_i * layers_per_ring
            outer_next = num_angles * layers_per_ring + next_i * layers_per_ring
            
            # Connect top surfaces
            top_layer = layers_per_ring - 1
            
            # Triangle 1
            faces.append([
                inner_base + top_layer,
                outer_base + top_layer,
                inner_next + top_layer
            ])
            
            # Triangle 2
            faces.append([
                inner_next + top_layer,
                outer_base + top_layer,
                outer_next + top_layer
            ])
            
            # Connect bottom surfaces
            faces.append([
                inner_base,
                inner_next,
                outer_base
            ])
            
            faces.append([
                outer_base,
                inner_next,
                outer_next
            ])
        
        return np.array(faces)
    
    def _create_model_data(self, vertices, faces):
        """Create model data for Three.js visualization"""
        
        # Final NaN cleanup before sending to frontend
        vertices = np.nan_to_num(vertices, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Calculate normals for lighting
        normals = self._calculate_normals(vertices, faces)
        
        # Clean normals too
        normals = np.nan_to_num(normals, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Generate colors
        colors = self._generate_colors(len(vertices))
        colors = np.nan_to_num(colors, nan=0.5, posinf=1.0, neginf=0.0)
        
        # Convert to lists and validate
        vertices_list = vertices.flatten().tolist()
        faces_list = faces.flatten().tolist()
        normals_list = normals.flatten().tolist()
        colors_list = colors.flatten().tolist()
        
        # Final validation - check for any remaining NaN/Inf values
        def has_invalid_values(data_list, name):
            invalid_count = sum(1 for x in data_list if not isinstance(x, (int, float)) or 
                              (isinstance(x, float) and (np.isnan(x) or np.isinf(x))))
            if invalid_count > 0:
                print(f"WARNING: Found {invalid_count} invalid values in {name}")
                return True
            return False
        
        has_invalid_values(vertices_list, "vertices")
        has_invalid_values(faces_list, "faces") 
        has_invalid_values(normals_list, "normals")
        has_invalid_values(colors_list, "colors")
        
        model_data = {
            'vertices': vertices_list,
            'faces': faces_list,
            'normals': normals_list,
            'colors': colors_list
        }
        
        print(f"Model data prepared: {len(vertices_list)} vertex coords, {len(faces_list)} face indices")
        
        return model_data
    
    def _calculate_normals(self, vertices, faces):
        """Calculate vertex normals for proper lighting"""
        normals = np.zeros_like(vertices)
        
        for face in faces:
            # Get face vertices
            v0, v1, v2 = vertices[face]
            
            # Calculate face normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)
            face_normal = face_normal / (np.linalg.norm(face_normal) + 1e-8)
            
            # Add to vertex normals
            for vertex_idx in face:
                normals[vertex_idx] += face_normal
        
        # Normalize vertex normals
        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] /= norm
        
        return normals
    
    def _generate_colors(self, num_vertices):
        """Generate colors based on vertex positions"""
        colors = np.zeros((num_vertices, 3))
        
        # Gradient from gold to rose gold
        for i in range(num_vertices):
            t = i / num_vertices
            # Gold to rose gold gradient
            colors[i] = [
                0.8 + 0.2 * t,  # Red
                0.6 + 0.2 * t,  # Green  
                0.2 + 0.3 * t   # Blue
            ]
        
        return colors
    
    def save_stl(self, vertices, faces, filename):
        """Save the 3D model as STL file for 3D printing"""
        
        with open(filename, 'wb') as f:
            # STL header (80 bytes)
            header = b'Heartbeat Bracelet Generated by AI' + b'\0' * (80 - 35)
            f.write(header)
            
            # Number of triangles
            f.write(struct.pack('<I', len(faces)))
            
            # Write each triangle
            for face in faces:
                # Get vertices of the triangle
                v0, v1, v2 = vertices[face]
                
                # Calculate normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                normal = normal / (np.linalg.norm(normal) + 1e-8)
                
                # Write normal (3 floats)
                f.write(struct.pack('<fff', *normal))
                
                # Write vertices (9 floats)
                f.write(struct.pack('<fff', *v0))
                f.write(struct.pack('<fff', *v1))
                f.write(struct.pack('<fff', *v2))
                
                # Attribute byte count (2 bytes, usually 0)
                f.write(struct.pack('<H', 0))
        
        print(f"STL file saved: {filename}")
    
    def save_obj(self, vertices, faces, filename):
        """Save the 3D model as OBJ file"""
        
        with open(filename, 'w') as f:
            f.write("# Heartbeat Bracelet Generated by AI\n")
            
            # Write vertices
            for vertex in vertices:
                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
            
            # Write faces (OBJ uses 1-based indexing)
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        
        print(f"OBJ file saved: {filename}")
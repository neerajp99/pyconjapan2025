"""
Origami Generative Design Simulator
==================================
A Flask web application for generating Japanese origami-inspired fabric patterns
that can be laser-cut. Features real-time generative design with animations and variations.

Built with PIL for drawing and Flask for web interface
"""

from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import math
import io
import base64
from PIL import Image, ImageDraw
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

class OrigamiPatternGenerator:
    def __init__(self):
        self.canvas_width = 800
        self.canvas_height = 600
        self.current_pattern = None
        self.animation_frame = 0
        self.pattern_data = []  # Store pattern elements for export
        self.random_seed = 42  # For reproducible randomness
        
    def setup_canvas(self):
        """Initialize drawing canvas"""
        self.pattern_data = []  # Reset pattern data
        
    def miura_fold_pattern(self, fold_width=40, fold_height=30, variation=0.1, rotation=0, complexity=3, symmetry=True, randomness=0.0, smoothness=1.0):
        """Generate Miura fold tessellation pattern with enhanced options"""
        self.setup_canvas()
        
        # Create PIL image for drawing
        img = Image.new('RGB', (self.canvas_width, self.canvas_height), (20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = self.canvas_width/2, self.canvas_height/2
        time_offset = self.animation_frame * 0.02
        
        # Calculate grid bounds based on complexity
        grid_range = complexity * 3
        
        # Set random seed for reproducible randomness
        np.random.seed(self.random_seed)
        
        for i in range(-grid_range, grid_range + 1):
            for j in range(-grid_range, grid_range + 1):
                # Base position
                x = i * fold_width + (j % 2) * fold_width/2
                y = j * fold_height
                
                # Apply symmetry
                if symmetry:
                    # Mirror pattern across center axes
                    if abs(i) == abs(j):
                        x *= 1.1  # Emphasize diagonal symmetry
                
                # Apply rotation
                cos_r, sin_r = np.cos(rotation), np.sin(rotation)
                rx = x * cos_r - y * sin_r
                ry = x * sin_r + y * cos_r
                
                # Enhanced variation with smoothness control
                smooth_factor = max(0.1, smoothness)
                base_variation = np.sin(time_offset + i * 0.3 * smooth_factor) * variation * fold_width
                base_variation += np.cos(time_offset + j * 0.3 * smooth_factor) * variation * fold_height
                
                # Add controlled randomness
                if randomness > 0:
                    random_x = (np.random.random() - 0.5) * randomness * fold_width * 0.5
                    random_y = (np.random.random() - 0.5) * randomness * fold_height * 0.5
                    rx += random_x
                    ry += random_y
                
                rx += base_variation * smooth_factor
                ry += base_variation * smooth_factor
                
                # Translate to center
                final_x = center_x + rx
                final_y = center_y + ry
                
                # Check bounds with smoother transitions
                margin = 20
                if margin <= final_x <= self.canvas_width - margin and margin <= final_y <= self.canvas_height - margin:
                    # Mountain folds (blue) with varying intensity
                    intensity = 1.0 - randomness * 0.3 if randomness > 0 else 1.0
                    blue_color = (int(100 * intensity), int(150 * intensity), int(255 * intensity))
                    
                    x1, y1 = final_x - fold_width/2, final_y
                    x2, y2 = final_x + fold_width/2, final_y
                    if margin <= x1 <= self.canvas_width - margin and margin <= x2 <= self.canvas_width - margin:
                        draw.line([(x1, y1), (x2, y2)], fill=blue_color, width=max(1, int(3 * smoothness)))
                        self.pattern_data.append({
                            'type': 'mountain_fold',
                            'coords': [(x1, y1), (x2, y2)]
                        })
                    
                    # Valley folds (green) with varying intensity
                    green_color = (int(100 * intensity), int(255 * intensity), int(150 * intensity))
                    x1, y1 = final_x, final_y - fold_height/2
                    x2, y2 = final_x, final_y + fold_height/2
                    if margin <= y1 <= self.canvas_height - margin and margin <= y2 <= self.canvas_height - margin:
                        draw.line([(x1, y1), (x2, y2)], fill=green_color, width=max(1, int(3 * smoothness)))
                        self.pattern_data.append({
                            'type': 'valley_fold',
                            'coords': [(x1, y1), (x2, y2)]
                        })
                    
                    # Cut lines (red) - rectangle outline with smoothness
                    red_color = (int(255 * intensity), int(100 * intensity), int(100 * intensity))
                    x1, y1 = final_x - fold_width/2, final_y - fold_height/2
                    x2, y2 = final_x + fold_width/2, final_y + fold_height/2
                    if (margin <= x1 <= self.canvas_width - margin and margin <= x2 <= self.canvas_width - margin and
                        margin <= y1 <= self.canvas_height - margin and margin <= y2 <= self.canvas_height - margin):
                        # Draw rectangle outline
                        rect_coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
                        for k in range(len(rect_coords) - 1):
                            draw.line([rect_coords[k], rect_coords[k+1]], fill=red_color, width=max(1, int(2 * smoothness)))
                        self.pattern_data.append({
                            'type': 'cut_line',
                            'coords': rect_coords[:-1]
                        })
        
        return self.pil_to_base64(img)
        
    def dragon_scale_pattern(self, scale_size=30, variation=0.5, rotation=0, complexity=3, symmetry=True, randomness=0.0, smoothness=1.0, pattern_mixing=0.0):
        """Generate enhanced dragon scale hexagonal pattern with advanced controls"""
        self.setup_canvas()
        
        img = Image.new('RGB', (self.canvas_width, self.canvas_height), (20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = self.canvas_width/2, self.canvas_height/2
        time_offset = self.animation_frame * 0.02
        hex_height = scale_size * np.sqrt(3) / 2
        
        # Increased grid range for more variation
        grid_range = complexity * 5
        
        # Set random seed for reproducible randomness
        np.random.seed(self.random_seed)
        
        for i in range(-grid_range, grid_range + 1):
            for j in range(-grid_range, grid_range + 1):
                x = i * scale_size * 3/4
                y = j * hex_height + (i % 2) * hex_height/2
                
                # Enhanced symmetry options
                if symmetry:
                    # Create radial symmetry patterns
                    distance_from_center = np.sqrt(i*i + j*j)
                    if distance_from_center > 0:
                        symmetry_factor = 1 + 0.2 * np.sin(distance_from_center * 0.5)
                        x *= symmetry_factor
                        y *= symmetry_factor
                
                # Apply rotation
                cos_r, sin_r = np.cos(rotation), np.sin(rotation)
                rx = x * cos_r - y * sin_r
                ry = x * sin_r + y * cos_r
                
                # Enhanced animation and variation with much higher range
                smooth_factor = max(0.1, smoothness)
                scale_factor = 1 + np.sin(time_offset + i * 0.2 + j * 0.2) * variation * 2.0  # Increased variation range
                
                # Add controlled randomness for size variations
                if randomness > 0:
                    random_scale = 1 + (np.random.random() - 0.5) * randomness * 0.8
                    scale_factor *= random_scale
                    
                    # Random position offset
                    rx += (np.random.random() - 0.5) * randomness * scale_size * 0.3
                    ry += (np.random.random() - 0.5) * randomness * scale_size * 0.3
                
                # Pattern mixing - occasionally use different shapes
                use_alternative = pattern_mixing > 0 and np.random.random() < pattern_mixing
                
                current_size = scale_size * scale_factor * smooth_factor
                
                final_x = center_x + rx
                final_y = center_y + ry
                
                # Improved bounds checking with margins
                margin = current_size + 10
                if (final_x - margin > 0 and final_x + margin < self.canvas_width and
                    final_y - margin > 0 and final_y + margin < self.canvas_height):
                    
                    if use_alternative:
                        # Draw alternative patterns (squares, triangles) for mixing
                        if np.random.random() < 0.5:
                            self.draw_square_pil(draw, final_x, final_y, current_size * 0.8, randomness)
                        else:
                            self.draw_triangle_pil(draw, final_x, final_y, current_size, randomness)
                    else:
                        self.draw_enhanced_hexagon_pil(draw, final_x, final_y, current_size, randomness, smoothness)
        
        return self.pil_to_base64(img)
        
    def draw_enhanced_hexagon_pil(self, draw, x, y, size, randomness=0.0, smoothness=1.0):
        """Draw an enhanced hexagon with improved visual quality"""
        # Calculate hexagon vertices with potential randomness
        vertices = []
        for i in range(6):
            angle = i * 2 * np.pi / 6
            
            # Add slight randomness to vertex positions for organic feel
            vertex_randomness = 0
            if randomness > 0:
                vertex_randomness = (np.random.random() - 0.5) * randomness * size * 0.1
            
            px = x + np.cos(angle) * (size + vertex_randomness)
            py = y + np.sin(angle) * (size + vertex_randomness)
            vertices.append((px, py))
        
        # Intensity based on randomness for visual variety
        intensity = max(0.3, 1.0 - randomness * 0.4)
        
        # Draw hexagon outline (cut lines) with varying thickness
        line_width = max(1, int(2 * smoothness))
        for i in range(6):
            start = vertices[i]
            end = vertices[(i + 1) % 6]
            color = (int(255 * intensity), int(100 * intensity), int(100 * intensity))
            draw.line([start, end], fill=color, width=line_width)
        
        self.pattern_data.append({
            'type': 'cut_line',
            'coords': vertices
        })
        
        # Enhanced internal fold lines with more complexity
        num_internal_lines = 6 if smoothness > 0.7 else 3
        for i in range(num_internal_lines):
            angle = i * 2 * np.pi / num_internal_lines
            inner_radius = size * (0.2 + 0.2 * smoothness)
            outer_radius = size * (0.4 + 0.1 * smoothness)
            
            px1 = x + np.cos(angle) * inner_radius
            py1 = y + np.sin(angle) * inner_radius
            px2 = x + np.cos(angle) * outer_radius
            py2 = y + np.sin(angle) * outer_radius
            
            if i % 2 == 0:
                color = (int(100 * intensity), int(150 * intensity), int(255 * intensity))  # Mountain fold
                fold_type = 'mountain_fold'
            else:
                color = (int(100 * intensity), int(255 * intensity), int(150 * intensity))  # Valley fold
                fold_type = 'valley_fold'
            
            draw.line([(px1, py1), (px2, py2)], fill=color, width=max(1, line_width - 1))
            self.pattern_data.append({
                'type': fold_type,
                'coords': [(px1, py1), (px2, py2)]
            })
    
    def draw_square_pil(self, draw, x, y, size, randomness=0.0):
        """Draw a square for pattern mixing"""
        half_size = size / 2
        
        # Add randomness to corners
        corners = [
            (x - half_size, y - half_size),
            (x + half_size, y - half_size),
            (x + half_size, y + half_size),
            (x - half_size, y + half_size)
        ]
        
        if randomness > 0:
            corners = [(cx + (np.random.random() - 0.5) * randomness * size * 0.1,
                       cy + (np.random.random() - 0.5) * randomness * size * 0.1) 
                      for cx, cy in corners]
        
        # Draw square outline
        for i in range(4):
            start = corners[i]
            end = corners[(i + 1) % 4]
            draw.line([start, end], fill=(255, 150, 100), width=2)
        
        self.pattern_data.append({
            'type': 'cut_line',
            'coords': corners
        })
    
    def draw_triangle_pil(self, draw, x, y, size, randomness=0.0):
        """Draw a triangle for pattern mixing"""
        vertices = []
        for i in range(3):
            angle = i * 2 * np.pi / 3 - np.pi/2  # Start from top
            
            vertex_randomness = 0
            if randomness > 0:
                vertex_randomness = (np.random.random() - 0.5) * randomness * size * 0.1
            
            px = x + np.cos(angle) * (size + vertex_randomness)
            py = y + np.sin(angle) * (size + vertex_randomness)
            vertices.append((px, py))
        
        # Draw triangle outline
        for i in range(3):
            start = vertices[i]
            end = vertices[(i + 1) % 3]
            draw.line([start, end], fill=(150, 255, 150), width=2)
        
        self.pattern_data.append({
            'type': 'cut_line',
            'coords': vertices
        })
        
    def waterbomb_tessellation(self, cell_size=50, variation=0.1, rotation=0, complexity=3, symmetry=True, randomness=0.0, smoothness=1.0, pattern_mixing=0.0):
        """Generate enhanced waterbomb tessellation pattern with advanced controls"""
        self.setup_canvas()
        
        img = Image.new('RGB', (self.canvas_width, self.canvas_height), (20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = self.canvas_width/2, self.canvas_height/2
        time_offset = self.animation_frame * 0.02
        
        grid_range = complexity * 4
        
        # Set random seed for reproducible randomness
        np.random.seed(self.random_seed)
        
        for i in range(-grid_range, grid_range + 1):
            for j in range(-grid_range, grid_range + 1):
                x = i * cell_size
                y = j * cell_size
                
                # Enhanced symmetry options
                if symmetry:
                    # Create checkerboard symmetry pattern
                    if (i + j) % 2 == 0:
                        x *= 1.05  # Slight emphasis on even positions
                        y *= 1.05
                
                # Apply rotation
                cos_r, sin_r = np.cos(rotation), np.sin(rotation)
                rx = x * cos_r - y * sin_r
                ry = x * sin_r + y * cos_r
                
                # Enhanced variation with smoothness control
                smooth_factor = max(0.1, smoothness)
                size_variation = np.sin(time_offset + i * 0.4 + j * 0.4) * variation
                current_size = cell_size * (1 + size_variation) * smooth_factor
                
                # Add controlled randomness
                if randomness > 0:
                    random_scale = 1 + (np.random.random() - 0.5) * randomness * 0.6
                    current_size *= random_scale
                    
                    # Random position offset
                    rx += (np.random.random() - 0.5) * randomness * cell_size * 0.2
                    ry += (np.random.random() - 0.5) * randomness * cell_size * 0.2
                
                # Pattern mixing
                use_alternative = pattern_mixing > 0 and np.random.random() < pattern_mixing
                
                final_x = center_x + rx
                final_y = center_y + ry
                
                # Improved bounds checking
                margin = current_size + 10
                if (final_x - margin > 0 and final_x + margin < self.canvas_width and
                    final_y - margin > 0 and final_y + margin < self.canvas_height):
                    
                    if use_alternative:
                        # Mix with other patterns
                        if np.random.random() < 0.3:
                            self.draw_enhanced_hexagon_pil(draw, final_x, final_y, current_size * 0.7, randomness, smoothness)
                        elif np.random.random() < 0.6:
                            self.draw_square_pil(draw, final_x, final_y, current_size * 0.8, randomness)
                        else:
                            self.draw_waterbomb_cell_enhanced_pil(draw, final_x, final_y, current_size, randomness, smoothness)
                    else:
                        self.draw_waterbomb_cell_enhanced_pil(draw, final_x, final_y, current_size, randomness, smoothness)
        
        return self.pil_to_base64(img)
        
    def draw_waterbomb_cell_enhanced_pil(self, draw, x, y, size, randomness=0.0, smoothness=1.0):
        """Draw an enhanced waterbomb cell with improved visual quality"""
        half_size = size / 2
        
        # Intensity based on randomness
        intensity = max(0.3, 1.0 - randomness * 0.4)
        line_width = max(1, int(2 * smoothness))
        
        # Add randomness to corner positions
        corner_offset = 0
        if randomness > 0:
            corner_offset = (np.random.random() - 0.5) * randomness * size * 0.05
        
        # Square outline (cut lines) with enhanced colors
        corners = [
            (x - half_size + corner_offset, y - half_size + corner_offset),
            (x + half_size - corner_offset, y - half_size + corner_offset),
            (x + half_size - corner_offset, y + half_size - corner_offset),
            (x - half_size + corner_offset, y + half_size - corner_offset)
        ]
        
        # Draw square outline
        red_color = (int(255 * intensity), int(100 * intensity), int(100 * intensity))
        for i in range(4):
            start = corners[i]
            end = corners[(i + 1) % 4]
            draw.line([start, end], fill=red_color, width=line_width)
        
        self.pattern_data.append({
            'type': 'cut_line',
            'coords': corners
        })
        
        # Enhanced diagonal fold lines (waterbomb pattern)
        diag_offset = size * (0.3 + 0.1 * smoothness)
        
        # Mountain folds (diagonals)
        blue_color = (int(100 * intensity), int(150 * intensity), int(255 * intensity))
        draw.line([(x - diag_offset, y - diag_offset), (x + diag_offset, y + diag_offset)], 
                 fill=blue_color, width=max(1, line_width - 1))
        draw.line([(x - diag_offset, y + diag_offset), (x + diag_offset, y - diag_offset)], 
                 fill=blue_color, width=max(1, line_width - 1))
        
        self.pattern_data.append({
            'type': 'mountain_fold',
            'coords': [(x - diag_offset, y - diag_offset), (x + diag_offset, y + diag_offset)]
        })
        self.pattern_data.append({
            'type': 'mountain_fold',
            'coords': [(x - diag_offset, y + diag_offset), (x + diag_offset, y - diag_offset)]
        })
        
        # Valley folds (cross pattern) with smoothness-based complexity
        green_color = (int(100 * intensity), int(255 * intensity), int(150 * intensity))
        cross_size = size * (0.2 + 0.1 * smoothness)
        
        # Horizontal valley fold
        draw.line([(x - cross_size, y), (x + cross_size, y)], 
                 fill=green_color, width=max(1, line_width - 1))
        # Vertical valley fold
        draw.line([(x, y - cross_size), (x, y + cross_size)], 
                 fill=green_color, width=max(1, line_width - 1))
        
        self.pattern_data.append({
            'type': 'valley_fold',
            'coords': [(x - cross_size, y), (x + cross_size, y)]
        })
        self.pattern_data.append({
            'type': 'valley_fold',
            'coords': [(x, y - cross_size), (x, y + cross_size)]
        })
        
        # Additional detail lines for high smoothness
        if smoothness > 0.8:
            detail_color = (int(150 * intensity), int(150 * intensity), int(150 * intensity))
            detail_size = size * 0.15
            
            # Add small corner details
            for corner in corners:
                cx, cy = corner
                draw.line([(cx - detail_size/2, cy), (cx + detail_size/2, cy)], 
                         fill=detail_color, width=1)
                draw.line([(cx, cy - detail_size/2), (cx, cy + detail_size/2)], 
                         fill=detail_color, width=1)
        
    def pil_to_base64(self, img):
        """Convert PIL image to base64"""
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_b64}"
        
    def generate_pattern(self, pattern_type, **params):
        """Generate specified pattern with parameters"""
        if pattern_type == 'miura_fold':
            # Filter parameters for miura_fold_pattern
            valid_params = {k: v for k, v in params.items() 
                          if k in ['fold_width', 'fold_height', 'variation', 'rotation', 'complexity']}
            return self.miura_fold_pattern(**valid_params)
        elif pattern_type == 'dragon_scale':
            # Filter parameters for dragon_scale_pattern
            valid_params = {k: v for k, v in params.items() 
                          if k in ['scale_size', 'variation', 'rotation', 'complexity']}
            return self.dragon_scale_pattern(**valid_params)
        elif pattern_type == 'waterbomb':
            # Filter parameters for waterbomb_tessellation
            valid_params = {k: v for k, v in params.items() 
                          if k in ['cell_size', 'variation', 'rotation', 'complexity']}
            return self.waterbomb_tessellation(**valid_params)
        else:
            valid_params = {k: v for k, v in params.items() 
                          if k in ['fold_width', 'fold_height', 'variation', 'rotation', 'complexity']}
            return self.miura_fold_pattern(**valid_params)
        
    def get_pattern_stats(self):
        """Calculate statistics from current pattern data"""
        cut_lines = sum(1 for item in self.pattern_data if item['type'] == 'cut_line')
        mountain_folds = sum(1 for item in self.pattern_data if item['type'] == 'mountain_fold')
        valley_folds = sum(1 for item in self.pattern_data if item['type'] == 'valley_fold')
        
        return {
            'total_lines': len(self.pattern_data),
            'cut_lines': cut_lines,
            'fold_lines': mountain_folds + valley_folds,
            'mountain_folds': mountain_folds,
            'valley_folds': valley_folds
        }
        
    def export_svg(self, pattern_data):
        """Export pattern as SVG for laser cutting"""
        svg_lines = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{self.canvas_width}" height="{self.canvas_height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.cut-line { stroke: red; stroke-width: 0.1mm; fill: none; }',
            '.mountain-fold { stroke: blue; stroke-width: 0.05mm; fill: none; stroke-dasharray: 2,1; }',
            '.valley-fold { stroke: green; stroke-width: 0.05mm; fill: none; stroke-dasharray: 1,1; }',
            '</style>',
            '</defs>'
        ]
        
        # Add pattern elements
        for item in self.pattern_data:
            coords = item['coords']
            if item['type'] == 'cut_line':
                class_name = 'cut-line'
            elif item['type'] == 'mountain_fold':
                class_name = 'mountain-fold'
            elif item['type'] == 'valley_fold':
                class_name = 'valley-fold'
            else:
                continue
                
            if len(coords) == 2:  # Line
                x1, y1 = coords[0]
                x2, y2 = coords[1]
                svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{class_name}"/>')
            elif len(coords) > 2:  # Polygon
                points = ' '.join([f"{x},{y}" for x, y in coords])
                svg_lines.append(f'<polygon points="{points}" class="{class_name}"/>')
        
        svg_lines.append('</svg>')
        return '\n'.join(svg_lines)
        
    def export_dxf(self, pattern_data):
        """Export pattern as DXF for CAD software"""
        dxf_lines = [
            '0', 'SECTION', '2', 'HEADER',
            '9', '$ACADVER', '1', 'AC1015',
            '0', 'ENDSEC',
            '0', 'SECTION', '2', 'ENTITIES'
        ]
        
        entity_id = 1
        for item in self.pattern_data:
            coords = item['coords']
            layer_name = item['type'].upper()
            
            if len(coords) == 2:  # Line
                x1, y1 = coords[0]
                x2, y2 = coords[1]
                dxf_lines.extend([
                    '0', 'LINE',
                    '8', layer_name,
                    '10', str(x1), '20', str(y1),
                    '11', str(x2), '21', str(y2)
                ])
            elif len(coords) > 2:  # Polyline
                dxf_lines.extend([
                    '0', 'LWPOLYLINE',
                    '8', layer_name,
                    '90', str(len(coords))
                ])
                for x, y in coords:
                    dxf_lines.extend(['10', str(x), '20', str(y)])
            
            entity_id += 1
        
        dxf_lines.extend(['0', 'ENDSEC', '0', 'EOF'])
        return '\n'.join(dxf_lines)

# Global generator instance
generator = OrigamiPatternGenerator()

@app.route('/')
def index():
    return render_template('origami_designer.html')

@app.route('/api/generate_pattern', methods=['POST'])
def generate_pattern():
    try:
        data = request.get_json()
        pattern_type = data.get('pattern_type', 'miura_fold')
        params = data.get('params', {})
        
        # Reset animation frame for static generation
        generator.animation_frame = 0
        
        # Generate pattern
        image_data = generator.generate_pattern(pattern_type, **params)
        
        # Get actual stats from pattern data
        stats = generator.get_pattern_stats()
        stats['pattern_type'] = pattern_type
        
        return jsonify({
            'success': True,
            'image': image_data,
            'stats': stats,
            'pattern_data': {'type': pattern_type, 'params': params, 'elements': generator.pattern_data}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/animate_pattern', methods=['POST'])
def animate_pattern():
    try:
        data = request.get_json()
        pattern_type = data.get('pattern_type', 'miura_fold')
        params = data.get('params', {})
        
        # Increment animation frame
        generator.animation_frame += 1
        
        # Generate animated frame
        frame_data = generator.generate_pattern(pattern_type, **params)
        
        return jsonify({
            'success': True,
            'frame': frame_data,
            'frame_number': generator.animation_frame
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export_pattern', methods=['POST'])
def export_pattern():
    try:
        data = request.get_json()
        pattern_data = data.get('pattern_data')
        format_type = data.get('format', 'svg')
        
        if format_type == 'svg':
            content = generator.export_svg(pattern_data)
            mimetype = 'image/svg+xml'
        elif format_type == 'dxf':
            content = generator.export_dxf(pattern_data)
            mimetype = 'application/dxf'
        else:
            return jsonify({'success': False, 'error': 'Unsupported format'})
        
        # Create file-like object
        file_obj = io.BytesIO(content.encode())
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'origami_pattern.{format_type}'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🎌 Starting Origami Generative Design Simulator...")
    print("🎨 Real-time pattern generation with py5/p5.py")
    print("✂️  Laser-cut ready exports (SVG/DXF)")
    print("🌊 Animated pattern variations")
    print("📱 Access at: http://localhost:8082")
    app.run(debug=True, port=8082, host='0.0.0.0')
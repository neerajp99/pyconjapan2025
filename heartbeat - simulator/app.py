from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import json
from heartbeat_generator import HeartbeatGenerator
from bracelet_3d_generator import Bracelet3DGenerator
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Main page with parameter controls"""
    return render_template('index.html')

@app.route('/generate_heartbeat', methods=['POST'])
def generate_heartbeat():
    """Generate heartbeat data from parameters"""
    try:
        data = request.json
        
        # Extract parameters
        heart_rate = data.get('heart_rate', 70)
        stress_level = data.get('stress_level', 0.5)
        activity_level = data.get('activity_level', 0.3)
        emotion = data.get('emotion', 'calm')
        duration = data.get('duration', 10)
        
        # Generate heartbeat data
        generator = HeartbeatGenerator()
        heartbeat_data = generator.generate(
            heart_rate=heart_rate,
            stress_level=stress_level,
            activity_level=activity_level,
            emotion=emotion,
            duration=duration
        )
        
        return jsonify({
            'success': True,
            'heartbeat_data': heartbeat_data.tolist(),
            'parameters': data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_3d_bracelet', methods=['POST'])
def generate_3d_bracelet():
    """Generate 3D bracelet from heartbeat data"""
    try:
        data = request.json
        heartbeat_data = np.array(data.get('heartbeat_data', []))
        
        # Validate heartbeat data
        if len(heartbeat_data) == 0:
            return jsonify({'success': False, 'error': 'No heartbeat data provided'})
        
        # Clean heartbeat data of any NaN values
        heartbeat_data = np.nan_to_num(heartbeat_data, nan=0.5, posinf=1.0, neginf=0.0)
        
        # Bracelet parameters with validation
        bracelet_params = {
            'radius': max(10, min(100, data.get('radius', 30))),  # Clamp between 10-100
            'thickness': max(1, min(20, data.get('thickness', 5))),  # Clamp between 1-20
            'height_variation': max(0.1, min(5.0, data.get('height_variation', 0.8))),
            'pattern_intensity': max(0.1, min(3.0, data.get('pattern_intensity', 1.0))),
            'smoothness': max(0.0, min(1.0, data.get('smoothness', 0.7)))
        }
        
        # Generate 3D bracelet
        bracelet_gen = Bracelet3DGenerator()
        vertices, faces, model_data = bracelet_gen.generate_from_heartbeat(
            heartbeat_data, **bracelet_params
        )
        
        # Save STL file (use original vertices for STL)
        stl_filename = f"bracelet_{hash(str(data))}.stl"
        stl_path = os.path.join('models', stl_filename)
        bracelet_gen.save_stl(vertices, faces, stl_path)
        
        # Return ONLY the cleaned model_data, not raw vertices/faces
        return jsonify({
            'success': True,
            'model_data': model_data,
            'stl_file': stl_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_stl/<filename>')
def download_stl(filename):
    """Download STL file"""
    try:
        return send_file(
            os.path.join('models', filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
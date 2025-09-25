#!/usr/bin/env python3
"""
Test script to verify the Voronoi 3D flower generation is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from voronoi_3d_flowers import Voronoi3DFlowers

def test_generation():
    print("Testing Voronoi 3D Flower generation...")
    
    designer = Voronoi3DFlowers()
    
    try:
        design = designer.create_earring_design('medium', 18, 'PLA')
        
        print(f"✅ Generation successful!")
        print(f"   Vertices: {len(design['vertices'])}")
        print(f"   Faces: {len(design['faces'])}")
        print(f"   Centroids: {len(design['centroids'])}")
        print(f"   Size config: {design['size_config']}")
        
        # Check if vertices and faces are valid
        if len(design['vertices']) > 0 and len(design['faces']) > 0:
            print("✅ Valid geometry generated")
            
            # Print first few vertices and faces for inspection
            print(f"   First vertex: {design['vertices'][0]}")
            print(f"   First face: {design['faces'][0]}")
        else:
            print("❌ Empty geometry generated")
            
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_generation()
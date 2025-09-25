class HeartbeatBraceletApp {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.braceletMesh = null;
        this.currentHeartbeatData = null;
        this.currentSTLFile = null;
        
        this.init();
        this.setupEventListeners();
        this.updateParameterDisplays();
    }
    
    init() {
        // Initialize Three.js scene
        this.setupThreeJS();
        
        // Generate initial heartbeat preview
        this.generateHeartbeatPreview();
    }
    
    setupThreeJS() {
        const container = document.getElementById('threejs-container');
        
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75, 
            container.clientWidth / container.clientHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(50, 50, 50);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Lighting
        this.setupLighting();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start render loop
        this.animate();
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0x4080ff, 0.3);
        fillLight.position.set(-50, 0, -50);
        this.scene.add(fillLight);
        
        // Rim light
        const rimLight = new THREE.DirectionalLight(0xffd700, 0.5);
        rimLight.position.set(0, 50, -50);
        this.scene.add(rimLight);
    }
    
    setupEventListeners() {
        // Parameter sliders
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.addEventListener('input', () => {
                this.updateParameterDisplays();
                this.generateHeartbeatPreview();
            });
        });
        
        // Emotion selector
        document.getElementById('emotion').addEventListener('change', () => {
            this.generateHeartbeatPreview();
        });
        
        // Generate button
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.generateBracelet();
        });
        
        // Download buttons
        document.getElementById('download-stl').addEventListener('click', () => {
            this.downloadSTL();
        });
        
        document.getElementById('download-obj').addEventListener('click', () => {
            this.downloadOBJ();
        });
    }
    
    updateParameterDisplays() {
        const parameters = [
            'heart-rate', 'stress-level', 'activity-level', 'duration',
            'radius', 'thickness', 'height-variation', 'pattern-intensity', 'smoothness'
        ];
        
        parameters.forEach(param => {
            const slider = document.getElementById(param);
            const display = document.getElementById(param + '-value');
            if (slider && display) {
                display.textContent = slider.value;
            }
        });
    }
    
    generateHeartbeatPreview() {
        const canvas = document.getElementById('heartbeat-canvas');
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Get parameters
        const heartRate = parseInt(document.getElementById('heart-rate').value);
        const stressLevel = parseFloat(document.getElementById('stress-level').value);
        const activityLevel = parseFloat(document.getElementById('activity-level').value);
        
        // Generate simple heartbeat preview
        const width = canvas.width;
        const height = canvas.height;
        const centerY = height / 2;
        
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        const beatsPerSecond = heartRate / 60;
        const timeSpan = 3; // Show 3 seconds
        const samplesPerSecond = 50;
        
        for (let i = 0; i < width; i++) {
            const t = (i / width) * timeSpan;
            const beatPhase = (t * beatsPerSecond) % 1;
            
            let amplitude = 0;
            
            // QRS complex
            if (beatPhase < 0.1) {
                const qrsPhase = beatPhase / 0.1;
                amplitude = Math.sin(qrsPhase * Math.PI) * (0.8 + activityLevel * 0.4);
            }
            // T wave
            else if (beatPhase > 0.3 && beatPhase < 0.6) {
                const tPhase = (beatPhase - 0.3) / 0.3;
                amplitude = Math.sin(tPhase * Math.PI) * 0.3;
            }
            
            // Add stress-based noise
            amplitude += (Math.random() - 0.5) * stressLevel * 0.2;
            
            const y = centerY - amplitude * (height * 0.3);
            
            if (i === 0) {
                ctx.moveTo(i, y);
            } else {
                ctx.lineTo(i, y);
            }
        }
        
        ctx.stroke();
    }
    
    async generateBracelet() {
        console.log('🚀 Starting bracelet generation...');
        const generateBtn = document.getElementById('generate-btn');
        const loading = document.getElementById('loading');
        const infoPanel = document.getElementById('info-panel');
        const downloadSection = document.getElementById('download-section');
        
        // Show loading
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ Generating...';
        loading.style.display = 'block';
        infoPanel.style.display = 'none';
        downloadSection.style.display = 'none';
        
        try {
            // Step 1: Generate heartbeat data
            console.log('📊 Step 1: Generating heartbeat data...');
            const heartbeatData = await this.generateHeartbeatData();
            console.log('📊 Heartbeat data response:', heartbeatData);
            
            if (!heartbeatData.success) {
                throw new Error(heartbeatData.error || 'Failed to generate heartbeat data');
            }
            
            this.currentHeartbeatData = heartbeatData.heartbeat_data;
            console.log('📊 Heartbeat data length:', heartbeatData.heartbeat_data.length);
            
            // Step 2: Generate 3D bracelet
            console.log('🔧 Step 2: Generating 3D bracelet...');
            const braceletData = await this.generate3DBracelet(heartbeatData.heartbeat_data);
            console.log('🔧 Bracelet data response:', braceletData);
            
            if (!braceletData.success) {
                throw new Error(braceletData.error || 'Failed to generate 3D bracelet');
            }
            
            // Step 3: Visualize in Three.js - pass the model_data
            console.log('🎨 Step 3: Visualizing bracelet...');
            this.visualizeBracelet(braceletData.model_data);
            
            // Update info panel - use model_data
            const modelData = braceletData.model_data;
            document.getElementById('vertex-count').textContent = modelData.vertices.length / 3;
            document.getElementById('face-count').textContent = modelData.faces.length / 3;
            
            // Store STL file reference
            this.currentSTLFile = braceletData.stl_file;
            
            // Show info and download options
            infoPanel.style.display = 'block';
            downloadSection.style.display = 'block';
            
            console.log('✅ Bracelet generation completed successfully!');
            
        } catch (error) {
            console.error('❌ Error generating bracelet:', error);
            alert('Error generating bracelet: ' + error.message);
        } finally {
            // Hide loading
            generateBtn.disabled = false;
            generateBtn.textContent = '🚀 Generate 3D Bracelet';
            loading.style.display = 'none';
        }
    }
    
    async generateHeartbeatData() {
        const parameters = {
            heart_rate: parseInt(document.getElementById('heart-rate').value),
            stress_level: parseFloat(document.getElementById('stress-level').value),
            activity_level: parseFloat(document.getElementById('activity-level').value),
            emotion: document.getElementById('emotion').value,
            duration: parseInt(document.getElementById('duration').value)
        };
        
        console.log('📊 Sending heartbeat parameters:', parameters);
        
        const response = await fetch('/generate_heartbeat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parameters)
        });
        
        console.log('📊 Heartbeat API response status:', response.status);
        const result = await response.json();
        console.log('📊 Heartbeat API result:', result);
        
        return result;
    }
    
    async generate3DBracelet(heartbeatData) {
        const parameters = {
            heartbeat_data: heartbeatData,
            radius: parseFloat(document.getElementById('radius').value),
            thickness: parseFloat(document.getElementById('thickness').value),
            height_variation: parseFloat(document.getElementById('height-variation').value),
            pattern_intensity: parseFloat(document.getElementById('pattern-intensity').value),
            smoothness: parseFloat(document.getElementById('smoothness').value)
        };
        
        console.log('🔧 Sending 3D bracelet parameters:', parameters);
        
        const response = await fetch('/generate_3d_bracelet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parameters)
        });
        
        console.log('🔧 3D Bracelet API response status:', response.status);
        const result = await response.json();
        console.log('🔧 3D Bracelet API result:', result);
        
        return result;
    }
    
    visualizeBracelet(braceletData) {
        console.log('🎨 Starting bracelet visualization...');
        console.log('🎨 Bracelet data received:', {
            vertices_length: braceletData.vertices?.length,
            faces_length: braceletData.faces?.length,
            normals_length: braceletData.normals?.length,
            colors_length: braceletData.colors?.length
        });
        
        // Remove existing bracelet
        if (this.braceletMesh) {
            this.scene.remove(this.braceletMesh);
            console.log('🎨 Removed existing bracelet mesh');
        }
        
        // Validate bracelet data
        if (!braceletData || !braceletData.vertices || !braceletData.faces) {
            console.error('❌ Invalid bracelet data received:', braceletData);
            return;
        }
        
        console.log('🎨 Vertices count:', braceletData.vertices.length);
        console.log('🎨 Faces count:', braceletData.faces.length);
        
        // Check for NaN values in vertices with detailed logging
        const vertices = braceletData.vertices;
        let nanCount = 0;
        let infCount = 0;
        
        for (let i = 0; i < vertices.length; i++) {
            if (isNaN(vertices[i])) {
                nanCount++;
                if (nanCount <= 5) { // Log first 5 NaN values
                    console.log(`🔍 NaN found at index ${i}, value:`, vertices[i]);
                }
            } else if (!isFinite(vertices[i])) {
                infCount++;
                if (infCount <= 5) { // Log first 5 Inf values
                    console.log(`🔍 Infinity found at index ${i}, value:`, vertices[i]);
                }
            }
        }
        
        if (nanCount > 0 || infCount > 0) {
            console.error(`⚠️ Invalid values detected - NaN: ${nanCount}, Infinity: ${infCount}`);
            console.log('🔧 Cleaning data...');
            
            // Replace invalid values with 0
            for (let i = 0; i < vertices.length; i++) {
                if (isNaN(vertices[i]) || !isFinite(vertices[i])) {
                    vertices[i] = 0;
                }
            }
            console.log('✅ Invalid values cleaned');
        } else {
            console.log('✅ All vertex values are valid');
        }
        
        // Create geometry from data
        console.log('🎨 Creating Three.js geometry...');
        const geometry = new THREE.BufferGeometry();
        
        // Set vertices with validation
        const verticesArray = new Float32Array(vertices);
        geometry.setAttribute('position', new THREE.BufferAttribute(verticesArray, 3));
        console.log('🎨 Position attribute set');
        
        // Set faces (indices)
        const indices = new Uint32Array(braceletData.faces);
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        console.log('🎨 Index attribute set');
        
        // Set normals
        if (braceletData.normals) {
            const normals = new Float32Array(braceletData.normals);
            geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
            console.log('🎨 Normal attribute set from data');
        } else {
            geometry.computeVertexNormals();
            console.log('🎨 Normal attribute computed');
        }
        
        // Set colors
        if (braceletData.colors) {
            const colors = new Float32Array(braceletData.colors);
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        }
        
        // Create material
        const material = new THREE.MeshPhongMaterial({
            color: 0xffd700,
            shininess: 100,
            specular: 0x444444,
            vertexColors: braceletData.colors ? true : false,
            side: THREE.DoubleSide
        });
        
        // Create mesh
        this.braceletMesh = new THREE.Mesh(geometry, material);
        this.braceletMesh.castShadow = true;
        this.braceletMesh.receiveShadow = true;
        
        // Add to scene
        this.scene.add(this.braceletMesh);
        
        // Center camera on bracelet
        const box = new THREE.Box3().setFromObject(this.braceletMesh);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        // Position camera
        const maxDim = Math.max(size.x, size.y, size.z);
        const distance = maxDim * 2;
        
        this.camera.position.set(
            center.x + distance,
            center.y + distance * 0.5,
            center.z + distance
        );
        
        this.controls.target.copy(center);
        this.controls.update();
    }
    
    downloadSTL() {
        if (this.currentSTLFile) {
            window.open(`/download_stl/${this.currentSTLFile}`, '_blank');
        } else {
            alert('Please generate a bracelet first!');
        }
    }
    
    downloadOBJ() {
        // For now, just download STL - OBJ can be added later
        this.downloadSTL();
    }
    
    onWindowResize() {
        const container = document.getElementById('threejs-container');
        
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Update controls
        this.controls.update();
        
        // Rotate bracelet slowly
        if (this.braceletMesh) {
            this.braceletMesh.rotation.y += 0.005;
        }
        
        // Render
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HeartbeatBraceletApp();
});
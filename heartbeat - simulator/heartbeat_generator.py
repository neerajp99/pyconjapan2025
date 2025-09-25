import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random

class HeartbeatGenerator:
    def __init__(self):
        self.sample_rate = 100  # Hz
        
    def generate(self, heart_rate=70, stress_level=0.5, activity_level=0.3, 
                 emotion='calm', duration=10):
        """
        Generate realistic heartbeat data based on parameters
        
        Parameters:
        - heart_rate: BPM (40-200)
        - stress_level: 0-1 (affects variability)
        - activity_level: 0-1 (affects amplitude)
        - emotion: 'calm', 'excited', 'anxious', 'relaxed'
        - duration: seconds
        """
        
        # Calculate time array
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Base heartbeat interval
        rr_interval = 60.0 / heart_rate
        
        # Generate R-R intervals with variability
        num_beats = int(duration / rr_interval)
        rr_intervals = self._generate_rr_intervals(
            num_beats, rr_interval, stress_level, emotion
        )
        
        # Generate heartbeat signal
        heartbeat = self._generate_heartbeat_signal(
            t, rr_intervals, activity_level, emotion
        )
        
        # Add noise based on stress level
        noise_amplitude = 0.05 + stress_level * 0.1
        noise = np.random.normal(0, noise_amplitude, len(heartbeat))
        heartbeat += noise
        
        # Normalize with proper NaN handling
        heartbeat_min = np.min(heartbeat)
        heartbeat_max = np.max(heartbeat)
        heartbeat_range = heartbeat_max - heartbeat_min
        
        if heartbeat_range < 1e-8 or np.isnan(heartbeat_range):
            heartbeat = np.full_like(heartbeat, 0.5)  # Default to middle value
        else:
            heartbeat = (heartbeat - heartbeat_min) / heartbeat_range
            
        # Ensure no NaN values
        heartbeat = np.nan_to_num(heartbeat, nan=0.5, posinf=1.0, neginf=0.0)
        
        return heartbeat
    
    def _generate_rr_intervals(self, num_beats, base_interval, stress_level, emotion):
        """Generate R-R intervals with heart rate variability"""
        
        # Emotion-based modifications
        emotion_factors = {
            'calm': {'variability': 0.05, 'trend': 0},
            'excited': {'variability': 0.15, 'trend': -0.1},
            'anxious': {'variability': 0.25, 'trend': -0.15},
            'relaxed': {'variability': 0.03, 'trend': 0.05}
        }
        
        factor = emotion_factors.get(emotion, emotion_factors['calm'])
        
        # Base variability
        variability = factor['variability'] + stress_level * 0.1
        
        # Generate intervals
        intervals = []
        for i in range(num_beats):
            # Add trend
            trend = factor['trend'] * (i / num_beats)
            
            # Add random variability
            variation = np.random.normal(0, variability)
            
            # Calculate interval
            interval = base_interval * (1 + trend + variation)
            interval = max(0.3, min(2.0, interval))  # Clamp to reasonable range
            intervals.append(interval)
            
        return np.array(intervals)
    
    def _generate_heartbeat_signal(self, t, rr_intervals, activity_level, emotion):
        """Generate the actual heartbeat waveform"""
        
        heartbeat = np.zeros_like(t)
        current_time = 0
        
        for interval in rr_intervals:
            if current_time >= t[-1]:
                break
                
            # Find closest time index
            beat_idx = np.argmin(np.abs(t - current_time))
            
            # Generate QRS complex
            qrs_width = 0.08 + activity_level * 0.04  # Wider with activity
            qrs_amplitude = 0.8 + activity_level * 0.4  # Higher with activity
            
            # Create QRS complex shape
            qrs_samples = int(qrs_width * self.sample_rate)
            qrs_t = np.linspace(-qrs_width/2, qrs_width/2, qrs_samples)
            
            # Multi-component QRS (Q, R, S waves)
            q_wave = -0.1 * np.exp(-((qrs_t + 0.02) / 0.01)**2)
            r_wave = qrs_amplitude * np.exp(-((qrs_t) / 0.015)**2)
            s_wave = -0.2 * np.exp(-((qrs_t - 0.02) / 0.01)**2)
            
            qrs_complex = q_wave + r_wave + s_wave
            
            # Add to signal
            start_idx = max(0, beat_idx - qrs_samples//2)
            end_idx = min(len(heartbeat), start_idx + len(qrs_complex))
            
            if end_idx > start_idx:
                qrs_to_add = qrs_complex[:end_idx-start_idx]
                heartbeat[start_idx:end_idx] += qrs_to_add
            
            # Add T-wave
            t_wave_delay = 0.3  # seconds after QRS
            t_wave_idx = beat_idx + int(t_wave_delay * self.sample_rate)
            
            if t_wave_idx < len(heartbeat):
                t_amplitude = 0.2 + activity_level * 0.1
                t_width = 0.15
                t_samples = int(t_width * self.sample_rate)
                
                if t_wave_idx + t_samples < len(heartbeat):
                    t_t = np.linspace(0, t_width, t_samples)
                    t_wave = t_amplitude * np.exp(-((t_t - t_width/2) / (t_width/4))**2)
                    heartbeat[t_wave_idx:t_wave_idx + t_samples] += t_wave
            
            current_time += interval
            
        return heartbeat
    
    def visualize_heartbeat(self, heartbeat_data, title="Generated Heartbeat"):
        """Visualize the generated heartbeat data"""
        plt.figure(figsize=(12, 6))
        t = np.linspace(0, len(heartbeat_data)/self.sample_rate, len(heartbeat_data))
        plt.plot(t, heartbeat_data, 'r-', linewidth=1.5)
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return plt
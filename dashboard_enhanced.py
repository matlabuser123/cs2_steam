#!/usr/bin/env python3
"""
Enhanced CS2 Performance Dashboard
Real-time monitoring and configuration management for Counter-Strike 2
"""

import streamlit as st
import random
import time
import subprocess
import os
import shutil
from collections import deque
from datetime import datetime
from pathlib import Path

# Import required packages with error handling
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    import psutil
    import GPUtil
    import numpy as np
except ImportError as e:
    st.error(f"Required packages not installed: {e}")
    st.error("Run: pip install -r requirements.txt")
    st.stop()

# Configuration
CONFIG_DIR = Path("./cs2tune/profiles")
CS2_CONFIG_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\autoexec.cfg")

# Global variables for monitoring
fps_data = deque(maxlen=100)
cpu_temp_data = deque(maxlen=100)
gpu_temp_data = deque(maxlen=100)
gpu_usage_data = deque(maxlen=100)
vram_data = deque(maxlen=100)
timestamps = deque(maxlen=100)


@st.cache_data
def get_available_profiles():
    """Get list of available CS2 configuration profiles."""
    if not CONFIG_DIR.exists():
        return []
    return [f.name for f in CONFIG_DIR.glob("*.cfg")]


def switch_profile(profile_name):
    """Switch CS2 configuration profile with backup."""
    src = CONFIG_DIR / profile_name
    
    if not src.exists():
        return False, f"Profile '{profile_name}' not found."
    
    try:
        # Create backup of current config
        if CS2_CONFIG_PATH.exists():
            backup_path = CS2_CONFIG_PATH.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg")
            shutil.copy2(CS2_CONFIG_PATH, backup_path)
        
        # Copy new profile
        shutil.copy2(src, CS2_CONFIG_PATH)
        
        return True, f"✅ Successfully switched to {profile_name}"
    except Exception as e:
        return False, f"❌ Error switching profile: {str(e)}"


def get_system_metrics():
    """Get comprehensive system performance metrics."""
    try:
        metrics = {
            'timestamp': datetime.now(),
            'fps': random.randint(180, 320),  # Replace with actual CS2 FPS reading
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_temp': 0,
            'gpu_temp': 0,
            'gpu_usage': 0,
            'vram_used': 0,
            'vram_total': 0
        }
        
        # Get CPU temperature
        try:
            sensors = psutil.sensors_temperatures()
            if 'coretemp' in sensors:
                temps = [sensor.current for sensor in sensors['coretemp'] if sensor.current]
                metrics['cpu_temp'] = max(temps) if temps else 0
        except (AttributeError, KeyError):
            pass
        
        # Get GPU metrics
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                metrics['gpu_temp'] = gpu.temperature or 0
                metrics['gpu_usage'] = (gpu.load * 100) if gpu.load else 0
                metrics['vram_used'] = gpu.memoryUsed / 1024 if gpu.memoryUsed else 0  # GB
                metrics['vram_total'] = gpu.memoryTotal / 1024 if gpu.memoryTotal else 0  # GB
        except (IndexError, AttributeError):
            pass
        
        return metrics
    except Exception as e:
        st.error(f"Error getting system metrics: {e}")
        return None


def create_performance_chart(data, title, color, unit=""):
    """Create a performance chart using Plotly."""
    if len(data) < 2:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=list(data),
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f"{title} Over Time",
        xaxis_title="Time",
        yaxis_title=f"{title} ({unit})",
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig


def main():
    """Main dashboard application."""
    # Page configuration
    st.set_page_config(
        page_title="CS2 Performance Dashboard",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎮 CS2 Performance Dashboard")
    st.markdown("**Real-time monitoring and configuration management for Counter-Strike 2**")
    
    # Sidebar - Configuration Management
    with st.sidebar:
        st.header("🛠️ Control Panel")
        
        # Profile Management
        st.subheader("⚙️ Configuration Profiles")
        available_profiles = get_available_profiles()
        
        if available_profiles:
            profile_descriptions = {
                'max_fps.cfg': '🚀 Maximum FPS - Competitive',
                'balanced.cfg': '⚖️ Balanced - General Gaming',
                'gpu_saver.cfg': '❄️ GPU Saver - Thermal Limited'
            }
            
            selected_profile = st.selectbox(
                "Select Profile:",
                options=available_profiles,
                format_func=lambda x: profile_descriptions.get(x, x.replace('.cfg', '').replace('_', ' ').title()),
                key="profile_selector"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Switch", type="primary", use_container_width=True):
                    success, message = switch_profile(selected_profile)
                    if success:
                        st.success(message)
                        st.session_state.current_profile = selected_profile
                    else:
                        st.error(message)
            
            with col2:
                if st.button("📄 View Config", use_container_width=True):
                    try:
                        with open(CONFIG_DIR / selected_profile, 'r') as f:
                            st.text_area("Configuration Preview:", f.read(), height=200)
                    except Exception as e:
                        st.error(f"Error reading config: {e}")
        else:
            st.warning("⚠️ No profiles found")
            st.info("Expected location: ./cs2tune/profiles/")
        
        # Current Profile Display
        current_profile = getattr(st.session_state, 'current_profile', 'Unknown')
        st.info(f"**Current Profile:** {current_profile}")
        
        # Monitoring Controls
        st.subheader("📊 Monitoring")
        monitoring_active = st.checkbox("🔴 Real-time Monitoring", value=True)
        refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 2)
        
        # Settings
        st.subheader("⚙️ Settings")
        show_advanced = st.checkbox("Show Advanced Metrics")
        chart_theme = st.selectbox("Chart Theme", ["plotly", "plotly_white", "plotly_dark"])
    
    # Main Dashboard Area
    if monitoring_active:
        # Auto-refresh setup
        placeholder = st.empty()
        
        # Get current metrics
        metrics = get_system_metrics()
        
        if metrics:
            # Update data queues
            fps_data.append(metrics['fps'])
            gpu_temp_data.append(metrics['gpu_temp'])
            gpu_usage_data.append(metrics['gpu_usage'])
            cpu_temp_data.append(metrics['cpu_temp'])
            vram_data.append(metrics['vram_used'])
            timestamps.append(metrics['timestamp'])
            
            with placeholder.container():
                # Key Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_fps = metrics['fps'] - (list(fps_data)[-2] if len(fps_data) > 1 else metrics['fps'])
                    st.metric(
                        label="🎯 FPS",
                        value=f"{metrics['fps']}",
                        delta=f"{delta_fps:+.0f}" if abs(delta_fps) > 0 else None
                    )
                
                with col2:
                    delta_gpu_temp = metrics['gpu_temp'] - (list(gpu_temp_data)[-2] if len(gpu_temp_data) > 1 else metrics['gpu_temp'])
                    temp_color = "normal" if metrics['gpu_temp'] < 75 else "off" if metrics['gpu_temp'] > 85 else "inverse"
                    st.metric(
                        label="🌡️ GPU Temp",
                        value=f"{metrics['gpu_temp']:.1f}°C",
                        delta=f"{delta_gpu_temp:+.1f}°C" if abs(delta_gpu_temp) > 0.1 else None
                    )
                
                with col3:
                    st.metric(
                        label="🎮 GPU Usage",
                        value=f"{metrics['gpu_usage']:.1f}%",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        label="💾 VRAM",
                        value=f"{metrics['vram_used']:.1f}GB",
                        delta=f"/ {metrics['vram_total']:.1f}GB"
                    )
                
                # Charts Row
                if len(fps_data) > 5:
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        fps_fig = create_performance_chart(fps_data, "FPS", "#00ff88", "fps")
                        if fps_fig:
                            st.plotly_chart(fps_fig, use_container_width=True)
                    
                    with chart_col2:
                        temp_fig = create_performance_chart(gpu_temp_data, "GPU Temperature", "#ff6b6b", "°C")
                        if temp_fig:
                            st.plotly_chart(temp_fig, use_container_width=True)
                
                # Advanced Metrics
                if show_advanced:
                    st.subheader("📈 Advanced Metrics")
                    
                    adv_col1, adv_col2, adv_col3 = st.columns(3)
                    
                    with adv_col1:
                        st.metric("💻 CPU Usage", f"{metrics['cpu_usage']:.1f}%")
                        st.metric("🧠 RAM Usage", f"{metrics['memory_usage']:.1f}%")
                    
                    with adv_col2:
                        st.metric("🌡️ CPU Temp", f"{metrics['cpu_temp']:.1f}°C")
                        frame_time = 1000 / metrics['fps'] if metrics['fps'] > 0 else 0
                        st.metric("⏱️ Frame Time", f"{frame_time:.2f}ms")
                    
                    with adv_col3:
                        if len(fps_data) > 10:
                            avg_fps = sum(list(fps_data)[-10:]) / 10
                            min_fps = min(list(fps_data)[-10:])
                            st.metric("📊 Avg FPS (10s)", f"{avg_fps:.1f}")
                            st.metric("📉 Min FPS (10s)", f"{min_fps}")
                
                # Performance Analysis
                if len(fps_data) > 30:
                    st.subheader("🔍 Performance Analysis")
                    
                    analysis_col1, analysis_col2 = st.columns(2)
                    
                    with analysis_col1:
                        recent_fps = list(fps_data)[-30:]
                        avg_fps = sum(recent_fps) / len(recent_fps)
                        fps_stability = (max(recent_fps) - min(recent_fps)) / avg_fps * 100
                        
                        if avg_fps >= 240:
                            st.success("🎯 Excellent performance!")
                        elif avg_fps >= 144:
                            st.info("✅ Good performance")
                        else:
                            st.warning("⚠️ Consider Max FPS profile")
                        
                        st.write(f"**FPS Stability:** {100-fps_stability:.1f}%")
                    
                    with analysis_col2:
                        recent_temps = list(gpu_temp_data)[-30:]
                        avg_temp = sum(recent_temps) / len(recent_temps) if recent_temps else 0
                        
                        if avg_temp > 85:
                            st.error("🔥 GPU overheating! Use GPU Saver profile")
                        elif avg_temp > 75:
                            st.warning("🌡️ GPU running warm")
                        else:
                            st.success("❄️ GPU temperature optimal")
                        
                        st.write(f"**Avg GPU Temp:** {avg_temp:.1f}°C")
        
        # Auto-refresh
        time.sleep(refresh_rate)
        st.rerun()
    
    else:
        st.info("📊 Real-time monitoring is disabled. Enable it in the sidebar to view live metrics.")
        
        # Static system information
        st.subheader("💻 System Information")
        system_col1, system_col2 = st.columns(2)
        
        with system_col1:
            st.write(f"**CPU Cores:** {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
            st.write(f"**Total RAM:** {psutil.virtual_memory().total / (1024**3):.1f} GB")
            st.write(f"**Available RAM:** {psutil.virtual_memory().available / (1024**3):.1f} GB")
        
        with system_col2:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    st.write(f"**GPU:** {gpu.name}")
                    st.write(f"**VRAM:** {gpu.memoryTotal} MB")
                    st.write(f"**Driver Version:** {gpu.driver}")
            except:
                st.write("**GPU:** Information unavailable")


if __name__ == "__main__":
    main()

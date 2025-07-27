import streamlit as st
import subprocess
import pandas as pd
import numpy as np
import time
import json
import os
import psutil
import threading
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import random
from collections import deque

# Fix unresolved import by ensuring the package is installed
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Please install the 'streamlit-autorefresh' package using pip.")

# Global variables for monitoring
fps_data = []
cpu_temp_data = []
gpu_temp_data = []
gpu_usage_data = []
timestamps = []
current_profile = "none"
monitoring_active = False
max_data_points = 100

# For telemetry dashboard
max_len = 50
fps_telemetry = deque(maxlen=max_len)
gpu_temp_telemetry = deque(maxlen=max_len)

# Run a command and display its output live in the Streamlit app
def run_command_live(cmd):
    """Run a command and display its output live in the Streamlit app."""
    with st.expander(f"📤 Output: {' '.join(cmd)}", expanded=True):
        placeholder = st.empty()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        output = ""
        for line in process.stdout:
            output += line
            placeholder.code(output, language="bash")
        process.wait()
        return process.returncode


# Get NVIDIA GPU temperature and usage using nvidia-smi
def get_gpu_info():
    """Get NVIDIA GPU temperature and usage using nvidia-smi."""
    try:
        output = subprocess.check_output([
            "nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu",
            "--format=csv,noheader,nounits"
        ]).decode()
        temp, usage = map(float, output.strip().split(','))
        return temp, usage
    except subprocess.CalledProcessError:
        return 0, 0


# Get CPU temperature using psutil
def get_cpu_temp():
    """Get CPU temperature using psutil."""
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            return sum(
                temp.current for temp in temps['coretemp']
            ) / len(temps['coretemp'])
        return 0
    except KeyError:
        return 0


# Simulate FPS reading (replace with actual CS2 FPS reading if available)
def get_fps():
    """Simulate FPS reading (replace with actual CS2 FPS reading)."""
    _, gpu_usage = get_gpu_info()
    base_fps = 250
    variance = np.random.normal(0, 15)
    fps = max(1, base_fps * (0.5 + (gpu_usage / 100) * 0.5) + variance)
    return fps


# Monitor system performance metrics
def monitor_system():
    """Monitor system metrics and update global variables."""
    global fps_data, cpu_temp_data, gpu_temp_data
    global gpu_usage_data, timestamps, monitoring_active

    while monitoring_active:
        fps = get_fps()
        cpu_temp = get_cpu_temp()
        gpu_temp, gpu_usage = get_gpu_info()

        current_time = datetime.now().strftime("%H:%M:%S")

        fps_data.append(fps)
        cpu_temp_data.append(cpu_temp)
        gpu_temp_data.append(gpu_temp)
        gpu_usage_data.append(gpu_usage)
        timestamps.append(current_time)

        # Keep only the last max_data_points
        if len(fps_data) > max_data_points:
            fps_data.pop(0)
            cpu_temp_data.pop(0)
            gpu_temp_data.pop(0)
            gpu_usage_data.pop(0)
            timestamps.pop(0)

        update_obs_overlay(fps, cpu_temp, gpu_temp, gpu_usage)
        time.sleep(1)


# Update OBS overlay JSON file with latest metrics
def update_obs_overlay(fps, cpu_temp, gpu_temp, gpu_usage):
    """Update OBS overlay JSON file with latest metrics"""
    overlay_data = {
        "fps": int(fps),
        "cpu_temp": round(cpu_temp, 1),
        "gpu_temp": round(gpu_temp, 1),
        "gpu_usage": round(gpu_usage, 1),
        "profile": current_profile,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    
    try:
        with open("obs_overlay.json", "w") as f:
            json.dump(overlay_data, f)
    except OSError:
        pass


# Set CS2 profile by copying the appropriate config file
def set_profile(profile_name):
    """Set CS2 profile by copying the appropriate config file."""
    global current_profile  # Ensure global declaration is at the top

    profiles_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "cs2tune", "profiles"
    )
    profile_file = os.path.join(profiles_dir, f"{profile_name}.cfg")
    if not os.path.exists(profile_file):
        return False

    try:
        current_profile = profile_name
        return True
    except OSError:
        return False


# Dashboard title with gaming theme
st.title("🚀 CS2 MAX PERFORMANCE DASHBOARD 🚀")

# Create tabs for different functionality
tab1, tab2, tab3 = st.tabs([
    "Performance Monitor", "Driver Manager", "Game Profiles"
])

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
    
if 'current_profile' not in st.session_state:
    st.session_state.current_profile = "none"

# Performance Monitor Tab
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Real-time Performance Metrics")
        
        # Start/Stop monitoring button
        if not monitoring_active:
            if st.button("🟢 Start Performance Monitoring"):
                monitoring_active = True
                monitor_thread = threading.Thread(
                    target=monitor_system, daemon=True
                )
                monitor_thread.start()
                st.session_state.monitoring = True
                st.success("Monitoring started!")
        else:
            if st.button("🔴 Stop Monitoring"):
                monitoring_active = False
                st.session_state.monitoring = False
                st.info("Monitoring stopped.")
    
    with col2:
        st.subheader("Current Profile")
        st.info(f"Active Profile: **{current_profile.upper()}**")
        
        if current_profile != "max_fps":
            if st.button("⚡ Switch to MAX FPS Mode"):
                if set_profile("max_fps"):
                    st.success("Switched to MAX FPS profile!")
                else:
                    st.error("Failed to switch profile.")
    
    # Performance Charts
    st.subheader("Performance Charts")
    
    if fps_data:
        # Create performance charts using Plotly
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("FPS", "Temperature & GPU Usage"),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.5]
        )
        
        # FPS Chart
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=fps_data, mode='lines', name='FPS',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
        
        # Temperature & GPU Usage Chart
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cpu_temp_data,
                mode='lines',
                name='CPU Temp (°C)',
                line=dict(color='red', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=gpu_temp_data,
                mode='lines',
                name='GPU Temp (°C)',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=gpu_usage_data,
                mode='lines',
                name='GPU Usage (%)',
                line=dict(color='blue', width=2)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start monitoring to see performance metrics.")
        
    # System Information
    st.subheader("System Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="CPU", value="i9-14900HX")
    
    with col2:
        st.metric(label="GPU", value="RTX 5000 Ada")
    
    with col3:
        st.metric(label="RAM", value="64GB DDR5")

    # Telemetry Dashboard
    st.subheader("Live Telemetry Dashboard")
    
    # Start telemetry button
    if st.button("▶️ Start Telemetry"):
        st.session_state.telemetry_active = True
        st.success("Telemetry started!")
        
    if st.session_state.get("telemetry_active", False):
        # Replace with real telemetry input
        fps = random.randint(120, 300)
        gpu_temp = random.uniform(60, 85)

        fps_telemetry.append(fps)
        gpu_temp_telemetry.append(gpu_temp)

        st.line_chart(list(fps_telemetry), use_container_width=True)
        st.line_chart(list(gpu_temp_telemetry), use_container_width=True)

        time.sleep(1)
    else:
        st.info("Click '▶️ Start Telemetry' to view live telemetry data.")

# Driver Manager Tab
with tab2:
    st.subheader("MSI CreatorPro Driver Installer")
    
    if st.button("List Available Drivers", key="list_drivers_tab2"):
        retcode = run_command_live(["pro-drivers", "--list"])
        if retcode == 0:
            st.success("Driver list completed.")
        else:
            st.error(f"Driver list failed with exit code {retcode}.")

    if st.button("Show Installation Summary", key="summary_tab2"):
        retcode = run_command_live(["pro-drivers", "--summary"])
        if retcode == 0:
            st.success("Summary completed.")
        else:
            st.error(f"Summary failed with exit code {retcode}.")
            
    if st.button("Run Full Install (Dry Run)", key="dry_run_tab2"):
        st.info("Starting dry-run installation...")
        retcode = run_command_live(["pro-drivers", "--dry-run"])
        if retcode == 0:
            st.success("Dry run completed successfully.")
        else:
            st.error(f"Dry run failed with exit code {retcode}.")

    if st.button("Run Full Install (Actual)", key="actual_install_tab2"):
        if st.checkbox(
            "I confirm I want to run the actual install",
            key="confirm_tab2"
        ):
            st.warning("Starting actual installation. Please wait...")
            retcode = run_command_live(["pro-drivers"])
            if retcode == 0:
                st.success("✅ Install completed successfully.")
                st.balloons()
            else:
                st.error(
                    f"Install failed with exit code {retcode}. "
                    "Check error_log.txt for details."
                )
        else:
            st.warning(
                "Please confirm by checking the box above "
                "before running actual install."
            )

    # Auto-refresh option
    st_autorefresh(interval=5000, key="refresh")

    # System Info Button
    st.markdown("## 🖥️ System Info")
    if st.button("Show System Info (via inxi)"):
        run_command_live(["inxi", "-Fxz"])

    # Advanced Install Options
    st.markdown("## ⚙️ Advanced Install Options")
    with st.form("advanced_install_form"):
        skip_fingerprint = st.checkbox("Skip Fingerprint Driver")
        skip_bluetooth = st.checkbox("Skip Bluetooth Driver")
        reboot_after = st.checkbox("Reboot After Install")
        dry_run = st.checkbox("Dry Run Only")
        submitted = st.form_submit_button("Run Custom Install")

        if submitted:
            cmd = ["pro-drivers"]
            if skip_fingerprint:
                cmd.append("--skip-fingerprint")
            if skip_bluetooth:
                cmd.append("--skip-bluetooth")
            if reboot_after:
                cmd.append("--reboot")
            if dry_run:
                cmd.append("--dry-run")
            st.info(f"Running custom install: {' '.join(cmd)}")
            retcode = run_command_live(cmd)
            st.success(
                "Custom install completed." if retcode == 0 else
                f"Install failed with code {retcode}"
            )

    # View Error Log
    st.markdown("## 🪵 View Error Log")
    log_path = Path("error_log.txt")
    if log_path.exists():
        with log_path.open("r") as log_file:
            st.code(log_file.read(), language="text")
        st.download_button(
            "Download Full Log",
            data=log_path.read_text(),
            file_name="error_log.txt"
        )
    else:
        st.info("No log file found yet. Run an install to generate logs.")

    # Success Feedback
    if st.button("🚀 Run Full Install Now"):
        st.warning("Starting actual installation. Please wait...")
        retcode = run_command_live(["pro-drivers"])
        if retcode == 0:
            st.success("✅ Install completed successfully.")
            st.balloons()
        else:
            st.error(
                f"❌ Install failed with exit code {retcode}. Check logs below."
            )

# Game Profiles Tab
with tab3:
    st.subheader("CS2 Performance Profiles")
    
    # Profile selection
    profile_options = ["max_fps", "balanced", "gpu_saver"]
    selected_profile = st.selectbox(
        "Select Performance Profile",
        profile_options,
        index=0
    )
    
    # Display profile description
    profile_descriptions = {
        "max_fps": (
            "Maximum FPS with minimal visual quality. "
            "Best for competitive gaming."
        ),
        "balanced": (
            "Good balance of performance and visuals. "
            "Good for most scenarios."
        ),
        "gpu_saver": (
            "Reduces GPU load to prevent overheating. "
            "Use when temps are high."
        )
    }
    
    st.info(profile_descriptions[selected_profile])
    
    # Apply profile button
    if st.button("Apply Selected Profile"):
        try:
            # Path to cs2tune profiles directory
            profiles_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "cs2tune", "profiles"
            )
            
            # Ensure the directory exists
            os.makedirs(profiles_dir, exist_ok=True)
            
            # Path to selected profile
            profile_path = os.path.join(
                profiles_dir, f"{selected_profile}.cfg"
            )
            
            if os.path.exists(profile_path):
                # Run the hardware monitor script with the selected profile
                cmd = ["python", os.path.join(profiles_dir, "..", "hardware_monitor.py"), 
                      "--profile", selected_profile]
                
                retcode = run_command_live(cmd)
                
                if retcode == 0:
                    st.success(f"Profile {selected_profile} applied successfully!")
                    # Update global variable
                    global current_profile
                    current_profile = selected_profile
                else:
                    st.error(f"Failed to apply profile. Exit code: {retcode}")
            else:
                st.error(f"Profile file {selected_profile}.cfg not found!")
        except Exception as e:
            st.error(f"Error applying profile: {str(e)}")
    
    # Auto-switching section
    st.subheader("Profile Auto-Switching")
    
    auto_switch = st.checkbox("Enable Automatic Profile Switching", 
                             value=False, key="auto_switch")
    
    if auto_switch:
        try:
            # Start the hardware monitor in auto mode
            cmd = ["python", os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                         "cs2tune", "hardware_monitor.py"),
                  "--only-when-running"]
            
            st.info("Starting auto-switching monitor in the background...")
            
            # Use Popen to run in background
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            
            st.session_state.auto_switch_pid = process.pid
            st.success("Auto-switching monitor started successfully!")
            
        except Exception as e:
            st.error(f"Error starting auto-switching: {str(e)}")
    elif "auto_switch_pid" in st.session_state:
        # Stop the auto-switching process
        try:
            os.kill(st.session_state.auto_switch_pid, 9)
            del st.session_state.auto_switch_pid
            st.info("Auto-switching monitor stopped.")
        except:
            st.warning("Auto-switching monitor already stopped or not running.")

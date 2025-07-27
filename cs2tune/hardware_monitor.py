#!/usr/bin/env python
"""
CS2 Auto Profile Switcher
Monitors system metrics and automatically switches CS2 profiles based on
temperature and performance.
"""

import os
import time
import json
import logging
import argparse
import subprocess
import psutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='cs2tune_monitor.log'
)

# Constants
PROFILES_DIR = Path(__file__).parent / "profiles"
CONFIG_DIR = Path(os.environ.get(
    'CSGO_CFG_DIR', 
    Path.home() / "steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg"
))
METRICS_FILE = Path(CONFIG_DIR / "cs2tune_metrics.json")
OBS_OVERLAY_FILE = Path(CONFIG_DIR / "obs_overlay.json")

# Default thresholds
DEFAULT_GPU_TEMP_HIGH = 85
DEFAULT_GPU_USAGE_HIGH = 95
DEFAULT_FPS_LOW = 180
DEFAULT_POLLING_INTERVAL = 5

# Profile definitions
PROFILES = {
    "max_fps": {
        "description": "Maximum FPS with minimal visual quality",
        "conditions": {
            "gpu_temp": "< 80",
            "gpu_usage": "< 95"
        }
    },
    "balanced": {
        "description": "Good balance of performance and visuals",
        "conditions": {
            "gpu_temp": "< 85",
            "fps": "> 200"
        }
    },
    "gpu_saver": {
        "description": "Reduces GPU load to prevent overheating",
        "conditions": {
            "gpu_temp": "> 85",
            "gpu_usage": "> 95"
        }
    }
}

def get_gpu_info():
    """Get NVIDIA GPU temperature and usage using nvidia-smi"""
    try:
        output = subprocess.check_output([
            "nvidia-smi", 
            "--query-gpu=temperature.gpu,utilization.gpu", 
            "--format=csv,noheader,nounits"
        ]).decode()
        temp, usage = map(float, output.strip().split(','))
        return temp, usage
    except Exception as e:
        logging.error(f"Failed to get GPU info: {e}")
        return 70, 80  # Default values if nvidia-smi fails

def get_cpu_temp():
    """Get CPU temperature using psutil"""
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            return sum(temp.current for temp in temps['coretemp']) / len(temps['coretemp'])
        return 70  # Default if can't get CPU temp
    except Exception as e:
        logging.error(f"Failed to get CPU temp: {e}")
        return 70

def get_fps():
    """Get current FPS from CS2 (simulated for now)"""
    # TODO: Implement actual CS2 FPS reading from game files or memory
    # For now, we'll simulate based on GPU usage
    _, gpu_usage = get_gpu_info()
    base_fps = 250
    fps = max(1, base_fps * (0.5 + (gpu_usage/100) * 0.5))
    
    # Try to read from metrics file if it exists (could be updated by another process)
    try:
        if METRICS_FILE.exists():
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
                if 'fps' in metrics:
                    return metrics['fps']
    except:
        pass
        
    return fps

def is_cs2_running():
    """Check if CS2 is currently running"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['cs2.exe', 'cs2']:
            return True
    return False

def set_profile(profile_name):
    """Set CS2 profile by copying the appropriate config file"""
    profile_file = PROFILES_DIR / f"{profile_name}.cfg"
    autoexec_file = CONFIG_DIR / "autoexec.cfg"
    
    if not profile_file.exists():
        logging.error(f"Profile {profile_name} does not exist")
        return False
    
    try:
        # Backup autoexec if doesn't exist already
        backup_file = CONFIG_DIR / "autoexec.cfg.backup"
        if not backup_file.exists() and autoexec_file.exists():
            with open(autoexec_file, 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
            logging.info("Created backup of autoexec.cfg")
        
        # Copy profile to autoexec.cfg
        with open(profile_file, 'r') as src:
            profile_content = src.read()
            
        with open(autoexec_file, 'r') as current:
            current_content = current.read()
            
        # Replace the profile section or append it
        if "// PROFILE SETTINGS START" in current_content:
            parts = current_content.split("// PROFILE SETTINGS START")
            if len(parts) > 1:
                second_parts = parts[1].split("// PROFILE SETTINGS END")
                if len(second_parts) > 1:
                    new_content = parts[0] + "// PROFILE SETTINGS START\n" + profile_content + "\n// PROFILE SETTINGS END" + second_parts[1]
                    with open(autoexec_file, 'w') as f:
                        f.write(new_content)
            else:
                with open(autoexec_file, 'a') as f:
                    f.write("\n// PROFILE SETTINGS START\n" + profile_content + "\n// PROFILE SETTINGS END\n")
        else:
            with open(autoexec_file, 'a') as f:
                f.write("\n// PROFILE SETTINGS START\n" + profile_content + "\n// PROFILE SETTINGS END\n")
        
        # Update OBS overlay
        update_obs_overlay(profile_name)
        
        logging.info(f"Applied profile: {profile_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to set profile {profile_name}: {e}")
        return False

def update_obs_overlay(profile_name):
    """Update OBS overlay JSON file with current metrics"""
    try:
        gpu_temp, gpu_usage = get_gpu_info()
        cpu_temp = get_cpu_temp()
        fps = get_fps()
        
        overlay_data = {
            "profile": profile_name,
            "fps": int(fps),
            "gpu_temp": round(gpu_temp, 1),
            "gpu_usage": round(gpu_usage, 1),
            "cpu_temp": round(cpu_temp, 1),
            "timestamp": time.strftime("%H:%M:%S"),
            "date": time.strftime("%Y-%m-%d")
        }
        
        # Create metrics file for internal use
        with open(METRICS_FILE, 'w') as f:
            json.dump(overlay_data, f)
            
        # Create OBS overlay file
        with open(OBS_OVERLAY_FILE, 'w') as f:
            json.dump(overlay_data, f)
            
    except Exception as e:
        logging.error(f"Failed to update OBS overlay: {e}")

def select_best_profile(gpu_temp, gpu_usage, fps):
    """Select the best profile based on current metrics"""
    if gpu_temp > DEFAULT_GPU_TEMP_HIGH or gpu_usage > DEFAULT_GPU_USAGE_HIGH:
        return "gpu_saver"
    elif fps < DEFAULT_FPS_LOW:
        return "balanced"
    else:
        return "max_fps"

def monitor_loop(args):
    """Main monitoring loop"""
    current_profile = None
    profile_change_time = 0
    min_change_interval = 30  # Minimum seconds between profile changes
    
    logging.info(f"Starting CS2 auto-profile monitor with {args.interval}s polling interval")
    
    while True:
        try:
            if not is_cs2_running():
                if args.only_when_running:
                    logging.info("CS2 not running, sleeping for 30 seconds")
                    time.sleep(30)
                    continue
            
            gpu_temp, gpu_usage = get_gpu_info()
            fps = get_fps()
            
            # Update metrics regardless of profile changes
            update_obs_overlay(current_profile or "none")
            
            # Select best profile based on metrics
            best_profile = select_best_profile(gpu_temp, gpu_usage, fps)
            
            # Only change profile if it's different and enough time has passed
            now = time.time()
            if (best_profile != current_profile and 
                (now - profile_change_time) > min_change_interval):
                
                logging.info(f"Changing profile from {current_profile} to {best_profile} "
                           f"(GPU: {gpu_temp}°C, Usage: {gpu_usage}%, FPS: {int(fps)})")
                
                if set_profile(best_profile):
                    current_profile = best_profile
                    profile_change_time = now
            
            time.sleep(args.interval)
            
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in monitor loop: {e}")
            time.sleep(args.interval)

def main():
    parser = argparse.ArgumentParser(description="CS2 Auto Profile Switcher")
    parser.add_argument("--interval", type=int, default=DEFAULT_POLLING_INTERVAL,
                       help=f"Polling interval in seconds (default: {DEFAULT_POLLING_INTERVAL})")
    parser.add_argument("--profile", type=str, choices=["max_fps", "balanced", "gpu_saver"],
                       help="Set specific profile and exit")
    parser.add_argument("--only-when-running", action="store_true",
                       help="Only switch profiles when CS2 is running")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create directories if they don't exist
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.profile:
        success = set_profile(args.profile)
        print(f"Profile {args.profile} {'applied successfully' if success else 'failed to apply'}")
        return
    
    # Otherwise, start the monitoring loop
    monitor_loop(args)

if __name__ == "__main__":
    main()

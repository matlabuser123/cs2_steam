import logging
import subprocess
from paths import (
    DRIVER_SCRIPT,
    VERIFY_SCRIPT,
    PERFTEST_CFG,
    DASHBOARD_SCRIPT,
    DOCKER_COMPOSE_FILE
)


def run_command(command, description):
    """Run a shell command with logging."""
    logging.info("Running: %s", description)
    try:
        subprocess.run(command, check=True, shell=True)
        logging.info("Success: %s", description)
    except subprocess.CalledProcessError as e:
        logging.error("Failed: %s with error: %s", description, e)


def file_exists(file_path, description):
    """Check if a file exists and log an error if not."""
    if not file_path.is_file():
        logging.error("%s not found.", description)
        return False
    return True


def install_drivers():
    """Run the driver installation script."""
    if file_exists(DRIVER_SCRIPT, "Driver installation script"):
        run_command(
            "powershell.exe -ExecutionPolicy Bypass -File "
            f"\"{DRIVER_SCRIPT}\"",
            "Installing drivers"
        )


def verify_drivers():
    """Run the driver verification script."""
    if file_exists(VERIFY_SCRIPT, "Driver verification script"):
        run_command(
            "powershell.exe -ExecutionPolicy Bypass -File "
            f"\"{VERIFY_SCRIPT}\"",
            "Verifying drivers"
        )


def run_performance_test():
    """Run the performance test configuration."""
    if file_exists(PERFTEST_CFG, "Performance test configuration file"):
        logging.info("Running performance test using perftest.cfg")
        # Add logic to execute the performance test if applicable


def launch_dashboard():
    """Launch the Streamlit dashboard."""
    if file_exists(DASHBOARD_SCRIPT, "Dashboard script"):
        run_command(
            "streamlit run "
            f"\"{DASHBOARD_SCRIPT}\" --server.port 8501 "
            "--server.enableCORS false",
            "Launching dashboard"
        )


def run_docker():
    """Build and run Docker containers."""
    if file_exists(DOCKER_COMPOSE_FILE, "docker-compose.yml"):
        run_command("docker-compose up --build", "Running Docker containers")
    else:
        logging.error("docker-compose.yml not found.")

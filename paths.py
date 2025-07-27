from pathlib import Path

# Define all paths used in the project
SCRIPT_DIR = Path(__file__).parent.resolve()
LOG_FILE = Path(SCRIPT_DIR / "automation_log.txt")
DRIVER_SCRIPT = Path(SCRIPT_DIR / "msi_drivers" / "install_msi_drivers.ps1")
VERIFY_SCRIPT = Path(SCRIPT_DIR / "msi_drivers" / "verify_drivers.ps1")
PERFTEST_CFG = Path(SCRIPT_DIR / "perftest.cfg")
DASHBOARD_SCRIPT = Path(SCRIPT_DIR / "dashboard.py")
DOCKER_COMPOSE_FILE = Path(SCRIPT_DIR / "docker-compose.yml")

import argparse
import logging
from pipelines import (
    install_drivers,
    verify_drivers,
    run_performance_test,
    launch_dashboard,
    run_docker
)
from paths import LOG_FILE
from drivers import list_driver_zips, extract_driver_zip


def setup_logging():
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG for detailed logs
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging initialized. Log file: %s", LOG_FILE)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Driver Automation Tool")
    parser.add_argument(
        "--install-drivers", action="store_true", help="Install all drivers"
    )
    parser.add_argument(
        "--verify-drivers",
        action="store_true",
        help="Verify installed drivers"
    )
    parser.add_argument(
        "--run-perftest", action="store_true", help="Run performance tests"
    )
    parser.add_argument(
        "--launch-dashboard",
        action="store_true",
        help="Launch the Streamlit dashboard"
    )
    parser.add_argument(
        "--run-docker", action="store_true", help="Run Docker containers"
    )
    parser.add_argument(
        "--list-drivers", action="store_true", help="List all driver ZIP files"
    )
    parser.add_argument(
        "--extract-driver", metavar="ZIP_FILE",
        help="Extract a specific driver ZIP file"
    )
    return parser.parse_args()


def execute_arguments(args):
    """Execute actions based on parsed arguments."""
    if args.install_drivers:
        install_drivers()
    if args.verify_drivers:
        verify_drivers()
    if args.run_perftest:
        run_performance_test()
    if args.launch_dashboard:
        launch_dashboard()
    if args.run_docker:
        run_docker()
    if args.list_drivers:
        list_driver_zips()
    if args.extract_driver:
        extract_driver_zip(args.extract_driver)


def main():
    setup_logging()
    args = parse_arguments()
    execute_arguments(args)


if __name__ == "__main__":
    main()

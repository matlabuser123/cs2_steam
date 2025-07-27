import os
import sys
import platform
import argparse
import subprocess
from pathlib import Path
import csv
import logging
import shutil
from typing import Dict, List

SCRIPT_DIR = Path(__file__).parent.resolve()
DRIVER_FOLDER = SCRIPT_DIR / "drivers"
LOG_FILE = SCRIPT_DIR / "install_log.txt"
INSTALL_ORDER = [
    "01_Intel_Chipset.zip",
    "02_Intel_ME_SW.zip",
    "03_Intel_Serial_IO_Drivers.zip",
    "04_Intel_DTT.zip",
    "05_Intel_VGA.zip",
    "06_NVIDIA_VGA_DCH_STUDIO.zip",
    "07_Realtek_Audio.zip",
    "08_Nahimic.zip",
    "09_Intel_Wireless.zip",
    "10_Intel_Bluetooth.zip",
    "11_Camera.zip",
    "12_HID_Event_Filter_Driver.zip",
    "13_SCM.zip",
    "14_MSI_TrueColor.zip",
    "15_MSI_Center_Pro.zip",
    "16_MSI_Microphone_Optimizer.zip",
    "17_MSI_Dragon_Edge.zip"
]
REBOOT_AFTER = {"01_Intel_Chipset.zip", "02_Intel_ME_SW.zip", "06_NVIDIA_VGA_DCH_STUDIO.zip"}

def setup_logging(verbose: bool = False):
    """Configure logging to file and console."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
    handlers = [logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')]
    if verbose:
        handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(
        level=logging.INFO if not verbose else logging.DEBUG,
        format='[pro_drivers_app] %(message)s',
        handlers=handlers
    )

def is_admin() -> bool:
    """Check for admin/root privileges."""
    if platform.system() == "Windows":
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0

def check_external_tools():
    """Warn if required external tools are missing."""
    if platform.system() != "Windows":
        if not shutil.which("unzip"):
            logging.warning("Missing 'unzip' tool. Please install it for extraction.")
        # Only warn about wine if we actually need it
        wine_needed = any(
            any(f.endswith(ext) for ext in [".exe", ".bat"]) for f in os.listdir(DRIVER_FOLDER)
        )
        if wine_needed and not shutil.which("wine"):
            logging.warning("Missing 'wine'. Windows installers may not run on Linux.")

def extract_zip(zip_path: Path, extract_path: Path, dry_run: bool = False) -> bool:
    """Extract ZIP archive to target folder."""
    if dry_run:
        logging.info(f"[DRY RUN] Would extract: {zip_path}")
        return True
    try:
        if platform.system() == "Windows":
            cmd = ["powershell", "-Command", f"Expand-Archive -Path '{zip_path}' -DestinationPath '{extract_path}' -Force"]
            subprocess.run(cmd, check=True)
        else:
            extract_path.mkdir(parents=True, exist_ok=True)
            subprocess.run(["unzip", "-o", str(zip_path), "-d", str(extract_path)], check=True)
        logging.info(f"Extracted: {zip_path.name}")
        return True
    except Exception as e:
        logging.error(f"Extraction failed for {zip_path.name}: {e}")
        return False

def run_installers(extract_path: Path, dry_run: bool = False, force_wine: bool = False) -> str:
    """Run all .exe and .bat installers found in extract_path."""
    found_installers: List[Path] = []
    failed = False
    for root, _, files in os.walk(extract_path):
        for file in files:
            full_path = Path(root) / file
            if file.endswith(".exe") or file.endswith(".bat"):
                found_installers.append(full_path)
    if not found_installers:
        logging.warning(f"No installer found in: {extract_path}")
        return "no_installer"
    for installer in found_installers:
        logging.info(f"Running installer: {installer}")
        if dry_run:
            continue
        try:
            if platform.system() == "Windows":
                if installer.suffix == ".bat":
                    subprocess.run(["cmd", "/c", str(installer)], check=True)
                else:
                    subprocess.run(str(installer), check=True, shell=True)
            elif force_wine:
                if installer.suffix == ".bat":
                    subprocess.run(["wine", "cmd", "/c", str(installer)], check=True)
                else:
                    subprocess.run(["wine", str(installer)], check=True)
            else:
                logging.warning(f"Skipping Windows installer {installer} on Linux (no Wine).")
        except Exception as e:
            logging.error(f"Installer failed: {installer}: {e}")
            failed = True
    return "failed" if failed else "installed"

def extract_and_install(zip_file: str, verbose: bool = False, dry_run: bool = False, auto_reboot: bool = False, force: bool = False, force_wine: bool = False) -> str:
    """Extract ZIP and run all installers, mark as installed, handle reboot."""
    folder_name = Path(zip_file).stem
    extract_path = DRIVER_FOLDER / folder_name
    marker_file = extract_path / ".installed"
    if marker_file.exists() and not force:
        logging.info(f"Skipping {zip_file}: already installed.")
        return "skipped"
    # Progress indicator
    print(f"\n[Progress] Processing {zip_file} ...")
    if not extract_path.exists() or force:
        ok = extract_zip(DRIVER_FOLDER / zip_file, extract_path, dry_run)
        if not ok:
            return "failed"
    else:
        logging.info(f"Already extracted: {zip_file}")
    result = run_installers(extract_path, dry_run, force_wine)
    if result == "installed" and not dry_run:
        try:
            marker_file.write_text("installed\n", encoding="utf-8")
        except Exception as e:
            logging.error(f"Failed to write marker file for {zip_file}: {e}")
    if zip_file in REBOOT_AFTER and result == "installed":
        if auto_reboot:
            logging.info("Auto-rebooting system...")
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/r", "/t", "0"])
            else:
                subprocess.run(["reboot"])
            sys.exit(0)
        else:
            resp = input(f"Reboot recommended after installing {zip_file}. Reboot now? (Y/N): ")
            if resp.strip().upper() == "Y":
                logging.info("Rebooting system...")
                if platform.system() == "Windows":
                    subprocess.run(["shutdown", "/r", "/t", "0"])
                else:
                    subprocess.run(["reboot"])
                sys.exit(0)
    return result

def print_summary():
    print("""
📦 MSI CreatorPro X18 HX Driver Categories:
1. ✅ Intel Chipset, MEI, Serial IO, DTT
2. 🎮 NVIDIA RTX 5000 ADA + Intel iGPU
3. 🔈 Realtek Audio + Nahimic
4. 📡 Intel Wi-Fi 7 (BE200) + Bluetooth 5.4
5. 🎥 IR/FHD Webcam Driver
6. ⌨️ White-backlit Keyboard Control
7. 🧰 Optional: MSI Center Pro, True Color, Thunderbolt

🛠️ Tips:
- Run this script with admin privileges.
- Run Intel iGPU driver BEFORE NVIDIA.
- Reboot between MEI and GPU installs if prompted.
""")

def print_driver_links():
    print("""
🔗 Official Driver Sources:
- MSI Support: https://www.msi.com/Workstation/CreatorPro-X18-HX-A14VX/support
- Intel Drivers: https://www.intel.com/content/www/us/en/download-center/home.html
- NVIDIA Studio: https://www.nvidia.com/en-au/studio/drivers/

🎯 Use Studio drivers unless you need latest Game Ready features.
""")

def export_results_csv(results: Dict[str, str], filename: str = "driver_install_results.csv"):
    """Export install results to CSV."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Driver ZIP", "Status"])
        for zip_file, status in results.items():
            writer.writerow([zip_file, status])
    print(f"Exported install results to {filename}")

def export_results_md(results: Dict[str, str], filename: str = "driver_install_results.md"):
    """Export install results to Markdown table."""
    with open(filename, "w") as f:
        f.write("| Driver ZIP | Status |\n|------------|--------|\n")
        for zip_file, status in results.items():
            f.write(f"| {zip_file} | {status} |\n")
    print(f"Exported install results to {filename}")

def main():
    parser = argparse.ArgumentParser(description="MSI CreatorPro X18 HX Driver Installer")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions only")
    parser.add_argument("--summary", action="store_true", help="Print driver categories and install tips")
    parser.add_argument("--links", action="store_true", help="Show official download links")
    parser.add_argument("--auto-reboot", action="store_true", help="Automatically reboot after critical driver installs")
    parser.add_argument("--silent", action="store_true", help="Suppress prompts (implies auto-reboot)")
    parser.add_argument("--verbose", action="store_true", help="Print more output")
    parser.add_argument("--list", action="store_true", help="List detected driver ZIPs and install order")
    parser.add_argument("--export-csv", action="store_true", help="Export install results to CSV")
    parser.add_argument("--export-md", action="store_true", help="Export install results to Markdown")
    parser.add_argument("--force", action="store_true", help="Force reinstall even if .installed marker exists")
    parser.add_argument("--wine", action="store_true", help="Use Wine for installer execution on Linux")
    args = parser.parse_args()

    setup_logging(args.verbose)
    check_external_tools()

    if not is_admin():
        logging.error("Please run this script as administrator/root.")
        sys.exit(1)

    if args.summary:
        print_summary()
        sys.exit(0)

    if args.links:
        print_driver_links()
        sys.exit(0)

    if args.list:
        print("Detected driver ZIPs in install order:")
        for zip_file in INSTALL_ORDER:
            zip_path = DRIVER_FOLDER / zip_file
            status = "FOUND" if zip_path.exists() else "MISSING"
            print(f"{zip_file} - {status}")
        sys.exit(0)

    auto_reboot = args.auto_reboot or args.silent

    results = {}
    missing_drivers = []
    for zip_file in INSTALL_ORDER:
        zip_path = DRIVER_FOLDER / zip_file
        if zip_path.exists():
            status = extract_and_install(
                zip_file,
                verbose=args.verbose,
                dry_run=args.dry_run,
                auto_reboot=auto_reboot,
                force=args.force,
                force_wine=args.wine
            )
            results[zip_file] = status
        else:
            logging.warning(f"Missing: {zip_file}")
            results[zip_file] = "missing"
            missing_drivers.append(zip_file)

    print("========== Driver Automation Summary ==========")
    print(f"Log file: {LOG_FILE}")
    print("| Driver ZIP | Status |")
    print("|------------|--------|")
    for zip_file, status in results.items():
        print(f"| {zip_file} | {status} |")
    if missing_drivers:
        print("\nMissing drivers:")
        for driver in missing_drivers:
            print(f"  - {driver}")
    print("===============================================")

    if args.export_csv:
        export_results_csv(results)
    if args.export_md:
        export_results_md(results)

    # Exit code: 0 if all installed/skipped, 1 if any failed/missing
    if any(s in ("failed", "missing", "no_installer") for s in results.values()):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

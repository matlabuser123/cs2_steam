import argparse
import shutil
import os


CONFIG_DIR = "./cs2tune/profiles"
ACTIVE_CONFIG_PATH = "/path/to/cs2/autoexec.cfg"


def list_profiles():
    """List all available CS2 configuration profiles."""
    return [f for f in os.listdir(CONFIG_DIR) if f.endswith('.cfg')]


def switch_profile(profile_name):
    """Switch to a specific CS2 configuration profile."""
    src = os.path.join(CONFIG_DIR, profile_name)
    if not os.path.isfile(src):
        print(f"Profile '{profile_name}' not found.")
        return False
    shutil.copy(src, ACTIVE_CONFIG_PATH)
    print(f"Switched to profile {profile_name}")
    return True


def main():
    """Main CLI interface for CS2 profile management."""
    parser = argparse.ArgumentParser(
        description="CS2 Configuration Profile Manager",
        epilog="Example: python cs2tune_cli.py --switch balanced.cfg"
    )
    parser.add_argument("--list", action="store_true",
                        help="List all available profiles")
    parser.add_argument("--switch", type=str,
                        help="Switch to specified profile")
    args = parser.parse_args()

    if args.list:
        profiles = list_profiles()
        if profiles:
            print("Available profiles:")
            for p in profiles:
                print(f"  - {p}")
        else:
            print("No profiles found in CONFIG_DIR")
    elif args.switch:
        switch_profile(args.switch)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

import pytest
from unittest.mock import patch, MagicMock
from pro_drivers_app import extract_and_install, is_admin, main
from pathlib import Path

DRIVER_FOLDER = Path(__file__).parent / "drivers"

@patch("pro_drivers_app.subprocess.run")
@patch("pro_drivers_app.Path.exists")
def test_extract_and_install_skips_if_installed(mock_exists, mock_run):
    mock_exists.side_effect = lambda path=None: True if path and ".installed" in str(path) else False
    status = extract_and_install("01_Intel_Chipset.zip", dry_run=False)
    assert status == "skipped"
    mock_run.assert_not_called()

@patch("pro_drivers_app.subprocess.run")
@patch("pro_drivers_app.Path.exists")
def test_extract_and_install_runs_installers(mock_exists, mock_run):
    # marker does not exist, folder exists, simulate one installer file
    mock_exists.side_effect = lambda path=None: False if path and ".installed" in str(path) else True
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [
            (str(DRIVER_FOLDER / "01_Intel_Chipset"), [], ["setup.exe"]),
        ]
        status = extract_and_install("01_Intel_Chipset.zip", dry_run=False)
        assert status == "installed"
        assert mock_run.called

@patch("pro_drivers_app.is_admin")
@patch("pro_drivers_app.subprocess.run")
def test_main_runs_and_exits(mon_run, mock_admin, capsys):
    mock_admin.return_value = True
    sys_argv_backup = sys.argv
    sys.argv = ["pro_drivers_app.py", "--dry-run", "--list"]
    try:
        main()
    except SystemExit as e:
        assert e.code == 0
    sys.argv = sys_argv_backup
    captured = capsys.readouterr()
    assert "Detected driver ZIPs" in captured.out

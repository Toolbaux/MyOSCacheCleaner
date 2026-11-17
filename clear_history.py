#!/usr/bin/env python3
"""
clear_history.py - Empty the trash and clear recent-file / app history.

Works on Windows, macOS, and Linux. Runs as a DRY RUN by default:
it only lists what it would delete. Add --yes to actually delete.

    python3 clear_history.py          # preview
    python3 clear_history.py --yes    # really delete

Close browsers and other apps first so they don't recreate history.
Deleted items cannot be recovered.
"""
import argparse
import glob
import os
import platform
import shutil
import subprocess
from pathlib import Path

HOME = Path.home()
SYSTEM = platform.system()


def targets():
    """Return (label, list_of_paths) pairs for this OS. Contents get removed."""
    t = []
    if SYSTEM == "Windows":
        appdata = Path(os.environ.get("APPDATA", HOME / "AppData/Roaming"))
        local = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData/Local"))
        t += [
            ("Recent files", [appdata / "Microsoft/Windows/Recent"]),
            ("Jump lists", [appdata / "Microsoft/Windows/Recent/AutomaticDestinations",
                            appdata / "Microsoft/Windows/Recent/CustomDestinations"]),
            ("Temp files", [local / "Temp"]),
            ("Thumbnail cache", [Path(p) for p in glob.glob(str(local / "Microsoft/Windows/Explorer/thumbcache_*.db"))]),
            ("Windows Timeline (activity history)", [local / "ConnectedDevicesPlatform"]),
        ]
    elif SYSTEM == "Darwin":
        t += [
            ("Recent items", [HOME / "Library/Application Support/com.apple.sharedfilelist"]),
            ("Saved app state", [HOME / "Library/Saved Application State"]),
            ("Quick Look cache", [HOME / "Library/Caches/com.apple.QuickLook.thumbnailcache"]),
        ]
    else:  # Linux / BSD
        t += [
            ("Recently used files", [HOME / ".local/share/recently-used.xbel"]),
            ("Thumbnail cache", [HOME / ".cache/thumbnails", HOME / ".thumbnails"]),
            ("Shell history", [HOME / ".bash_history", HOME / ".zsh_history",
                               HOME / ".local/share/fish/fish_history", HOME / ".python_history"]),
            ("Activity log (Zeitgeist)", [HOME / ".local/share/zeitgeist"]),
        ]
    # Common to all: shell/REPL history files on Mac & Windows PowerShell
    if SYSTEM == "Darwin":
        t.append(("Shell history", [HOME / ".bash_history", HOME / ".zsh_history",
                                    HOME / ".python_history", HOME / ".zsh_sessions"]))
    if SYSTEM == "Windows":
        appdata = Path(os.environ.get("APPDATA", HOME / "AppData/Roaming"))
        t.append(("PowerShell history",
                  [appdata / "Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"]))
    return t


def trash_dirs():
    if SYSTEM == "Darwin":
        return [HOME / ".Trash"]
    if SYSTEM == "Windows":
        return []  # handled via PowerShell below
    dirs = [HOME / ".local/share/Trash"]
    # Trash on other mounted drives
    dirs += [Path(p) for p in glob.glob(f"/media/*/*/.Trash-{os.getuid()}")]
    dirs += [Path(p) for p in glob.glob(f"/mnt/*/.Trash-{os.getuid()}")]
    return dirs


def remove(path: Path, really: bool):
    """Delete a file, or the contents of a folder (keeps the folder itself)."""
    if not path.exists() and not path.is_symlink():
        return 0
    count = 0
    items = [path] if path.is_file() or path.is_symlink() else list(path.iterdir())
    for item in items:
        print(("  deleting " if really else "  would delete ") + str(item))
        count += 1
        if really:
            try:
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
            except Exception as e:  # file in use, permission denied, etc.
                print(f"    skipped ({e})")
    return count


def empty_trash(really: bool):
    print("\n[Trash]")
    if SYSTEM == "Windows":
        print("  " + ("emptying" if really else "would empty") + " the Recycle Bin")
        if really:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"])
        return
    for d in trash_dirs():
        remove(d, really)


def clear_history(really: bool):
    for label, paths in targets():
        print(f"\n[{label}]")
        for p in paths:
            remove(p, really)
    if SYSTEM == "Windows" and really:
        # Clear Run dialog and Explorer typed-path history
        for key in [r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"]:
            subprocess.run(["reg", "delete", key, "/f"], capture_output=True)
        print("\n[Registry] cleared Run dialog and Explorer typed-path history")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="actually delete (default is a dry run)")
    ap.add_argument("--no-trash", action="store_true", help="skip emptying the trash")
    ap.add_argument("--no-history", action="store_true", help="skip clearing history")
    args = ap.parse_args()

    print(f"OS: {SYSTEM}   Mode: {'DELETE' if args.yes else 'DRY RUN (nothing deleted)'}")
    if not args.no_trash:
        empty_trash(args.yes)
    if not args.no_history:
        clear_history(args.yes)
    if not args.yes:
        print("\nDry run only. Re-run with --yes to delete these.")
    else:
        print("\nDone. A restart (or logging out) clears anything still held in memory.")


if __name__ == "__main__":
    main()

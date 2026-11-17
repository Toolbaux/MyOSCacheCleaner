# MyOSCacheCleaner

Cross-platform Python script that empties the trash / Recycle Bin and clears recent-file and app history on Windows, macOS, and Linux.

**Deletions are permanent.** Items removed with `--yes` cannot be recovered. Close browsers and other apps first so they do not recreate history.

Browser history (Chrome, Firefox, Safari, Edge, and others) is **not** covered.

## Usage

Dry run is the default. The script only lists what it would delete until you pass `--yes`.

```bash
python3 clear_history.py              # preview only
python3 clear_history.py --yes        # actually delete
python3 clear_history.py --no-trash   # preview history only
python3 clear_history.py --no-history # preview trash only
python3 clear_history.py --yes --no-trash   # delete history, leave trash
```

| Flag | Effect |
| --- | --- |
| *(none)* | Dry run. Prints paths; deletes nothing. |
| `--yes` | Permanently delete the listed items. |
| `--no-trash` | Skip emptying the trash / Recycle Bin. |
| `--no-history` | Skip recent-file and app history. |

## What it clears

### Windows

- Recycle Bin (`Clear-RecycleBin`)
- Recent files and jump lists
- User temp files (`%LOCALAPPDATA%\Temp`)
- Explorer thumbnail cache
- Windows Timeline / activity history (`ConnectedDevicesPlatform`)
- PowerShell PSReadLine history
- With `--yes` only: Run dialog (`RunMRU`) and Explorer typed paths

### macOS

- User trash (`~/.Trash`)
- Recent items (shared file list)
- Saved application state
- Quick Look thumbnail cache
- Shell and Python history (`.bash_history`, `.zsh_history`, `.python_history`, `.zsh_sessions`)

### Linux

- User trash (`~/.local/share/Trash`) and per-drive trash under `/media` and `/mnt`
- Recently used files (`recently-used.xbel`)
- Thumbnail cache (`~/.cache/thumbnails`, `~/.thumbnails`)
- Shell and Python history (bash, zsh, fish, `.python_history`)
- Zeitgeist activity log

## Requirements

Python 3. No third-party packages. On Windows, emptying the Recycle Bin and clearing registry keys uses `powershell` and `reg`, which ship with Windows.

"""Application control — open, close, discover apps."""

import subprocess
import os
from pathlib import Path
from typing import Optional, List

from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger

logger = get_logger("tools.applications")

# Common Windows applications and their typical paths/commands
_APP_REGISTRY = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "settings": "ms-settings:",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "snipping tool": "SnippingTool.exe",
    "snip": "SnippingTool.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
}

# Apps that might be in Program Files
_PROGRAM_FILES_APPS = {
    "chrome": [
        r"Google\Chrome\Application\chrome.exe",
    ],
    "google chrome": [
        r"Google\Chrome\Application\chrome.exe",
    ],
    "firefox": [
        r"Mozilla Firefox\firefox.exe",
    ],
    "mozilla firefox": [
        r"Mozilla Firefox\firefox.exe",
    ],
    "vs code": [
        r"Microsoft VS Code\Code.exe",
    ],
    "vscode": [
        r"Microsoft VS Code\Code.exe",
    ],
    "visual studio code": [
        r"Microsoft VS Code\Code.exe",
    ],
    "vlc": [
        r"VideoLAN\VLC\vlc.exe",
    ],
    "spotify": [
        r"Spotify\Spotify.exe",
    ],
}


class ApplicationTool(BaseTool):
    """Application management tool."""

    def execute(self, **kwargs) -> ToolResult:
        """Route to open or close."""
        action = kwargs.get("_action", "open_application")
        if action == "close_application":
            return self.close_application(**kwargs)
        return self.open_application(**kwargs)

    def open_application(self, app_name: str = "", **kwargs) -> ToolResult:
        """Open an application by name."""
        if not app_name:
            return ToolResult(success=False, error="No application name provided.")

        app_lower = app_name.lower().strip()
        logger.info(f"Attempting to open: {app_lower}")

        # Check built-in registry
        if app_lower in _APP_REGISTRY:
            cmd = _APP_REGISTRY[app_lower]
            return self._launch(cmd, app_name)

        # Check Program Files apps
        if app_lower in _PROGRAM_FILES_APPS:
            for relative_path in _PROGRAM_FILES_APPS[app_lower]:
                for base in self._get_program_dirs():
                    full_path = base / relative_path
                    if full_path.exists():
                        return self._launch(str(full_path), app_name)

        # Try Start Menu search
        start_path = self._find_in_start_menu(app_lower)
        if start_path:
            return self._launch(str(start_path), app_name)

        # Try running as command (some apps are in PATH)
        try:
            subprocess.Popen(app_lower, shell=False)
            return ToolResult(success=True, message=f"🚀 Opened: {app_name}")
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Try with shell=True as last resort for ms-settings: etc
        if ":" in app_lower:
            try:
                os.startfile(app_lower)
                return ToolResult(success=True, message=f"🚀 Opened: {app_name}")
            except Exception:
                pass

        return ToolResult(
            success=False,
            error=f"Could not find application: {app_name}. "
                  f"Try providing the full path or ensure it's installed."
        )

    def close_application(self, app_name: str = "", **kwargs) -> ToolResult:
        """Close an application by name."""
        if not app_name:
            return ToolResult(success=False, error="No application name provided.")

        try:
            # Use taskkill to close by image name
            process_name = app_name.lower().strip()
            if not process_name.endswith(".exe"):
                process_name += ".exe"

            result = subprocess.run(
                ["taskkill", "/IM", process_name, "/F"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                return ToolResult(success=True, message=f"✖️ Closed: {app_name}")
            else:
                # Try by window title
                result2 = subprocess.run(
                    ["taskkill", "/FI", f"WINDOWTITLE eq {app_name}*", "/F"],
                    capture_output=True, text=True, timeout=10
                )
                if result2.returncode == 0:
                    return ToolResult(success=True, message=f"✖️ Closed: {app_name}")
                return ToolResult(success=False, error=f"Could not close {app_name}: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Timeout closing {app_name}")
        except Exception as e:
            return ToolResult(success=False, error=f"Error closing {app_name}: {e}")

    def _launch(self, cmd: str, display_name: str) -> ToolResult:
        """Launch a command."""
        try:
            if cmd.startswith("ms-"):
                os.startfile(cmd)
            else:
                subprocess.Popen(cmd, shell=False)
            logger.info(f"Launched: {cmd}")
            return ToolResult(success=True, message=f"🚀 Opened: {display_name}")
        except FileNotFoundError:
            return ToolResult(success=False, error=f"Application not found: {cmd}")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to launch {display_name}: {e}")

    def _get_program_dirs(self) -> List[Path]:
        """Get Program Files directories."""
        dirs = []
        for env_var in ["ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"]:
            val = os.environ.get(env_var, "")
            if val:
                dirs.append(Path(val))
        return dirs

    def _find_in_start_menu(self, app_name: str) -> Optional[Path]:
        """Search Start Menu for an application."""
        start_dirs = []

        appdata = os.environ.get("APPDATA", "")
        if appdata:
            start_dirs.append(Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

        programdata = os.environ.get("ProgramData", "")
        if programdata:
            start_dirs.append(Path(programdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

        for start_dir in start_dirs:
            if not start_dir.exists():
                continue
            for item in start_dir.rglob("*.lnk"):
                if app_name in item.stem.lower():
                    return item

        return None

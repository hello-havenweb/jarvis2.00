"""File system tools — list, search, create, copy, move, rename, delete."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger
from utils.paths import resolve_user_path, get_special_folder

logger = get_logger("tools.filesystem")


class FileSystemTool(BaseTool):
    """File system operations tool."""

    def execute(self, **kwargs) -> ToolResult:
        """Route to appropriate file system action."""
        action = kwargs.get("_action", "list_files")

        dispatch = {
            "list_files": self.list_files,
            "search_files": self.search_files,
            "create_folder": self.create_folder,
            "delete_file": self.delete_file,
            "copy_file": self.copy_file,
            "move_file": self.move_file,
            "rename_file": self.rename_file,
            "read_file": self.read_file,
            "open_folder": self.open_folder,
            "open_file": self.open_file,
        }

        func = dispatch.get(action, self.list_files)
        return func(**kwargs)

    def list_files(self, path: str = "", **kwargs) -> ToolResult:
        """List files in a directory."""
        try:
            target = resolve_user_path(path) if path else Path.home()
            if not target.exists():
                return ToolResult(success=False, error=f"Path does not exist: {target}")

            items = sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            lines = [f"📁 Contents of {target}:"]

            for item in items[:50]:  # Limit to 50 items
                icon = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    try:
                        s = item.stat().st_size
                        size = f" ({self._format_size(s)})"
                    except OSError:
                        size = ""
                lines.append(f"  {icon} {item.name}{size}")

            if len(list(target.iterdir())) > 50:
                lines.append(f"  ... and {len(list(target.iterdir())) - 50} more items")

            return ToolResult(success=True, message="\n".join(lines))
        except PermissionError:
            return ToolResult(success=False, error=f"Permission denied: {path}")
        except Exception as e:
            return ToolResult(success=False, error=f"Error listing files: {e}")

    def search_files(self, query: str = "", path: str = "", **kwargs) -> ToolResult:
        """Search for files by name."""
        if not query:
            return ToolResult(success=False, error="No search query provided.")

        try:
            target = resolve_user_path(path) if path else Path.home()
            matches = []

            for item in target.rglob(f"*{query}*"):
                matches.append(str(item))
                if len(matches) >= 30:
                    break

            if not matches:
                return ToolResult(success=True, message=f"No files found matching '{query}'.")

            lines = [f"🔍 Search results for '{query}':"]
            for m in matches:
                lines.append(f"  📄 {m}")
            return ToolResult(success=True, message="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Search error: {e}")

    def create_folder(self, name: str = "", path: str = "", **kwargs) -> ToolResult:
        """Create a new folder."""
        if not name:
            return ToolResult(success=False, error="Folder name not provided.")

        try:
            base = resolve_user_path(path) if path else Path.home() / "Desktop"
            new_folder = base / name
            new_folder.mkdir(parents=True, exist_ok=True)
            return ToolResult(success=True, message=f"📁 Folder created: {new_folder}")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to create folder: {e}")

    def delete_file(self, path: str = "", **kwargs) -> ToolResult:
        """Delete a file or empty folder."""
        if not path:
            return ToolResult(success=False, error="No path provided.")

        try:
            target = resolve_user_path(path)
            if not target.exists():
                return ToolResult(success=False, error=f"Path does not exist: {target}")

            if target.is_file():
                target.unlink()
                return ToolResult(success=True, message=f"🗑️ Deleted file: {target}")
            elif target.is_dir():
                if any(target.iterdir()):
                    return ToolResult(
                        success=False,
                        error=f"Directory is not empty: {target}. Use recursive delete for non-empty directories."
                    )
                target.rmdir()
                return ToolResult(success=True, message=f"🗑️ Deleted folder: {target}")
            else:
                return ToolResult(success=False, error=f"Unknown path type: {target}")
        except PermissionError:
            return ToolResult(success=False, error=f"Permission denied: {path}")
        except Exception as e:
            return ToolResult(success=False, error=f"Delete failed: {e}")

    def copy_file(self, source: str = "", destination: str = "", path: str = "", **kwargs) -> ToolResult:
        """Copy a file."""
        if not source:
            return ToolResult(success=False, error="No source path provided.")
        if not destination:
            return ToolResult(success=False, error="No destination path provided.")

        try:
            src = resolve_user_path(source)
            dst = resolve_user_path(destination)

            if not src.exists():
                return ToolResult(success=False, error=f"Source does not exist: {src}")

            if src.is_file():
                shutil.copy2(str(src), str(dst))
            elif src.is_dir():
                shutil.copytree(str(src), str(dst))

            return ToolResult(success=True, message=f"📋 Copied: {src} → {dst}")
        except Exception as e:
            return ToolResult(success=False, error=f"Copy failed: {e}")

    def move_file(self, source: str = "", destination: str = "", path: str = "", **kwargs) -> ToolResult:
        """Move a file."""
        if not source:
            return ToolResult(success=False, error="No source path provided.")
        if not destination:
            return ToolResult(success=False, error="No destination path provided.")

        try:
            src = resolve_user_path(source)
            dst = resolve_user_path(destination)

            if not src.exists():
                return ToolResult(success=False, error=f"Source does not exist: {src}")

            shutil.move(str(src), str(dst))
            return ToolResult(success=True, message=f"📦 Moved: {src} → {dst}")
        except Exception as e:
            return ToolResult(success=False, error=f"Move failed: {e}")

    def rename_file(self, path: str = "", new_name: str = "", **kwargs) -> ToolResult:
        """Rename a file or folder."""
        if not path or not new_name:
            return ToolResult(success=False, error="Path and new name are required.")

        try:
            target = resolve_user_path(path)
            if not target.exists():
                return ToolResult(success=False, error=f"Path does not exist: {target}")

            new_path = target.parent / new_name
            target.rename(new_path)
            return ToolResult(success=True, message=f"✏️ Renamed: {target.name} → {new_name}")
        except Exception as e:
            return ToolResult(success=False, error=f"Rename failed: {e}")

    def read_file(self, path: str = "", **kwargs) -> ToolResult:
        """Read a text file."""
        if not path:
            return ToolResult(success=False, error="No file path provided.")

        try:
            target = resolve_user_path(path)
            if not target.exists():
                return ToolResult(success=False, error=f"File does not exist: {target}")

            if not target.is_file():
                return ToolResult(success=False, error=f"Not a file: {target}")

            # Limit read size
            size = target.stat().st_size
            if size > 1024 * 1024:  # 1 MB
                return ToolResult(
                    success=False,
                    error=f"File too large to read ({self._format_size(size)}). Max: 1 MB."
                )

            content = target.read_text(encoding="utf-8", errors="replace")
            return ToolResult(
                success=True,
                message=f"📄 Contents of {target.name}:\n\n{content[:5000]}",
                data=content
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Read failed: {e}")

    def open_folder(self, folder: str = "", **kwargs) -> ToolResult:
        """Open a folder in File Explorer."""
        try:
            if not folder:
                folder = "desktop"

            # Special folders
            special = get_special_folder(folder)
            if special and special.exists():
                target = special
            else:
                target = resolve_user_path(folder)

            if not target.exists():
                return ToolResult(success=False, error=f"Folder does not exist: {target}")

            subprocess.Popen(["explorer", str(target)])
            return ToolResult(success=True, message=f"📂 Opened: {target}")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to open folder: {e}")

    def open_file(self, path: str = "", **kwargs) -> ToolResult:
        """Open a file with default application."""
        if not path:
            return ToolResult(success=False, error="No file path provided.")

        try:
            target = resolve_user_path(path)
            if not target.exists():
                return ToolResult(success=False, error=f"File does not exist: {target}")

            os.startfile(str(target))
            return ToolResult(success=True, message=f"📄 Opened: {target}")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to open file: {e}")

    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

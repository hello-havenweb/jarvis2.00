"""System control tools — info, volume, shutdown, etc."""

import platform
import subprocess
from datetime import datetime
from typing import Optional

import psutil

from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger

logger = get_logger("tools.system")


class SystemTool(BaseTool):
    """System information and control tool."""

    def execute(self, **kwargs) -> ToolResult:
        """Route to the appropriate system action based on registered tool name."""
        # The executor calls this with _action or we detect from context
        action = kwargs.get("_action", "system_info")

        dispatch = {
            "system_info": self.system_info,
            "show_time": self.show_time,
            "show_date": self.show_date,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "mute": self.mute,
            "lock_pc": self.lock_pc,
            "shutdown_pc": self.shutdown_pc,
            "restart_pc": self.restart_pc,
        }

        func = dispatch.get(action, self.system_info)
        return func()

    def system_info(self) -> ToolResult:
        """Get system information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            info_lines = [
                "💻 System Information:",
                f"  OS: {platform.system()} {platform.release()} ({platform.machine()})",
                f"  CPU: {cpu_percent}% used ({psutil.cpu_count()} cores)",
                f"  RAM: {memory.percent}% used ({self._format_bytes(memory.used)} / {self._format_bytes(memory.total)})",
                f"  Disk: {disk.percent}% used ({self._format_bytes(disk.used)} / {self._format_bytes(disk.total)})",
            ]

            # Battery
            battery = psutil.sensors_battery()
            if battery:
                plug = "🔌 Plugged in" if battery.power_plugged else "🔋 On battery"
                info_lines.append(f"  Battery: {battery.percent}% ({plug})")

            # Network
            net = psutil.net_if_addrs()
            info_lines.append(f"  Network interfaces: {len(net)}")

            # Uptime
            boot = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            info_lines.append(f"  Uptime: {hours}h {minutes}m")

            return ToolResult(success=True, message="\n".join(info_lines))

        except Exception as e:
            logger.error(f"System info error: {e}")
            return ToolResult(success=False, error=f"Failed to get system info: {e}")

    def show_time(self) -> ToolResult:
        """Show current time."""
        now = datetime.now()
        return ToolResult(
            success=True,
            message=f"🕐 Current time: {now.strftime('%I:%M %p')}"
        )

    def show_date(self) -> ToolResult:
        """Show current date."""
        now = datetime.now()
        return ToolResult(
            success=True,
            message=f"📅 Today's date: {now.strftime('%A, %B %d, %Y')}"
        )

    def volume_up(self) -> ToolResult:
        """Increase system volume."""
        try:
            from ctypes import cast, POINTER
            import comtypes
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = min(1.0, current + 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return ToolResult(success=True, message=f"🔊 Volume: {int(new_vol * 100)}%")
        except ImportError:
            # Fallback using nircmd or keyboard simulation
            try:
                import subprocess
                subprocess.run(
                    ["powershell", "-Command",
                     "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"],
                    capture_output=True, timeout=5
                )
                return ToolResult(success=True, message="🔊 Volume increased.")
            except Exception as e2:
                return ToolResult(success=False, error=f"Volume control not available: {e2}")
        except Exception as e:
            return ToolResult(success=False, error=f"Volume error: {e}")

    def volume_down(self) -> ToolResult:
        """Decrease system volume."""
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-Command",
                 "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"],
                capture_output=True, timeout=5
            )
            return ToolResult(success=True, message="🔉 Volume decreased.")
        except Exception as e:
            return ToolResult(success=False, error=f"Volume error: {e}")

    def mute(self) -> ToolResult:
        """Mute/unmute system volume."""
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-Command",
                 "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"],
                capture_output=True, timeout=5
            )
            return ToolResult(success=True, message="🔇 Volume muted/unmuted.")
        except Exception as e:
            return ToolResult(success=False, error=f"Mute error: {e}")

    def lock_pc(self) -> ToolResult:
        """Lock the PC."""
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"],
                           capture_output=True, timeout=5)
            return ToolResult(success=True, message="🔒 PC locked.")
        except Exception as e:
            return ToolResult(success=False, error=f"Lock failed: {e}")

    def shutdown_pc(self) -> ToolResult:
        """Shutdown the PC."""
        try:
            subprocess.run(["shutdown", "/s", "/t", "30", "/c",
                            "JARVIS: Shutting down in 30 seconds. Run 'shutdown /a' to cancel."],
                           capture_output=True, timeout=5)
            return ToolResult(
                success=True,
                message="⚡ Shutdown scheduled in 30 seconds. Run 'shutdown /a' in CMD to cancel."
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Shutdown failed: {e}")

    def restart_pc(self) -> ToolResult:
        """Restart the PC."""
        try:
            subprocess.run(["shutdown", "/r", "/t", "30", "/c",
                            "JARVIS: Restarting in 30 seconds. Run 'shutdown /a' to cancel."],
                           capture_output=True, timeout=5)
            return ToolResult(
                success=True,
                message="🔄 Restart scheduled in 30 seconds. Run 'shutdown /a' in CMD to cancel."
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Restart failed: {e}")

    @staticmethod
    def _format_bytes(b: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

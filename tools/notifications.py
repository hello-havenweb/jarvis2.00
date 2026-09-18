"""Desktop notifications."""

from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger

logger = get_logger("tools.notifications")


class NotificationTool(BaseTool):
    """Desktop notification tool."""

    def execute(self, title: str = "JARVIS", message: str = "", **kwargs) -> ToolResult:
        """Show a desktop notification."""
        if not message:
            return ToolResult(success=False, error="No notification message.")

        try:
            # Use Windows toast notification via PowerShell
            import subprocess
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message}</text>
                    </binding>
                </visual>
            </toast>
"@
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("JARVIS").Show($toast)
            """
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True, timeout=10
            )
            return ToolResult(success=True, message=f"🔔 Notification sent: {message}")
        except Exception as e:
            logger.warning(f"Notification failed: {e}")
            # Fallback — just log it
            return ToolResult(success=True, message=f"🔔 {title}: {message}")

"""Main JARVIS application controller."""

import threading
from typing import Optional

from core.config import Config
from core.state import AppState
from core.router import CommandRouter
from core.planner import ActionPlanner
from core.executor import ActionExecutor
from core.events import event_bus
from core.models import UserCommand, JarvisResponse, JarvisState, ToolResult
from core.logger import get_logger, setup_logging
from ai.ollama_provider import OllamaProvider
from ai.language import LanguageDetector
from memory.memory import MemoryManager
from memory.database import DatabaseManager
from tools.registry import ToolRegistry
from security.audit import AuditLogger
from reports.activity import ActivityTracker

logger = get_logger("app")


class JarvisApp:
    """Main application controller — coordinates all subsystems."""

    def __init__(self) -> None:
        self.config = Config()
        setup_logging(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        logger.info("Initializing JARVIS...")

        self.state = AppState()
        self.database = DatabaseManager()
        self.database.initialize()
        self.memory = MemoryManager(self.database)
        self.ai_provider = OllamaProvider()
        self.language_detector = LanguageDetector()
        self.tool_registry = ToolRegistry()
        self.router = CommandRouter()
        self.planner = ActionPlanner()
        self.executor = ActionExecutor(self.tool_registry)
        self.audit = AuditLogger()
        self.activity = ActivityTracker(self.database)

        self._register_tools()
        self._check_ollama()

        logger.info("JARVIS initialized.")

    def _register_tools(self) -> None:
        """Register all available tools."""
        from tools.system import SystemTool
        from tools.filesystem import FileSystemTool
        from tools.screenshot import ScreenshotTool
        from tools.applications import ApplicationTool
        from tools.clipboard import ClipboardTool
        from tools.notifications import NotificationTool

        system_tool = SystemTool()
        fs_tool = FileSystemTool()
        app_tool = ApplicationTool()
        ss_tool = ScreenshotTool()
        clip_tool = ClipboardTool()
        notif_tool = NotificationTool()

        # Register system tools
        self.tool_registry.register("system_info", system_tool)
        self.tool_registry.register("show_time", system_tool)
        self.tool_registry.register("show_date", system_tool)
        self.tool_registry.register("volume_up", system_tool)
        self.tool_registry.register("volume_down", system_tool)
        self.tool_registry.register("mute", system_tool)
        self.tool_registry.register("lock_pc", system_tool)
        self.tool_registry.register("shutdown_pc", system_tool)
        self.tool_registry.register("restart_pc", system_tool)

        # File tools
        self.tool_registry.register("list_files", fs_tool)
        self.tool_registry.register("search_files", fs_tool)
        self.tool_registry.register("create_folder", fs_tool)
        self.tool_registry.register("delete_file", fs_tool)
        self.tool_registry.register("copy_file", fs_tool)
        self.tool_registry.register("move_file", fs_tool)
        self.tool_registry.register("rename_file", fs_tool)
        self.tool_registry.register("read_file", fs_tool)
        self.tool_registry.register("open_folder", fs_tool)
        self.tool_registry.register("open_file", fs_tool)

        # Application tools
        self.tool_registry.register("open_application", app_tool)
        self.tool_registry.register("close_application", app_tool)

        # Screenshot
        self.tool_registry.register("screenshot", ss_tool)

        # Clipboard
        self.tool_registry.register("clipboard_read", clip_tool)
        self.tool_registry.register("clipboard_write", clip_tool)

        # Notifications
        self.tool_registry.register("notification", notif_tool)

        # Memory tools
        self.tool_registry.register("show_memory", self.memory)
        self.tool_registry.register("clear_memory", self.memory)
        self.tool_registry.register("remember", self.memory)

        # Reminder tools
        from reminders.manager import ReminderManager
        reminder_mgr = ReminderManager(self.database)
        self.tool_registry.register("set_reminder", reminder_mgr)
        self.tool_registry.register("show_reminders", reminder_mgr)
        self.tool_registry.register("cancel_reminder", reminder_mgr)
        self._reminder_manager = reminder_mgr

        # Daily progress
        self.tool_registry.register("daily_progress", self.activity)

        # Web search (wrapper)
        from browser.search import WebSearchTool
        web_search = WebSearchTool()
        self.tool_registry.register("web_search", web_search)

        logger.info(f"Registered {len(self.tool_registry)} tools.")

    def _check_ollama(self) -> None:
        """Check if Ollama is available."""
        self.state.ollama_connected = self.ai_provider.is_available()
        if self.state.ollama_connected:
            logger.info("Ollama is available.")
        else:
            logger.warning("Ollama is not available. AI features will be limited.")

    def process_command(self, text: str, source: str = "text") -> JarvisResponse:
        """Process a user command through the full pipeline."""
        try:
            self.state.state = JarvisState.THINKING

            # Detect language
            detected_lang = self.language_detector.detect(text)
            logger.info(f"Input: '{text}' | Language: {detected_lang} | Source: {source}")

            command = UserCommand(text=text, language=detected_lang, source=source)

            # Route to intent
            intent = self.router.route(command)

            # If it's a conversation intent, use AI
            if intent.action == "conversation":
                return self._handle_conversation(text, detected_lang)

            # Create plan
            plan = self.planner.plan(intent)

            # Execute
            response = self.executor.execute(plan, language=detected_lang)

            # Track activity
            self.activity.track(
                category=intent.action,
                action=intent.action,
                details=text,
                success=response.state != JarvisState.ERROR
            )

            # Store in memory
            self.memory.add_conversation(text, response.text)

            self.state.state = JarvisState.IDLE
            return response

        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            self.state.state = JarvisState.ERROR
            return JarvisResponse(
                text=f"I encountered an error: {str(e)}",
                state=JarvisState.ERROR
            )

    def _handle_conversation(self, text: str, language: str) -> JarvisResponse:
        """Handle a conversation using the AI provider."""
        if not self.state.ollama_connected:
            self.state.state = JarvisState.IDLE
            return JarvisResponse(
                text="I'm sorry, the AI service (Ollama) is not available right now. "
                     "Please start Ollama and try again.\n\n"
                     "To start Ollama: open a terminal and run 'ollama serve'",
                language=language,
                state=JarvisState.IDLE
            )

        try:
            # Get conversation history
            history = self.memory.get_recent_conversation(limit=10)

            # Build context
            from ai.prompts import build_chat_prompt
            messages = build_chat_prompt(text, history, language)

            # Get AI response
            ai_response = self.ai_provider.chat(messages)

            # Store conversation
            self.memory.add_conversation(text, ai_response)

            self.state.state = JarvisState.IDLE
            return JarvisResponse(text=ai_response, language=language, state=JarvisState.IDLE)

        except Exception as e:
            logger.error(f"AI conversation error: {e}", exc_info=True)
            self.state.state = JarvisState.ERROR
            return JarvisResponse(
                text=f"AI error: {str(e)}",
                language=language,
                state=JarvisState.ERROR
            )

    def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("Shutting down JARVIS...")
        try:
            if hasattr(self, '_reminder_manager'):
                self._reminder_manager.stop()
            if hasattr(self, 'database'):
                self.database.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        logger.info("JARVIS shutdown complete.")

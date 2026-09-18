"""Executes action plans using the tool registry."""

from typing import Optional

from core.models import ActionPlan, ToolResult, JarvisResponse, JarvisState, PermissionLevel
from core.logger import get_logger
from core.events import event_bus
from core.exceptions import PermissionDeniedError, ToolNotFoundError, ToolExecutionError
from tools.registry import ToolRegistry
from security.audit import AuditLogger

logger = get_logger("executor")


class ActionExecutor:
    """Executes action plans with permission checks."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tools = tool_registry
        self.audit = AuditLogger()
        self._confirmation_callback = None

    def set_confirmation_callback(self, callback) -> None:
        """Set the callback function for requesting user confirmation."""
        self._confirmation_callback = callback

    def execute(self, plan: ActionPlan, language: str = "en") -> JarvisResponse:
        """Execute an action plan."""
        if plan.permission_level == PermissionLevel.BLOCKED:
            msg = "This action is blocked by security policy."
            logger.warning(f"Blocked action: {plan.description}")
            self.audit.log_action(
                command=plan.description,
                intent=plan.steps[0].action if plan.steps else "unknown",
                tool="blocked",
                permission=PermissionLevel.BLOCKED.value,
                confirmed=False,
                result="BLOCKED",
                error=msg
            )
            return JarvisResponse(text=msg, language=language, state=JarvisState.ERROR)

        # Handle confirmation
        if plan.requires_confirmation:
            if self._confirmation_callback:
                confirmed = self._confirmation_callback(plan.description)
                if not confirmed:
                    msg = "Action cancelled by user."
                    self.audit.log_action(
                        command=plan.description,
                        intent=plan.steps[0].action if plan.steps else "unknown",
                        tool="cancelled",
                        permission=plan.permission_level.value,
                        confirmed=False,
                        result="CANCELLED"
                    )
                    return JarvisResponse(text=msg, language=language, state=JarvisState.IDLE)

        results = []
        event_bus.publish("state_changed", state=JarvisState.EXECUTING, previous=JarvisState.THINKING)

        for step in plan.steps:
            try:
                result = self._execute_step(step)
                results.append(result)

                self.audit.log_action(
                    command=step.raw_text,
                    intent=step.action,
                    tool=step.tool or step.action,
                    parameters=step.parameters,
                    permission=plan.permission_level.value,
                    confirmed=plan.requires_confirmation,
                    result="SUCCESS" if result.success else "FAILED",
                    error=result.error
                )

            except Exception as e:
                error_msg = f"Error executing {step.action}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results.append(ToolResult(success=False, error=error_msg))
                self.audit.log_action(
                    command=step.raw_text,
                    intent=step.action,
                    tool=step.tool or step.action,
                    permission=plan.permission_level.value,
                    confirmed=plan.requires_confirmation,
                    result="ERROR",
                    error=error_msg
                )

        # Compose response
        response_parts = []
        all_success = True
        for r in results:
            if r.success:
                response_parts.append(r.message)
            else:
                all_success = False
                response_parts.append(f"Error: {r.error or r.message}")

        response_text = "\n".join(response_parts) if response_parts else "Done."

        return JarvisResponse(
            text=response_text,
            language=language,
            tool_results=results,
            state=JarvisState.IDLE if all_success else JarvisState.ERROR
        )

    def _execute_step(self, intent) -> ToolResult:
        """Execute a single intent step."""
        tool_name = intent.tool or intent.action

        tool = self.tools.get(tool_name)
        if tool is None:
            # If it's a conversation, handle differently
            if intent.action == "conversation":
                return ToolResult(success=True, message="", data={"needs_ai": True, "message": intent.parameters.get("message", "")})
            raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry.")

        return tool.execute(**intent.parameters)

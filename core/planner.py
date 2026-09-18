"""Plans action sequences from intents."""

from core.models import Intent, ActionPlan, PermissionLevel
from core.logger import get_logger
from security.permissions import PermissionManager

logger = get_logger("planner")


class ActionPlanner:
    """Creates action plans from intents."""

    def __init__(self) -> None:
        self.permission_mgr = PermissionManager()

    def plan(self, intent: Intent) -> ActionPlan:
        """Create an action plan from an intent."""
        permission = self.permission_mgr.get_permission_level(intent.action)

        plan = ActionPlan(
            steps=[intent],
            requires_confirmation=(permission in (PermissionLevel.CONFIRM, PermissionLevel.DANGEROUS)),
            permission_level=permission,
            description=self._describe_plan(intent, permission)
        )

        logger.info(f"Plan created: action={intent.action}, permission={permission.value}, "
                     f"confirm={plan.requires_confirmation}")
        return plan

    def _describe_plan(self, intent: Intent, permission: PermissionLevel) -> str:
        """Create human-readable description of the plan."""
        action = intent.action
        params = intent.parameters

        descriptions = {
            "open_application": f"Open application: {params.get('app_name', 'unknown')}",
            "close_application": f"Close application: {params.get('app_name', 'unknown')}",
            "system_info": "Show system information",
            "screenshot": "Take a screenshot",
            "create_folder": f"Create folder: {params.get('name', 'unknown')}",
            "delete_file": f"Delete: {params.get('path', 'unknown')}",
            "send_email": f"Send email to: {params.get('to', 'unknown')}",
            "send_whatsapp": f"Send WhatsApp message to: {params.get('contact', 'unknown')}",
            "shutdown_pc": "Shut down the computer",
            "restart_pc": "Restart the computer",
            "batch_process": f"Process files in batches of {params.get('size', 5)}",
            "conversation": "Have a conversation with AI",
            "web_search": f"Search the web for: {params.get('query', '')}",
        }

        desc = descriptions.get(action, f"Execute: {action}")
        if permission == PermissionLevel.DANGEROUS:
            desc = f"⚠️ DANGEROUS: {desc}"
        elif permission == PermissionLevel.CONFIRM:
            desc = f"⚡ {desc} (requires confirmation)"
        return desc

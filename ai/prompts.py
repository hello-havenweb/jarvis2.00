"""Prompt templates for JARVIS AI interactions."""

from typing import List, Dict, Tuple


SYSTEM_PROMPT = """You are JARVIS, a highly capable personal AI assistant. 
You are helpful, concise, and professional. You run locally on the user's Windows PC.

Key behaviors:
- Be direct and helpful
- If asked to perform an action, describe what you would do
- Support multiple languages — respond in the language the user uses
- You can help with: PC operations, file management, web browsing, email, scheduling, and general questions
- Be aware of system context provided to you
- When uncertain, ask for clarification
- Never make up information — say "I don't know" if unsure

Current capabilities:
- Open/close applications
- File operations (list, search, create, copy, move, delete)
- System information (CPU, RAM, disk)
- Screenshots
- Web searching
- Reminders and scheduling
- Memory and conversation history
- Daily activity reports
"""


def build_chat_prompt(
    user_message: str,
    history: List[Tuple[str, str]],
    language: str = "en"
) -> List[Dict[str, str]]:
    """Build the chat prompt with context."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Add conversation history
    for user_msg, assistant_msg in history[-8:]:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    # Add current message
    messages.append({"role": "user", "content": user_message})

    return messages


def build_intent_prompt(user_message: str, language: str = "en") -> str:
    """Build a prompt for intent detection."""
    return f"""Analyze the following user command and extract the intent.

User command: "{user_message}"
Detected language: {language}

Respond with ONLY a JSON object in this exact format:
{{
    "action": "<action_name>",
    "tool": "<tool_name>",
    "parameters": {{}},
    "confidence": 0.0
}}

Available actions:
- open_application (params: app_name)
- close_application (params: app_name)
- system_info
- screenshot
- create_folder (params: name, path)
- delete_file (params: path)
- list_files (params: path)
- search_files (params: query, path)
- web_search (params: query)
- open_folder (params: folder)
- set_reminder (params: text, time)
- show_reminders
- daily_progress
- show_time
- show_memory
- send_email (params: to, subject, body)
- send_whatsapp (params: contact, message)
- conversation (for general chat)

If the command doesn't match any specific action, use "conversation".
"""

# JARVIS — Personal AI Desktop Assistant

A local-first, privacy-respecting AI desktop assistant for Windows 10/11.

## Requirements

- **Windows 10/11 64-bit**
- **Python 3.11.x** (recommended: 3.11.9)
- **Ollama** (for local LLM) — https://ollama.ai
- Microphone (optional — text mode always available)
- Internet (optional — for browser/email features)

## Quick Install

1. Install Python 3.11.x from https://python.org (check "Add to PATH")
2. Install Ollama from https://ollama.ai
3. Pull a model: `ollama pull llama3`
4. Extract this project to a folder (e.g., `C:\JARVIS`)
5. Double-click `install.bat`
6. Double-click `run_jarvis.bat`

## Features

### Always Available
- Text command input
- AI conversation (via Ollama)
- PC control (open apps, system info, volume, etc.)
- File management
- Screenshot capture
- Clipboard operations
- Memory & conversation history
- Reminders
- Daily progress reports
- Permission system & audit log

### Optional (configure in .env)
- Voice input (requires microphone + faster-whisper)
- Text-to-speech (pyttsx3)
- Browser automation (Playwright)
- Email (IMAP/SMTP)
- WhatsApp Web automation
- HAVEN business data

## Multilingual Support

JARVIS auto-detects language. Supported:
English, Urdu, Roman Urdu, Hindi, Punjabi, Arabic, Spanish, French, German, Chinese, Japanese, and more.

Mixed-language commands work:
- "JARVIS Chrome kholo"
- "JARVIS open this folder aur files dikhao"

Change language: "Speak Urdu", "Speak English", "Auto language mode"

## Commands

| Command | Description |
|---|---|
| `open Chrome` | Open Chrome browser |
| `open Downloads` | Open Downloads folder |
| `show system status` | Show CPU, RAM, disk info |
| `take screenshot` | Capture screen |
| `create folder Test` | Create a new folder |
| `set reminder tomorrow at 10 AM call Ahmed` | Set reminder |
| `show today's progress` | Daily activity report |
| `process this folder in batches of 5` | Batch processing |

## Diagnostics

Run `diagnose.bat` to check all subsystems.

## Troubleshooting

1. **"Python not found"** — Install Python 3.11.x, ensure it's in PATH
2. **"Ollama not running"** — Start Ollama: `ollama serve`
3. **"No microphone"** — Text mode still works
4. **"Browser error"** — Run `playwright install chromium`
5. **Import errors** — Run `install.bat` again

## Uninstall

Run `uninstall.bat` to remove the virtual environment. Your data in `data/` is preserved unless you delete it manually.

## Backup

Important data is in `data/`. Back up this folder regularly.

# 🎙️ AI Speech to Text

<div align="center">

**Hold SHIFT to speak, release to type.** Fast, accurate voice-to-text using Groq Whisper API.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)](https://github.com/TheD0SH/ai-speech-to-text/releases)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎤 **Push-to-Talk** | Hold SHIFT to record, release to transcribe |
| ⚡ **Fast** | ~0.5s transcription using Groq Whisper API |
| 🎯 **Accurate** | Uses Whisper large-v3-turbo model |
| 🔢 **Accounting Mode** | Converts "one hundred" → "100" |
| 💬 **Casual Mode** | Lowercase output with informal punctuation |
| 😀 **Emoji Support** | Say "happy emoji" → 😊 (100+ emojis) |
| 🎹 **Custom Hotkeys** | Change push-to-talk key in settings |
| 🚫 **Filter Words** | Block unwanted phrases |

## 📥 Installation

### Windows (Recommended)
1. Go to releases folder
2. Double-click to run - no installation needed!

### macOS
1. Go to releases
2. Double-click and follow the installer
3. Find VoiceType in your Applications folder

### From Source
```bash
# Clone the repo
git clone https://github.com/TheD0SH/ai-speech-to-text.git
cd ai-speech-to-text

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python voice_type.py
```

### Using .env (Optional)
```bash
# Copy example file
cp example.env .env

# Edit .env and add your API key
GROQ_API_KEY=your_key_here
```

## ⚙️ Setup

1. Get a **free** API key from [Groq Console](https://console.groq.com/keys)
2. Right-click tray icon → **Settings** (opens automatically on first run)
3. Paste your API key
4. Select your microphone
5. Configure features
6. Click **Save**

## 🚀 Usage

1. Place your cursor where you want text
2. **Hold SHIFT** and speak (widget appears)
3. **Release SHIFT** to transcribe
4. Text appears at your cursor!
5. Widget auto-hides after 2 seconds

## 🔢 Features in Detail

### Accounting Mode
Converts spoken number words to digits:
| You Say | You Get |
|---------|---------|
| "one" | "1" |
| "twenty five" | "25" |
| "one hundred" | "100" |
| "one million" | "1,000,000" (with comma option) |

### Casual Mode
Outputs lowercase text with informal punctuation:
- No capitalization
- Periods removed
- Multiple punctuation reduced (`!!!` → `!`)

### Emoji Support
Speak emoji names to insert actual emojis:

| Say This | Get This |
|----------|----------|
| "happy emoji" | 😊 |
| "fire emoji" | 🔥 |
| "thumbs up emoji" | 👍 |
| "rocket emoji" | 🚀 |

**100+ emojis supported!**

## 📋 Two Versions

| Version | File | Best For |
|---------|------|----------|
| **Full** | `VoiceType.exe` | Most users - all features |
| **Lite** | `VoiceTypeLite.exe` | Older/slower computers |

**Lite Version:**
- Uses faster model (distil-whisper-large-v3-en)
- No system tray (less memory)
- No emoji conversion
- Simpler UI

## 🛠️ Building from Source

### Windows
```bash
pip install pyinstaller
pyinstaller VoiceType.spec --noconfirm
```

### macOS
```bash
chmod +x build-mac.sh
./build-mac.sh
```

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "No API key" error | Get free key from [console.groq.com](https://console.groq.com/keys) |
| Microphone not detected | Check system permissions, restart app |
| Transcription is empty | Speak louder, check mic in settings |
| "Rate limited" error | Wait a moment, will auto-retry |
| Network errors | Check internet connection |

## 📜 Version History

| Version | Changes |
|---------|---------|
| **v1.2.0** | Accounting mode, casual mode, filter words, blue theme, Lite version |
| **v1.1.0** | Emoji support, custom hotkeys |
| **v1.0.0** | Initial release |

## 🔒 Security

- API keys stored locally in `~/.voice-type-config.json`
- Audio processed in real-time, not saved to disk
- No data sent anywhere except Groq API

## 📄 Requirements

- Python 3.8+
- Microphone
- Internet connection
- Groq API key (free tier available)

## 📝 License

MIT License - use freely!

---

<div align="center">

Made with ❤️ for productivity

**[Get Started](https://github.com/TheD0SH/ai-speech-to-text/releases)** | **[Report Bug](https://github.com/TheD0SH/ai-speech-to-text/issues)** | **[Request Feature](https://github.com/TheD0SH/ai-speech-to-text/issues)**

</div>

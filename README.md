# 🎙️ VoiceType - AI Speech to Text

<div align="center">

**Hold SHIFT to speak, release to type.** Lightning-fast, accurate voice-to-text powered by Groq Whisper API.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com/)
[![Version](https://img.shields.io/badge/Version-2.3.0-blue)](https://github.com/TheD0SH/ai-speech-to-text/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://github.com/TheD0SH/ai-speech-to-text/releases)

**50+ Features • 60 Voice Commands • Professional Grade**

</div>

---

## ✨ Features Overview

| Category | Highlights |
|----------|------------|
| 🎤 **Core** | Push-to-talk, ~0.5s transcription, Whisper large-v3-turbo |
| 📝 **Text Processing** | Accounting mode, casual mode, smart quotes, capitalize sentences |
| 🎨 **UI/UX** | Dark/light themes, 6 accent colors, compact mode, recording timer |
| 📜 **History** | Transcription history with search & export |
| 🎤 **Voice Commands** | 60+ commands (delete, select, copy, paste, punctuation, etc.) |
| 📚 **Vocabulary** | Custom vocabulary, word replacements, voice macros |
| 🌍 **International** | 15+ languages with auto-detection |
| 💾 **Audio** | Save recordings, transcribe files from disk |
| ⚙️ **Platform** | Auto-start, always-on-top, minimize to tray |

## 🆕 What's New in v2.3.0

### Major Features (18 new!)
- **Voice Macros** - Custom shortcuts with `{{DATE}}` and `{{TIME}}` placeholders
- **Statistics Dashboard** - Track words, sessions, transcriptions, time saved
- **History with Search** - Search past transcriptions, export to file
- **Custom Vocabulary** - Add industry-specific terms for better accuracy
- **Word Replacements** - Auto-replace words (e.g., "teh" → "the")
- **Quick Snippets (F2)** - 10 common phrases at your fingertips
- **Context Menu** - Right-click widget for quick actions
- **Compact Mode** - Smaller widget for minimal screen space
- **6 Accent Colors** - Purple, blue, green, red, orange, pink
- **Recording Timer** - See recording duration in real-time
- **Widget Position Memory** - Remembers where you put it
- **Auto-Copy to Clipboard** - Optionally copy every transcription
- **Save Audio Recordings** - Keep recordings for reference
- **Transcribe Audio Files** - Transcribe WAV, MP3, M4A, OGG, FLAC
- **Minimize to Tray** - Start hidden, show when needed
- **Reset to Defaults** - One-click settings reset
- **Expanded Voice Commands** - Select all, copy, paste, undo, redo, repeat
- **60 Voice Commands** - Punctuation, symbols, navigation, editing

### Improvements
- 3x more features than v1.x
- Professional-grade UI with themes
- Comprehensive voice command system
- Better error handling and recovery
- Improved keyboard shortcuts overlay (F1)
- Word and character count display

## 📥 Installation

### Windows (Recommended)
1. Download **VoiceType.exe** from the [dist folder](dist/) or [releases](https://github.com/TheD0SH/ai-speech-to-text/releases)
2. Double-click to run - **no installation needed!**

### Portable Version
1. Download **VoiceType.zip**
2. Extract anywhere
3. Run `VoiceType.exe`

### Lite Version (For Older Computers)
1. Download **VoiceTypeLite.exe**
2. Lighter on resources, fewer features
3. Uses faster distil-whisper model

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
5. Configure features (20+ options!)
6. Click **Save**

## 🚀 Usage

### Basic Usage
1. Place your cursor where you want text
2. **Hold SHIFT** and speak (widget appears)
3. **Release SHIFT** to transcribe
4. Text appears at your cursor!
5. Widget auto-hides after 2 seconds

### Quick Snippets (F2)
Press **F2** to open quick snippets popup with common phrases:
- Email templates
- Meeting responses
- Follow-up messages
- Professional closings

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| **Hold SHIFT** | Push-to-talk recording |
| **F1** | Show keyboard shortcuts overlay |
| **F2** | Show quick snippets popup |

### Right-Click Menu
Right-click the widget for quick actions:
- Copy last transcription
- Open history
- Open settings
- Toggle always-on-top
- Minimize to tray

## 🎤 Voice Commands (60+)

### Editing Commands
| Say This | Action |
|----------|--------|
| "delete last word" | Deletes last word |
| "delete last sentence" | Deletes last sentence |
| "delete all" | Deletes everything |
| "undo that" | Deletes last word |
| "scratch that" | Deletes last word |

### Navigation Commands
| Say This | Action |
|----------|--------|
| "select all" | Selects all text |
| "copy that" | Copies to clipboard |
| "paste" | Pastes from clipboard |
| "cut that" | Cuts to clipboard |
| "undo" | Undo (Ctrl+Z) |
| "redo" | Redo (Ctrl+Y) |
| "repeat last" | Types last transcription again |

### Formatting Commands
| Say This | You Get |
|----------|---------|
| "new paragraph" | `\n\n` |
| "new line" | `\n` |
| "tab" | `\t` |

### Punctuation Commands
| Say This | You Get |
|----------|---------|
| "period" / "full stop" | `.` |
| "comma" | `,` |
| "question mark" | `?` |
| "exclamation mark" | `!` |
| "colon" | `:` |
| "semicolon" | `;` |
| "quote" / "open quote" / "close quote" | `"` |
| "apostrophe" | `'` |

### Brackets
| Say This | You Get |
|----------|---------|
| "open parenthesis" | `(` |
| "close parenthesis" | `)` |
| "open bracket" | `[` |
| "close bracket" | `]` |
| "open brace" | `{` |
| "close brace" | `}` |

### Special Characters
| Say This | You Get |
|----------|---------|
| "at sign" / "at symbol" | `@` |
| "hash" / "hashtag" | `#` |
| "percent" / "percent sign" | `%` |
| "ampersand" | `&` |
| "asterisk" | `*` |
| "plus sign" | `+` |
| "minus sign" | `-` |
| "equals" | `=` |
| "slash" | `/` |
| "backslash" | `\` |
| "underscore" | `_` |
| "pipe" | `\|` |
| "dollar sign" | `$` |

### Programming
| Say This | You Get |
|----------|---------|
| "less than" / "open angle" | `<` |
| "greater than" / "close angle" | `>` |

### Common Replacements
| Say This | You Get |
|----------|---------|
| "dot com" | `.com` |
| "dot net" | `.net` |
| "dot org" | `.org` |
| "dot io" | `.io` |
| "dot ai" | `.ai` |

## 🔢 Text Processing Features

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

### Smart Quotes
Converts straight quotes to curly quotes automatically:
- `"` → `"` (opening)
- `"` → `"` (closing)

### Capitalize Sentences
Auto-capitalizes first letter of sentences:
- "hello world. this is a test." → "Hello world. This is a test."

### Granular Punctuation Controls
Toggle each punctuation type independently:
- Periods
- Commas
- Question marks
- Exclamation marks
- Colons
- Semicolons
- Quotes

### Emoji Support
Speak emoji names to insert actual emojis:

| Say This | Get This |
|----------|----------|
| "happy emoji" | 😊 |
| "fire emoji" | 🔥 |
| "thumbs up emoji" | 👍 |
| "rocket emoji" | 🚀 |

**100+ emojis supported!**

## 📋 Version Comparison

| Feature | Full | Lite |
|---------|------|------|
| System Tray | ✅ | ❌ |
| Emoji Support | ✅ | ❌ |
| Voice Commands | ✅ 60+ | ❌ |
| History | ✅ | ❌ |
| Statistics | ✅ | ❌ |
| Themes | ✅ | ❌ |
| Audio Level | ✅ | ❌ |
| Transcription Speed | ~0.5s | ~0.3s |
| Model | large-v3-turbo | distil-whisper |
| Memory Usage | ~150MB | ~80MB |

**Recommendation:** Use Full version unless you have a very old/slow computer.

## 🛠️ Building from Source

### Windows
```bash
pip install pyinstaller
pyinstaller VoiceType.spec --noconfirm
```

Output: `dist/VoiceType.exe`

### Lite Version
```bash
pyinstaller VoiceTypeLite.spec --noconfirm
```

Output: `dist/VoiceTypeLite.exe`

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "No API key" error | Get free key from [console.groq.com](https://console.groq.com/keys) |
| Microphone not detected | Check system permissions, restart app |
| Transcription is empty | Speak louder, check mic in settings |
| "Rate limited" error | Wait a moment, will auto-retry |
| Network errors | Check internet connection |
| Widget not appearing | Check always-on-top setting, restart app |
| Text not pasting in Quicken | Enable Quicken Mode in settings |
| Wrong language detected | Set language in settings instead of auto-detect |

## 📊 Feature Statistics

| Category | Count |
|----------|-------|
| Total Features | 50+ |
| Voice Commands | 60+ |
| Emoji Commands | 100+ |
| Settings Options | 20+ |
| Languages Supported | 15+ |
| Quick Snippets | 10 |

## 🌍 Language Support

VoiceType supports 15+ languages with auto-detection:

| Code | Language |
|------|----------|
| auto | Auto-detect |
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| it | Italian |
| pt | Portuguese |
| ru | Russian |
| ja | Japanese |
| ko | Korean |
| zh | Chinese |
| ar | Arabic |
| hi | Hindi |
| nl | Dutch |
| pl | Polish |
| tr | Turkish |

**Note:** Accounting Mode works best with English.

## 🔒 Security & Privacy

- API keys stored locally in `~/.voice-type-config.json`
- Audio processed in real-time, not saved to disk (unless enabled)
- No data sent anywhere except Groq API
- History stored locally (if enabled)
- Recordings saved locally (if enabled)

## 📄 Requirements

- **OS:** Windows 10/11
- **Python:** 3.8+ (for source)
- **Hardware:** Microphone
- **Network:** Internet connection
- **API:** Groq API key (free tier available)

## 🎯 Use Cases

- **Email Composition** - Dictate emails 3x faster than typing
- **Code Documentation** - Write comments and docs by voice
- **Chat & Messaging** - Quick responses in Discord, Slack, etc.
- **Content Creation** - Draft blog posts, articles, scripts
- **Data Entry** - Fill forms and spreadsheets by voice
- **Accessibility** - Alternative to typing for mobility issues
- **Meeting Notes** - Dictate notes during or after meetings
- **Creative Writing** - Get ideas down quickly

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v2.3.0** | Mar 2026 | 50+ features, voice commands, themes, history, vocabulary, audio |
| **v2.0.0** | Feb 2026 | Voice macros, statistics, compact mode, themes, custom vocabulary |
| **v1.2.0** | Feb 2026 | Accounting mode, casual mode, filter words, Lite version |
| **v1.1.0** | Feb 2026 | Emoji support, custom hotkeys |
| **v1.0.0** | Feb 2026 | Initial release |

See [ROADMAP.md](ROADMAP.md) for detailed feature planning.

## 📜 License

MIT License - use freely!

## 🤝 Credits

- **Original Creator:** [@boring877](https://github.com/boring877)
- **Maintainer:** [@TheD0SH](https://github.com/TheD0SH)
- **Powered By:** [Groq](https://groq.com/) Whisper API

---

<div align="center">

**Made with ❤️ for productivity**

**[Download Now](https://github.com/TheD0SH/ai-speech-to-text/releases)** | **[Documentation](ROADMAP.md)** | **[Report Bug](https://github.com/TheD0SH/ai-speech-to-text/issues)** | **[Request Feature](https://github.com/TheD0SH/ai-speech-to-text/issues)**

**Website:** [voice-type-site.vercel.app](https://voice-type-site.vercel.app/)

</div>

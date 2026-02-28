# AI Speech-to-Text - Quality of Life Improvements

## Improvements Plan

### PR 1: Add .env Support & Config Validation
- Support `.env` file for API key
- Validate API key format
- Add example.env file

### PR 2: Add Audio Level Indicator
- Visual feedback while recording
- Shows microphone is working
- Helps debug audio issues

### PR 3: Add Test Microphone Button
- Records 3 seconds and plays back
- Verifies microphone is working
- No transcription needed

### PR 4: Add Retry Logic for Failed Transcriptions
- Auto-retry up to 3 times on network errors
- Exponential backoff
- Show retry count to user

### PR 5: Add Sound Feedback
- Optional beep on start/stop recording
- Uses system sounds (cross-platform)
- Can be disabled in settings

### PR 6: Add Transcription History
- Keep last 50 transcriptions
- Viewable in settings
- Copy to clipboard button
- Clear history option

### PR 7: Improve Error Messages
- Specific error for invalid API key
- Network error detection
- Microphone permission errors
- Clear actionable messages

### PR 8: Add Keyboard Shortcut Info
- Show current hotkey in widget
- Update README with all shortcuts
- Add keyboard shortcut to open settings

---

_This document tracks all improvements being made_

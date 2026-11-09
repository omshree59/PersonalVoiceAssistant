# Desktop Cat Voice Listener

A Windows desktop assistant built around a transparent animated cat. Click the cat, speak once, and it either does the task quietly or answers you like a person.

It does not sit in a window frame. The cat rests on the desktop, stays above other windows, and remembers where you leave it.

## What it does

Each click starts one listen. The microphone stays open until you pause (about 1.2 seconds of silence) or until 9 seconds pass. Speech is transcribed, then handled in one of two ways:

- **Actions stay quiet.** "Open YouTube", "volume up", and "open Chrome" run immediately. The cat flashes success and does not read the command back.
- **Greetings get a reply.** "Hi", "hello", "hey", "good morning", "thanks", and "bye" show a text bubble and are spoken aloud. "Hi" and "hello" both come back as "Hi, how can I help you?"

You can also chain steps in one sentence: "open Chrome and then click my profile". Steps run in order, with a short pause between them.

Click the cat again while it is listening to cancel.

## Quick start

Windows 10 or later, Python 3.10+, a working microphone, and an internet connection for speech recognition.

```bash
pip install SpeechRecognition sounddevice numpy Pillow pyautogui pywin32
python app.py
```

Other ways to start it:

| How | What you get |
| --- | --- |
| `run_listener.bat` | Same as `python app.py`, with the console left open so logs stay visible |
| `run_silent.vbs` | No console. Uses `pythonw.exe` |
| `python create_desktop_shortcut.py` | A **Voice Listener** shortcut on your desktop that launches the silent script |

`settings.json` is created on first use and is not part of the repo. It stores the cat's position, audio tuning, and Chrome path.

## Using the cat

- **Click** to listen or to stop a listen already in progress.
- **Drag** to move it. The new spot is saved.
- **Right-click** for Start Listening, the voice-command guide, detected Chrome profiles, Always on Top, and Exit.

While it works, the cat changes pose:

| State | What you see |
| --- | --- |
| Idle | Sitting, a slow breathing motion, and an occasional blink |
| Listening | A hop, perked ears, and sound-wave arcs. Louder speech makes the hop bigger |
| Processing | Both ears up, with thinking dots |
| Success | A happy face, blush, a bounce, and music notes |

A small toast appears beside the cat for greetings, unclear audio, and failures. Successful actions do not toast the command text.

## Commands

Phrases are matched loosely. "Open", "launch", "start", and "go to" all work for the same targets.

### Assistant (spoken, and shown as text)

| You say | It answers |
| --- | --- |
| hi, hii, hello, hey, hey there, yo | Hi, how can I help you? |
| good morning / afternoon / evening | The same greeting, then "How can I help you?" |
| good night | Good night. I'll be here when you need me. |
| how are you, what's up | I'm good. How can I help you? |
| thanks, thank you | Anytime. What else can I do? |
| bye, goodbye, see you | Bye. I'll be right here. |
| help, who are you, what can you do | A one-line reminder of what to try |

"Hi, open YouTube" still says hello, then opens YouTube without narrating the action.

### YouTube

- "open youtube" opens [YouTube](https://www.youtube.com) in a Chrome app window (no tab strip) when `youtube_app_mode` is on.
- "search lofi hip hop on youtube", "play lofi on youtube", or "youtube search lofi" opens that search.

If Chrome is missing, it falls back to the default browser.

### Chrome profiles

Profiles come from Chrome's local `Local State` file, not from a hardcoded list. Right-click the cat and choose **Chrome Profiles** to see the directories it found.

| You say | What it launches |
| --- | --- |
| open chrome | The Default profile |
| open my profile, click my profile, open omshree | The personal profile (matched on name, Gmail, or the Default directory) |
| open vit profile, open college profile | The VIT / student profile, when that domain or name is installed |
| open iit profile, open scale profile | The IIT Ropar Scale profile, when that domain or name is installed |
| open chrome and then click my profile | Chrome, then that profile, as two steps |

Any other installed profile can be named directly if the spoken name matches the profile name Chrome has stored.

### Sites

"Open …", "launch …", or "go to …" any of these:

GitHub, Google, ChatGPT, Reddit, Gmail, Netflix, Spotify, Twitter / X, Instagram, WhatsApp, LinkedIn, Twitch, Amazon.

### Search

- "search pasta on google" or "google how to cook pasta"
- "what is", "who is", and "how to …" also open a Google search

### Windows

| You say | Result |
| --- | --- |
| open calculator, notepad, paint, cmd, powershell, terminal, file explorer, task manager, settings, camera, snipping tool | Starts that app. Unknown names are passed to `start` |
| volume up / volume down | A few steps on the volume keys |
| mute / unmute | Toggles mute |
| take screenshot, snip | Win+Shift+S (Snipping Tool overlay) |
| show desktop, minimize all, go to desktop | Win+D |

## How a phrase is handled

```
click  →  record until silence  →  Google speech-to-text
                                         │
                         greeting?  ─────┴─────  command?
                         speak + bubble          run it, stay quiet
```

1. `audio/recorder.py` captures 16 kHz mono audio with `sounddevice` and stops on silence.
2. `audio/recognizer.py` sends it to the Google Web Speech API (`en-US`). No API key. If the network request fails, it tries Vosk when that package is installed.
3. `automation/command_parser.py` decides whether the line is small talk or a command, including chains split on "and then", "then", or "and" before a verb such as open, click, or search.
4. `automation/actions.py` launches Chrome, sites, and Windows apps, and sends volume and desktop hotkeys with PyAutoGUI.
5. `feedback/tts.py` speaks only assistant replies, through the Windows SAPI voice. Listen and error cues are short beeps.

## Settings

Edit `settings.json` in the project folder after the app has run once. Defaults live in `config.py`.

| Key | Default | Meaning |
| --- | --- | --- |
| `silence_threshold` | `0.015` | How loud audio must be to count as speech |
| `silence_duration_seconds` | `1.2` | Pause that ends the recording |
| `max_listen_seconds` | `9.0` | Hard cap on one listen |
| `sample_rate` | `16000` | Microphone sample rate |
| `speech_engine` | `"hybrid"` | Stored preference. Recognition uses Google, then Vosk if the request fails |
| `tts_enabled` | `true` | Speak greeting replies |
| `sound_cues` | `true` | Beeps when listening starts, or when something fails |
| `youtube_app_mode` | `true` | Open YouTube as a standalone Chrome window |
| `chrome_path` | auto | Full path to `chrome.exe`. Filled in automatically when empty |
| `always_on_top` | `true` | Keep the cat above other windows. Also toggled from the right-click menu |
| `widget_size` | `70` | Cat size in pixels |
| `window_x`, `window_y` | remembered | Last dragged position |

## Project layout

```
app.py                      listen loop and when to speak
run_listener.bat            start with a console
run_silent.vbs              start without a console
create_desktop_shortcut.py  desktop shortcut
config.py                   defaults and settings.json
audio/                      microphone and speech-to-text
automation/                 command matching, Chrome profiles, actions
feedback/tts.py             spoken replies and beeps
gui/                        cat window and toast bubble
assets/                     cat sprites and icon
```

Sprite helpers in `assets/` (`generate_assets.py`, `generate_cat_sprites.py`, `extract_perfect_cat.py`) are only needed if you redraw the cat. They need Pillow and OpenCV. The listener itself does not.

## Offline speech

Google transcription needs the network. For the fallback path:

```bash
pip install vosk
```

Vosk also needs a model on the path `speech_recognition` expects. If neither engine returns text, the cat shows "Could not understand audio" and does not guess a command.

## Limits

- One click, one utterance. There is no wake word and it does not keep listening after a command.
- Recognition language is English (`en-US`).
- Profile aliases for "my profile", VIT, and IIT are matched against the Chrome profiles installed on this PC. Another machine only hits those aliases when a profile name, email, or hosted domain lines up.
- PyAutoGUI drives volume, screenshot, and show-desktop by sending real keystrokes, so those shortcuts behave like you pressed the keys yourself.

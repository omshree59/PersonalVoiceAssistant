# 🐱 Desktop Cat Voice Listener

A personal, lightweight voice assistant for Windows featuring a custom animated cat companion sitting right on your desktop with **no background box or frame**. 

Whenever you click the cat, it **perks its ears up, twitches, and jumps happily** with glowing acoustic ripples while listening to your commands!

---

## ✨ Cat Animations & Features

- **No Background At All**:
  - The cat character sits directly on your desktop screen with smooth transparency. No rectangle borders or boxes.
- **Interactive Jumping & Ear Listening Animations**:
  - 🔵 **Idle State**: The cat sits peacefully on your desktop, with subtle breathing rhythm and natural eye-blinking every few seconds.
  - 🔴 **Listening State (When speaking / hearing)**:
    - **Jumping**: The cat hops up and down in a lively bounce with realistic squash-and-stretch physics. When voice audio is detected, it jumps even higher and more enthusiastically!
    - **Ear Listening**: The cat's ears perk up and twitch in response to speech.
    - **Acoustic Ear Ripples**: Animated glowing sound-wave ripples (`) )` and `( (`) emit outward from the cat's ear tips while it listens!
  - 🟡 **Processing State**: The cat stays alert with both ears perked up and small glowing thinking sparkles rotating above its head.
  - 🟢 **Success State**: The cat celebrates with happy arched eyes `^_^`, blush on its cheeks, a cheerful bounce, and rising music notes!
- **Fully Draggable**:
  - Click and drag the cat anywhere on your screen. It automatically saves your preferred desktop position.

---

## 🗣️ Voice Commands Supported

### 1. YouTube
- **`"open youtube"`** / **`"launch youtube"`**
  - Opens YouTube in standalone app mode (clean desktop window without browser tabs).
- **`"search lofi hip hop on youtube"`**
  - Directly opens YouTube search results.

### 2. Google Chrome & Profiles
- **`"open chrome and then click my profile"`** / **`"open chrome and click my profile"`**
  - Chains the command: opens Google Chrome and switches directly into your personal profile (**OMSHREE**).
- **`"click my profile"`** / **`"open my profile"`**
  - Switches to your personal profile.
- **`"open vit profile"`** / **`"open college profile"`**
  - Launches Chrome with your `vitapstudent.ac.in` student profile.
- **`"open iit profile"`** / **`"open scale profile"`**
  - Launches Chrome with your `scale.iitrpr.ac.in` profile.

### 3. Desktop Apps & Searches
- **`"open calculator"`**, **`"open notepad"`**, **`"open cmd"`**, **`"open task manager"`**, **`"open settings"`**
- **`"open github"`**, **`"open chatgpt"`**, **`"open reddit"`**, **`"open spotify"`**
- **`"search [query] on google"`**

### 4. System Controls
- **`"volume up"`**, **`"volume down"`**, **`"mute"`**
- **`"take screenshot"`** (opens snipping tool)
- **`"show desktop"`** / **`"minimize all"`**

---

## 🚀 How to Launch

1. **Desktop Shortcut**:
   - Double-click the **`Voice Listener`** shortcut on your Windows desktop (`C:\Users\User\Desktop\Voice Listener.lnk`).
2. **Terminal with Logs**:
   - Double-click `run_listener.bat` or run:
     ```bash
     python app.py
     ```
3. **Silent Background**:
   - Double-click `run_silent.vbs`.

# scrolly

A Python program that uses your webcam to control a web browser with hand gestures. You can scroll up and down, stop scrolling, and switch tabs without touching the keyboard or mouse.

## How it works

1. **MediaPipe Hands** finds 21 landmark points on your hand in each webcam frame.
2. The program checks which fingers are extended (a finger counts as "up" when its tip is farther from the wrist than its middle joint).
3. The pattern of raised fingers is matched to a gesture.
4. **PyAutoGUI** sends the matching scroll or keyboard action to the active window.

A gesture must be held steady for a few frames before it counts, which prevents accidental triggers.

## Gestures

Show one hand to the webcam with your palm facing the camera.

| Gesture | Action |
|---|---|
| Index finger only | Start scrolling up (continues until stopped) |
| Index + middle finger (peace sign) | Start scrolling down (continues until stopped) |
| Open palm (all 5 fingers) | Stop scrolling |
| Index + middle + ring finger | Next tab (Ctrl+Tab) |
| Thumb + pinky ("hang loose") | Previous tab (Ctrl+Shift+Tab) |
| Fist or anything else | No action |

## Requirements

- macOS (Intel or Apple Silicon)
- Python 3.9 to 3.12 (MediaPipe does not install on newer versions such as 3.13+)
- A webcam

## Setup

```bash
cd path/to/project-folder
python3.12 -m venv gestures
source gestures/bin/activate
python -m pip install --upgrade pip
python -m pip install opencv-python mediapipe pyautogui
```

Check that the environment uses the right version:

```bash
python --version
```

It should print `Python 3.12.x`.

If MediaPipe fails to install on an Intel Mac, try an older release:

```bash
python -m pip install "mediapipe==0.10.14"
```

## macOS permissions

Go to **System Settings > Privacy & Security** and enable your terminal app (Terminal, iTerm, or VS Code) under:

- **Camera**
- **Accessibility**

Quit and reopen the terminal afterward.

## Run

```bash
source gestures/bin/activate
python gesture_control.py
```

Click on your browser window so it is the active window, then show your gestures to the camera.

Press `q` in the webcam window to quit, or `Ctrl+C` in the terminal.

**Emergency stop:** move your mouse into a

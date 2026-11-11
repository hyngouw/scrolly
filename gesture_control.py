"""
Hand-gesture browser control
----------------------------
Gestures (show ONE hand to the webcam, palm facing the camera):

  Index finger only ............ start scrolling UP   (keeps going)
  Index + middle (peace sign) .. start scrolling DOWN (keeps going)
  Open palm (all 5 fingers) .... STOP scrolling
  Three fingers (index+middle+ring) .. NEXT tab      (Ctrl+Tab)
  Thumb + pinky ("hang loose") . PREVIOUS tab        (Ctrl+Shift+Tab)
  Fist / anything else ......... do nothing

Press 'q' in the preview window to quit.
Emergency stop: slam your mouse into a screen corner (PyAutoGUI failsafe).

Install:  pip install mediapipe opencv-python pyautogui
"""

import math
import time
from collections import deque

import cv2
import mediapipe as mp
import pyautogui

# ---------------- Settings you can tweak ----------------
SCROLL_AMOUNT = 1        # per frame; lower on macOS (try 5-10)
STABLE_FRAMES = 3         # gesture must be held this many frames to count
TAB_COOLDOWN = 1.0        # seconds between tab switches
CAMERA_INDEX = 0
# --------------------------------------------------------

pyautogui.PAUSE = 0       # no built-in delay after each action
pyautogui.FAILSAFE = True

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# (tip landmark, middle-joint landmark) for each non-thumb finger
FINGERS = {
    "index": (8, 6),
    "middle": (12, 10),
    "ring": (16, 14),
    "pinky": (20, 18),
}


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def fingers_extended(lm):
    """Return the set of finger names that are held out straight.

    A finger counts as 'up' when its tip is farther from the wrist than its
    middle joint. This works no matter how the hand is rotated.
    """
    wrist = lm[0]
    up = set()
    for name, (tip, joint) in FINGERS.items():
        if dist(wrist, lm[tip]) > dist(wrist, lm[joint]) * 1.05:
            up.add(name)
    # Thumb: tip is farther from the base of the pinky than the thumb's
    # upper joint is, when the thumb is stuck out.
    if dist(lm[4], lm[17]) > dist(lm[3], lm[17]) * 1.05:
        up.add("thumb")
    return up


def classify(up):
    if up == {"index"}:
        return "scroll_up"
    if up == {"index", "middle"}:
        return "scroll_down"
    if up == {"thumb", "index", "middle", "ring", "pinky"}:
        return "stop"
    if up == {"index", "middle", "ring"}:
        return "next_tab"
    if up == {"thumb", "pinky"}:
        return "prev_tab"
    return None


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    history = deque(maxlen=STABLE_FRAMES)
    scroll_mode = None          # None, "up", or "down"
    last_gesture = None         # last confirmed gesture (so tabs fire once)
    last_tab_time = 0.0

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6,
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # mirror so it feels natural
            result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            raw = None
            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                raw = classify(fingers_extended(hand.landmark))

            # Only accept a gesture once it's been steady for N frames
            history.append(raw)
            confirmed = (
                history[0]
                if len(history) == STABLE_FRAMES and len(set(history)) == 1
                else last_gesture
            )

            # A gesture "fires" when it changes to something new
            if confirmed != last_gesture:
                now = time.time()
                if confirmed == "scroll_up":
                    scroll_mode = "up"
                elif confirmed == "scroll_down":
                    scroll_mode = "down"
                elif confirmed == "stop":
                    scroll_mode = None
                elif confirmed == "next_tab" and now - last_tab_time > TAB_COOLDOWN:
                    pyautogui.hotkey("ctrl", "tab")
                    last_tab_time = now
                elif confirmed == "prev_tab" and now - last_tab_time > TAB_COOLDOWN:
                    pyautogui.hotkey("ctrl", "shift", "tab")
                    last_tab_time = now
                last_gesture = confirmed

            # Keep scrolling every frame until "stop" is shown
            if scroll_mode == "up":
                pyautogui.scroll(SCROLL_AMOUNT)
            elif scroll_mode == "down":
                pyautogui.scroll(-SCROLL_AMOUNT)

            # On-screen status
            cv2.putText(frame, f"Gesture: {raw}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Scrolling: {scroll_mode}", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
            cv2.imshow("Gesture Control (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

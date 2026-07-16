# main.py
import time
import sys
import os
from datetime import datetime
import pyautogui
import re  # for sanitising filenames

# Import functions from utils
from utils import (
    get_current_left_month_from_region,
    calculate_month_clicks,
    find_number_in_region,
    capture_full_screen,
    wait_and_click,
    type_text_and_enter
)

# Import all configuration variables from config
from config import (
    WAIT_INITIAL,
    WAIT_AFTER_ENTER1,
    WAIT_AFTER_CLICK2,
    WAIT_AFTER_CLICK4,
    WAIT_AFTER_CLICK5,
    WAIT_AFTER_SNAPSHOT,
    WAIT_AFTER_NAVIGATION,
    WAIT_AFTER_DAY_CLICK,
    TARGET_DATE,
    TEXT1,
    TEXT2,
    TEXT3,
    TYPING_WPM,
    CLICK_1,
    CLICK_2,
    CLICK_3,
    CLICK_4,
    CLICK_5,
    CLICK_6,
    CALENDAR_SNAPSHOT_REGION,
    DAY_GRID_REGION,
    FORWARD_BUTTON,
    BACKWARD_BUTTON,
    IMAGE_NAME_PREFIX   # we'll keep this but we'll not use SAVE_FOLDER anymore
)

# Safety: move mouse to top‑left corner to abort
pyautogui.FAILSAFE = True

def sanitize_filename(text):
    """Replace spaces with underscores and remove any non‑alphanumeric characters."""
    # Replace spaces and keep only letters, digits, underscores, dashes
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', text)
    # Collapse multiple underscores
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_')

def main():
    print("🚀 Starting automation...")
    print(f"⏳ Waiting {WAIT_INITIAL} seconds for you to open the website...")
    time.sleep(WAIT_INITIAL)

    # Step 1
    wait_and_click(CLICK_1)
    type_text_and_enter(TEXT1, pause=WAIT_AFTER_ENTER1, wpm=TYPING_WPM)

    # Step 2
    wait_and_click(CLICK_2)
    type_text_and_enter(TEXT2, pause=WAIT_AFTER_CLICK2, wpm=TYPING_WPM)

    # Step 3
    wait_and_click(CLICK_3)

    # Step 4
    wait_and_click(CLICK_4)
    type_text_and_enter(TEXT3, pause=WAIT_AFTER_CLICK4, wpm=TYPING_WPM)

    # Step 5
    wait_and_click(CLICK_5, pause=WAIT_AFTER_CLICK5)

    # Step 6: Month detection (VLM + OCR fallback)
    print("📸 Taking first calendar snapshot...")
    try:
        current_month_text = get_current_left_month_from_region(CALENDAR_SNAPSHOT_REGION)
        print(f"   Detected left panel: {current_month_text}")
    except Exception as e:
        print(f"❌ Failed to read calendar: {e}")
        sys.exit(1)

    diff = calculate_month_clicks(current_month_text, TARGET_DATE)
    print(f"   Need {abs(diff)} clicks {'forward' if diff > 0 else 'backward'} to reach {TARGET_DATE}")

    if diff > 0:
        button = FORWARD_BUTTON
        for _ in range(abs(diff)):
            wait_and_click(button, pause=0.2)
    elif diff < 0:
        button = BACKWARD_BUTTON
        for _ in range(abs(diff)):
            wait_and_click(button, pause=0.2)
    else:
        print("   Already on the correct month.")

    print(f"⏳ Waiting {WAIT_AFTER_NAVIGATION} seconds for calendar to settle...")
    time.sleep(WAIT_AFTER_NAVIGATION)

    # Step 7: Find and click day number using OCR
    target_day = datetime.strptime(TARGET_DATE, "%Y-%m-%d").day
    print(f"🔍 Looking for day {target_day} in the day grid...")
    try:
        day_x, day_y = find_number_in_region(DAY_GRID_REGION, target_day)
        print(f"   Found at absolute coordinates: ({day_x}, {day_y})")
    except Exception as e:
        print(f"❌ Failed to locate day {target_day}: {e}")
        sys.exit(1)

    pyautogui.moveTo(day_x, day_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1)

    # Step 8: Final click
    wait_and_click(CLICK_6, pause=WAIT_AFTER_DAY_CLICK)

    # ----- FINAL SCREENSHOT (with new naming and location) -----
    print(f"⏳ Waiting {WAIT_AFTER_SNAPSHOT} seconds before taking final screenshot...")
    time.sleep(WAIT_AFTER_SNAPSHOT)

    # Sanitise texts for filename
    clean_text2 = sanitize_filename(TEXT2)
    clean_text3 = sanitize_filename(TEXT3)
    # Target date (already in YYYY-MM-DD)
    target_date_str = TARGET_DATE  # "2027-12-25"
    # Current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # e.g., 2026-07-16_14-30-45

    # Build filename: MMT_<text2>_<text3>_<target_date>_<timestamp>.png
    # If text2 or text3 are empty, skip them
    parts = ["MMT"]
    if clean_text2:
        parts.append(clean_text2)
    if clean_text3:
        parts.append(clean_text3)
    parts.append(target_date_str)
    parts.append(timestamp)
    filename = "_".join(parts) + ".png"

    # Save inside the current script's directory (demoagent5)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(script_dir, filename)

    # Use the existing capture function (from utils)
    from utils import capture_full_screen
    capture_full_screen(save_path)

    print("✅ Automation complete!")

if __name__ == "__main__":
    main()
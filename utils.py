# utils.py
import os
import sys
import subprocess
import pyautogui
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import time
import re
import base64
import requests
import json
from datetime import datetime
from config import (
    TESSERACT_CMD,
    CALENDAR_SNAPSHOT_REGION,
    DAY_GRID_REGION,
    NVIDIA_API_KEY,
    NVIDIA_MODEL
)

# ---------- 1. TESSERACT SETUP ----------
def _find_tesseract():
    if TESSERACT_CMD and os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        return TESSERACT_CMD
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\Atharva Karanjkar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    ]
    for path in common_paths:
        if os.path.exists(path):
            print(f"Found Tesseract at: {path}")
            pytesseract.pytesseract.tesseract_cmd = path
            return path
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                pytesseract.pytesseract.tesseract_cmd = path
                return path
        else:
            result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                pytesseract.pytesseract.tesseract_cmd = path
                return path
    except:
        pass
    return None

if not _find_tesseract():
    print("⚠️ Tesseract not found. Install from https://github.com/UB-Mannheim/tesseract/wiki")
    sys.exit(1)

try:
    print(f"✅ Tesseract version: {pytesseract.get_tesseract_version()}")
except:
    pass

# ---------- 2. MONTH NAME MAPPING ----------
MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def parse_month_year(text):
    """Extract month and year from a string like 'February 2027'."""
    text = text.strip().replace(",", " ").replace(".", "")
    match = re.search(r"([A-Za-z]+)\s*[,]?\s*(\d{4})", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse month/year from: '{text}'")
    month_name, year_str = match.groups()
    month_num = MONTHS.get(month_name.lower())
    if month_num is None:
        raise ValueError(f"Unknown month: '{month_name}'")
    return month_num, int(year_str)

# ---------- 3. VISION LLM FOR MONTH DETECTION ----------
def get_current_left_month_vision(region):
    """Use NVIDIA Vision LLM to read month and year from left panel."""
    x1, y1, x2, y2 = region
    width = x2 - x1
    height = y2 - y1
    img = pyautogui.screenshot(region=(x1, y1, width, height))
    img.save("debug_calendar_vision.png")
    print("   📷 Saved debug_calendar_vision.png for inspection")

    import io
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    b64_image = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Look at the calendar in the image. Identify the month and year displayed on the LEFT panel. "
        "Return your answer strictly in this format: 'Month Year' (e.g., 'February 2027'). "
        "Do not include any extra text, explanations, or punctuation."
    )
    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        "max_tokens": 20,
        "temperature": 0.0
    }

    print("   🧠 Calling NVIDIA Vision LLM for month detection...")
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    result = resp.json()['choices'][0]['message']['content'].strip()
    print(f"   ✅ Vision LLM responded: {result}")
    return result

# ---------- 4. OCR FALLBACK FOR MONTH ----------
def get_current_left_month_ocr(region):
    """Fallback OCR to read month/year."""
    print("   🔍 Falling back to OCR for month detection...")
    left, top, width, height = region
    img = pyautogui.screenshot(region=region)
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)
    img = img.filter(ImageFilter.SHARPEN)
    img.save("debug_calendar_ocr.png")

    custom_config = r'--psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789,."'
    text = pytesseract.image_to_string(img, config=custom_config)
    lines = text.splitlines()
    months_regex = "|".join(["January", "February", "March", "April", "May", "June",
                             "July", "August", "September", "October", "November", "December"])
    for line in lines:
        if re.search(rf"({months_regex})\s*[,]?\s*\d{{4}}", line, re.IGNORECASE):
            return line.strip()

    top_crop = img.crop((0, 0, img.width, int(img.height * 0.3)))
    text = pytesseract.image_to_string(top_crop, config=custom_config)
    for line in text.splitlines():
        if re.search(rf"({months_regex})\s*[,]?\s*\d{{4}}", line, re.IGNORECASE):
            return line.strip()

    raise ValueError("No month/year found by OCR.")

# ---------- 5. MASTER MONTH DETECTION ----------
def get_current_left_month_from_region(region):
    try:
        return get_current_left_month_vision(region)
    except Exception as e:
        print(f"   ⚠️ Vision LLM failed: {e}")
        return get_current_left_month_ocr(region)

# ---------- 6. CLICK CALCULATION ----------
def calculate_month_clicks(current_text, target_date_str):
    cur_month, cur_year = parse_month_year(current_text)
    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    tgt_year, tgt_month = target.year, target.month
    diff_months = (tgt_year - cur_year) * 12 + (tgt_month - cur_month)
    return diff_months

# ---------- 7. DAY GRID OCR – Using your WORKING character‑level approach ----------
from collections import Counter  # add this at the top if not already there

# ============================================================
#  ROBUST DAY FINDER – OCR + grid inference
# ============================================================

def find_number_in_region(region, target_number):
    """
    Locate a day number (1-31) inside a calendar-grid screen region.
    Two‑layer approach: word‑level OCR + grid inference fallback.
    Works with or without price text, any colour, any font.
    """
    x1, y1, x2, y2 = region
    width = x2 - x1
    height = y2 - y1

    # Capture the region (exact same as before)
    img = pyautogui.screenshot(region=(x1, y1, width, height))
    img.save("debug_day_grid.png")
    print("   💾 Saved debug_day_grid.png for inspection")

    # Delegate to the core logic
    return _find_day_in_image(img, target_number, region_origin=(x1, y1))


def _find_day_in_image(img, target_number, region_origin=(0, 0)):
    """
    Core logic – works with a PIL image and returns absolute coordinates.
    """
    ox, oy = region_origin

    # ── 1. WORD‑LEVEL OCR (no digit whitelist, so prices with commas are ignored) ──
    data = pytesseract.image_to_data(
        img, config='--psm 6', output_type=pytesseract.Output.DICT
    )

    detected = {}   # { day_number: (cx, cy, height) }
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        try:
            conf = int(data['conf'][i])
        except:
            conf = -1
        if conf < 5 or not text:
            continue
        # Only pure‑digit strings that are valid day numbers (1‑31)
        if text.isdigit() and 1 <= int(text) <= 31:
            cx = data['left'][i] + data['width'][i] // 2
            cy = data['top'][i] + data['height'][i] // 2
            h  = data['height'][i]
            num = int(text)
            # If duplicate, keep the one further down the page (grid > header)
            if num not in detected or cy > detected[num][1]:
                detected[num] = (cx, cy, h)

    print(f"   🔢 OCR detected days: {sorted(detected.keys())} "
          f"({len(detected)}/30-31)")

    # ── 2. GRID INFERENCE (fills in missing days) ────────────────
    if len(detected) >= 5:
        grid_positions = _build_grid(detected)

        # Fill missing days from the grid
        all_days = set(detected.keys()) | set(grid_positions.keys())
        for day in sorted(all_days):
            if day not in detected and day in grid_positions:
                detected[day] = (*grid_positions[day], 0)

        if target_number not in detected and target_number in grid_positions:
            detected[target_number] = (*grid_positions[target_number], 0)
            print(f"   📐 Day {target_number} position computed from grid")

    print(f"   ✅ Final day set: {sorted(d for d in detected if 1 <= d <= 31)}")

    if target_number not in detected:
        raise ValueError(
            f"Day {target_number} not found. "
            f"Detected: {sorted(detected.keys())}"
        )

    rel_x, rel_y, _ = detected[target_number]
    abs_x = ox + rel_x
    abs_y = oy + rel_y
    print(f"   📍 Day {target_number} at absolute ({abs_x}, {abs_y})")
    return abs_x, abs_y


def _build_grid(detected):
    """
    From the detected day→(cx, cy, h) mapping, compute the full
    7-column calendar grid and return positions for ALL 31 possible days.
    """
    # Cluster x‑coordinates into 7 columns
    x_vals = sorted(set(v[0] for v in detected.values()))
    col_clusters = _cluster_values(x_vals, tolerance=25)
    if len(col_clusters) < 3:
        return {}
    col_centers = [int(sum(c) / len(c)) for c in col_clusters]
    col_centers.sort()

    # If fewer than 7 columns, extrapolate the missing ones
    if len(col_centers) >= 2:
        spacing = _median_spacing(col_centers)
        col_centers = _fill_columns(col_centers, spacing, target=7)

    # Cluster y‑coordinates into rows
    y_vals = sorted(set(v[1] for v in detected.values()))
    row_clusters = _cluster_values(y_vals, tolerance=20)
    row_centers = sorted(int(sum(r) / len(r)) for r in row_clusters)

    if len(row_centers) >= 2:
        spacing = _median_spacing(row_centers)
        # Extend downward if needed (month may have 5 or 6 rows)
        while len(row_centers) < 6:
            next_y = row_centers[-1] + spacing
            row_centers.append(next_y)

    # Determine start column (where day‑1 sits) using majority vote
    votes = []
    for day, (cx, cy, h) in detected.items():
        col_idx = _nearest_index(cx, col_centers)
        sc = (col_idx - (day - 1) % 7 + 7) % 7
        votes.append(sc)

    if not votes:
        return {}

    start_col = Counter(votes).most_common(1)[0][0]

    # Build the complete grid
    grid = {}
    for day in range(1, 32):
        col_idx = (start_col + day - 1) % 7
        row_idx = (start_col + day - 1) // 7
        if col_idx < len(col_centers) and row_idx < len(row_centers):
            grid[day] = (col_centers[col_idx], row_centers[row_idx])

    return grid


def _cluster_values(values, tolerance):
    """Group sorted values that are within `tolerance` of each other."""
    if not values:
        return []
    clusters = [[values[0]]]
    for v in values[1:]:
        if v - clusters[-1][-1] <= tolerance:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return clusters


def _median_spacing(centers):
    """Median gap between consecutive sorted centers."""
    gaps = [centers[i+1] - centers[i] for i in range(len(centers) - 1)]
    gaps.sort()
    return gaps[len(gaps) // 2]


def _fill_columns(centers, spacing, target=7):
    """Extend column centers to exactly `target` columns."""
    centers = sorted(centers)
    # Fill left
    while len(centers) < target and centers[0] - spacing > 0:
        centers.insert(0, centers[0] - spacing)
    # Fill right
    while len(centers) < target:
        centers.append(centers[-1] + spacing)
    # Trim to target (take the most central)
    if len(centers) > target:
        mid = len(centers) // 2
        start = mid - target // 2
        centers = centers[start:start+target]
    return centers


def _nearest_index(value, centers):
    """Return the index of the closest center."""
    return min(range(len(centers)), key=lambda i: abs(centers[i] - value))
# ---------- 8. MOUSE & KEYBOARD ACTIONS ----------
def wait_and_click(coord, pause=0.5, smooth=True):
    if smooth:
        pyautogui.moveTo(coord[0], coord[1], duration=0.6, tween=pyautogui.easeInOutQuad)
    else:
        pyautogui.moveTo(coord[0], coord[1])
    pyautogui.click()
    time.sleep(pause)

def type_text_with_speed(text, wpm=40):
    if not text:
        return
    base_delay = 60.0 / (wpm * 5)
    for ch in text:
        pyautogui.typewrite(ch)
        delay = base_delay * (1 + (0.1 - (0.2 * (hash(ch) % 100) / 100.0)))
        time.sleep(delay)

def type_text_and_enter(text, pause=0.5, wpm=40):
    type_text_with_speed(text, wpm)
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(pause)

def capture_full_screen(save_path):
    im = pyautogui.screenshot()
    im.save(save_path)
    print(f"📸 Full screenshot saved: {save_path}")
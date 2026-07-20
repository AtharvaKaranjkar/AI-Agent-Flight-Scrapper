# config.py
# ============================================================
#  ✏️  ALL YOUR INPUTS – Change these to match your workflow
# ============================================================

# ----- Timings (seconds) -----
WAIT_INITIAL = 5             # wait after starting script (to open website)
WAIT_AFTER_ENTER1 = 10       # wait after first Enter
WAIT_AFTER_CLICK2 = 2        # wait after step 2 click+type
WAIT_AFTER_CLICK4 = 2        # wait after step 4 (click at 741,471)
WAIT_AFTER_CLICK5 = 2        # wait after step 5 (click at 830,572)
WAIT_AFTER_SNAPSHOT = 2      # wait after taking first calendar snapshot
WAIT_AFTER_NAVIGATION = 2    # wait after clicking forward/backward buttons
WAIT_AFTER_DAY_CLICK = 20    # wait after clicking the day and final click



# ----- Target date (YYYY-MM-DD) -----
TARGET_DATE = "2026-07-24"

# ----- Texts to type (fill these with your actual texts) -----
TEXT1 = "https://www.makemytrip.com/"    # typed after click at (240,78)
TEXT2 = "BLR"   # typed after click at (304,464)
TEXT3 = "DEL"    # typed after click at (741,471)

# ----- NVIDIA Vision LLM credentials (for month detection) -----
NVIDIA_API_KEY = "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"   # <-- YOUR API KEY HERE
NVIDIA_MODEL = "nvidia/llama-3.1-nemotron-nano-vl-8b-v1"  # or your preferred model




# ----- Typing speed (words per minute) -----
TYPING_WPM =200
# ----- Step‑by‑step coordinates (absolute screen pixels) -----
CLICK_1 = (240, 78)          # first click
CLICK_7 = (261,372)
CLICK_2 = (304, 464)         # second click
CLICK_3 = (317, 574)         # third click
CLICK_4 = (741, 471)         # fourth click (then type TEXT3)
CLICK_5 = (830, 572)         # fifth click
CLICK_6 = (961, 798)         # final click after selecting day

# ----- Rectangle for first calendar snapshot (top‑left and bottom‑right) -----
CALENDAR_SNAPSHOT_REGION = (567,449,1567,960)   # (x1, y1, x2, y2)

# ----- Rectangle for the left panel's day grid (after navigation) -----
DAY_GRID_REGION = (581, 494, 1065, 970)   # adjust if needed

# ----- Navigation buttons (absolute coordinates) -----
FORWARD_BUTTON = (1538,521)    # right arrow
BACKWARD_BUTTON = (608,520)    # left arrow

# ----- Save folder for final screenshot -----
SAVE_FOLDER = r"C:\Users\Atharva Karanjkar\Downloads"
IMAGE_NAME_PREFIX = "MMT-"      # final name: MMT-YYYY-MM-DD.png

# ----- Optional: Tesseract path (only if not in PATH) -----
# Set to None to use default, or provide full path if Tesseract is not in PATH
TESSERACT_CMD = None   # e.g., r"C:\Program Files\Tesseract-OCR\tesseract.exe"
📄 README.md
Create a file named README.md with this content:

markdown
# AI-Agent-Flight-Scrapper

An AI-powered automation agent that scrapes flight prices using the NVIDIA **llama-3.1-nemotron-nano-vl-8b-v1** vision model and Tesseract OCR.

## Features
- Automated mouse/keyboard control via `pyautogui`
- Calendar navigation using Vision LLM + OCR fallback
- Date selection using robust grid‑based OCR
- Typing at configurable speed (default 40 WPM)
- Final screenshot saved with timestamp and custom naming

## Prerequisites
- Python 3.8+
- Tesseract OCR installed ([download for Windows](https://github.com/UB-Mannheim/tesseract/wiki))
- NVIDIA API key (for Vision LLM – sign up at [NVIDIA NGC](https://ngc.nvidia.com/signup))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AtharvaKaranjkar/AI-Agent-Flight-Scrapper.git
   cd AI-Agent-Flight-Scrapper
Install dependencies:

bash
pip install -r requirements.txt
(Optional) If Tesseract is not in your PATH, set the full path in config.py.

Configuration
Edit config.py with your:

NVIDIA_API_KEY – your personal API key from NGC

NVIDIA_MODEL – the vision model ID (default works)

Screen coordinates – update all CLICK_*, CALENDAR_SNAPSHOT_REGION, DAY_GRID_REGION, FORWARD_BUTTON, BACKWARD_BUTTON to match your screen and website layout.

Target date – set TARGET_DATE in YYYY-MM-DD format.

Texts – TEXT1, TEXT2, TEXT3 for input fields.

Typing speed – adjust TYPING_WPM.

Important:
config.py is ignored by Git (see .gitignore) to keep your API key secret.
If you want to share the structure, create a config.example.py with placeholder values.

Usage
Run the automation:

bash
python main.py
The script will:

Wait 5 seconds for you to open your website.

Follow your pre‑configured clicks and text entries.

Detect the current month from the calendar (using Vision LLM).

Click the forward/backward buttons to reach your target month.

Use OCR to locate the exact day number in the calendar grid.

Click on the day.

Take a full‑screen screenshot and save it in the project folder with a descriptive name.

File Structure
text
.
├── main.py               # Orchestration script
├── utils.py              # OCR, mouse, screenshot functions
├── config.py             # All user settings (ignored by Git)
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore            # Files/folders to exclude from Git
Dependencies
pyautogui – mouse & keyboard control

pillow – image processing

pytesseract – OCR wrapper

requests – API calls to NVIDIA

Install all with pip install -r requirements.txt.

How It Works (Brief)
Navigation – The script performs a series of clicks and text entries (you configure these).

Calendar reading – It takes a screenshot of the calendar region, sends it to the NVIDIA Vision LLM to read the month/year.

Month navigation – It computes how many forward/backward clicks are needed to reach your target month, then clicks the buttons.

Day selection – It captures the day grid and uses Tesseract OCR with grid inference to locate your target day, even if OCR misses some numbers.

Final screenshot – Saves the result with a timestamp and your custom input texts in the filename.

Troubleshooting
Tesseract not found – install Tesseract and ensure it’s in your system PATH, or set TESSERACT_CMD in config.py.

API key error – check that your NVIDIA API key is valid and has the required permissions.

Coordinates off – use a tool like pyautogui.mouseInfo() to get exact pixel positions for your screen.

Day not found – inspect debug_day_grid.png to verify that the captured region contains the calendar grid clearly.

License
MIT License – see LICENSE file (if you add one).

Author
Atharva Karanjkar


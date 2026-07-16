# AI-Agent-Flight-Scrapper

An AI-powered automation agent that scrapes flight prices using the NVIDIA **llama-3.1-nemotron-nano-vl-8b-v1** vision model and Tesseract OCR.

## Features
- Automated mouse/keyboard control via `pyautogui`
- Calendar navigation using Vision LLM + OCR fallback
- Date selection using robust grid‑based OCR
- Typing at configurable speed (40 WPM)
- Final screenshot saved with timestamp and custom naming

## Prerequisites
- Python 3.8+
- Tesseract OCR installed ([download](https://github.com/UB-Mannheim/tesseract/wiki))
- NVIDIA API key (for Vision LLM)

## Installation
```bash
git clone https://github.com/AtharvaKaranjkar/AI-Agent-Flight-Scrapper.git
cd AI-Agent-Flight-Scrapper
pip install -r requirements.txt
# swimming_race_report

An end-to-end Python tool for swimming race analysis: scrape official race results, perform manual stroke analysis via video, and generate a one-page performance report.

## Overview

This tool combines web-scraped race data with video-based stroke analysis to produce a comprehensive swimming performance report. It is designed for coaches, researchers, and analysts who want to integrate timing data with stroke metrics.

## Features

- **Result Scraping** (`extract_results`): Scrapes official swimming competition results from [swim.or.jp](https://result.swim.or.jp/) by event URL.
- **Video Stroke Analysis** (`analyze_video`): Interactive OpenCV-based GUI for clicking stroke entry points in race videos to compute stroke rate and stroke length.
- **Report Generation** (`generate_report`): Creates a performance report with plots of stroke rate, stroke length, and velocity using Matplotlib.

## Requirements

- Python 3.8+
- OpenCV (`opencv-python`)
- pandas
- NumPy
- Matplotlib
- BeautifulSoup4
- requests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python swimming_race_report.py
```

> **Note**: The script requires a valid race result URL from swim.or.jp and a video file for analysis.

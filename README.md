# Astronomy utilities : Telescope & Eyepiece Comparator

A command-line tool to help amateur astronomers choose the best optical combinations. It calculates magnification, exit pupil, and highlights potential optical issues based on theoretical limits.

The tool uses the following standard astronomical limits:
- max exit pupil: 6mm (typical for adult human eyes)
- min exit pupil: 0.5mm
- ideal range: 1mm to 5mm


## Features

- **Telescope Stats:** : calculates F/D ratio, minimum, and maximum practical magnification
- **Eyepiece Comparison:** : generates a matrix of magnification and exit pupil for multiple telescopes
- **Visual Cues:** : uses color coding to highlight ideal vs. suboptimal configurations


## Usage

Prepare your `data.json` file (see example bellow).

Run the comparison : `astronomy compare data.json`

To see constants and formulas used : `astronomy print-parameters`


JSON file example :

```json
{
    "telescopes": [
        {
            "name": "Newton on Dobson mount",
            "diameter": 203,
            "focal": 1200
        },
    ],
    "eyepieces": [
        {
            "name": "Artesky Syper ED 25mm",
            "focal": 25
        },
    ]
}
```

## Local development

First, clone the repository then :

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Build process :

```bash
pip install pyinstaller
pyinstaller --onedir --name astronomy main.py
```
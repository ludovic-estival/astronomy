## Astronomy utilities

### Installation

It's recommended to use a Python virtual environment: `python -m venv venv`

Activation on Linux: `source venv/bin/activate`

Activation on Windows: `.\venv\Scripts\activate` (use `Set-ExecutionPolicy Unrestricted -Scope Process`)

Install dependencies: `pip install -r requirements.txt`

### Usage

Use `python main.py compare [JSON_FILE]` to compare telescopes with a range of oculars.

JSON file expected :

```json
{
    "telescopes": [
        {
            "name": "Newton on Dobson",
            "diameter": 203,
            "focal": 1200
        },
    ],
    "oculars": [
        {
            "name": "Artesky Syper ED 25mm",
            "focal": 25
        },
    ]
}
```

Use `python main.py print-parameters` to see constants and formulas used.

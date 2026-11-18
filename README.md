# weather-tracker

A Python command-line script that fetches daily temperatures from the
[Open-Meteo](https://open-meteo.com/) API, computes summary statistics, and
exports the result to a CSV file.

## Features

- Fetches daily min/max temperatures for a configured location (Open-Meteo API)
- Computes the average, minimum and maximum temperatures
- Validates the API response and detects missing or incomplete data
- Exports a CSV file with a summary block
- Logs to the console and to a log file
- Handles network errors, invalid API responses and incomplete data

## Architecture

Single script, `meteo.py`, with a linear pipeline:

```
Open-Meteo API  ->  validation  ->  pandas DataFrame  ->  statistics  ->  CSV export + check
                         |
                     logging (console + file)
```

The location (latitude, longitude and city name) is set directly in the script.

## Requirements

- Python 3.14 (version used for development)
- Dependencies pinned in `requirements.txt` (`requests`, `pandas`)

## Usage

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py meteo.py
```

## Output

- `meteo.csv`: one row per day (date, max, min and mean temperature), followed
  by a summary block (period, average, minimum and maximum temperatures)
- `meteo.log`: execution log

Both files are generated at each run and are ignored by Git.

## Roadmap

- Automated tests (pytest)
- GitHub Actions workflow (lint and tests)

## License

MIT, see [LICENSE](LICENSE).
# weather-tracker

A Python command-line script that fetches daily temperatures from the
[Open-Meteo](https://open-meteo.com/) API, computes summary statistics, and
writes the result to a CSV file.

> Work in progress: the README will be completed (architecture, usage,
> sample output) as the project is versioned.

## Features

- Fetches daily min/max temperatures for a given city (Open-Meteo API)
- Computes average, minimum and maximum temperatures
- Detects missing or incomplete data
- Exports a CSV file with a summary section
- Handles network errors, invalid API responses and incomplete data

## Requirements

- Python 3.10+
- `requests`, `pandas`

## License

MIT, see [LICENSE](LICENSE).

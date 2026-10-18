# Data Cleaning Notes

## Source
Open-Meteo Historical Weather API (CC BY 4.0), daily data, 2015-01-01 to 2025-12-31.

## Scope
- 5 cities: Newcastle, Middlesbrough, Sunderland, London, Manchester
- 20,090 rows (4,018 days per city)
- Variables: max, min and mean temperature (°C), rainfall (mm), max wind speed (km/h)

## Checks performed
| Check | Method | Result |
|-------|--------|--------|
| Missing values | `isna().sum()` on all columns | 0 missing |
| Duplicates | Duplicate (date, city) pairs | 0 found |
| Impossible temperatures | Max temp outside -30 to 45 °C | 0 removed |
| Negative rainfall | Rain below 0 mm | 0 removed |

## Transformations
- Renamed columns to include units (e.g. `temp_max_c`, `rain_mm`)
- Parsed dates as datetime
- Added `year`, `month`, `month_name`, `season` for grouping
- Seasons defined meteorologically: Winter (Dec-Feb), Spring (Mar-May), Summer (Jun-Aug), Autumn (Sep-Nov)

## Value ranges
- Temperature max: [-2.2] to [38.0] °C
- Rainfall: [0.0] to [60.3] mm
- Wind max: [3.3] to [68.2] km/h

## Limitations
- Data is modelled reanalysis at a grid point, not readings from a physical weather station
- Coordinates represent city centres, so local microclimates are not captured
- Rainfall totals may differ from Met Office station records
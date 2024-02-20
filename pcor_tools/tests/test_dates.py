from datetime import datetime

def parse_date(date_str):
    # Define common date formats
    date_formats = [
        '%Y',           # Year only
        '%Y-%m-%d',     # Year-month-day
        '%b-%y',        # Abbreviated month-year (e.g., Feb-00)
        '%m/%d/%y',     # Month/day/year
        '%Y-%Y',        # Year range (e.g., 1999-2000)
        '%Y-%Y-%H-%M',  # Year range with hours and minutes (not present in example, adjust accordingly)
        'current',      # Special case for 'current'
    ]

    # Parse date using different formats
    for fmt in date_formats:
        try:
            if fmt == 'current':
                return 'current'
            else:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            pass

    # Return None if date format is not recognized
    return None

# File names and date formats
files = {
    "GeoExposure _1.4.0_MTBS.xlsm": "1984",
    "GeoExposure_1.4.0 EPA-AQS.xlsm": "1980",
    "GeoExposure_1.4.0 National Interagency Fire Center.xlsm": "2000",
    "GeoExposure_1.4.0_NASA_LAADS_DAAC.xlsm": "1957",
    "GeoExposure_1.4.0_NASA_MODIS.xlsm": "Feb-00",
    "GeoExposure_1.4.0_Wildfire Smoke Estimates (Vargo).xlsm": ["6/1/10", "12/17/19"],
    "PopulationData_1.4.1_WA-APCD.xlsm": ["2014"]
}

# Convert dates and print results
for file, dates in files.items():
    if isinstance(dates, list):
        converted_dates = [parse_date(date) for date in dates]
        print(f"{file}: {converted_dates}")
    else:
        converted_date = parse_date(dates)
        print(f"{file}: {converted_date}")
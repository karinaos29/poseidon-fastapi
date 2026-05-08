import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# The 15 vessels from whitelist
VESSELS = [
    "vessel_rotterdam_001", "vessel_rotterdam_002",
    "vessel_amsterdam_001", "vessel_amsterdam_002",
    "vessel_hamburg_001", "vessel_hamburg_002",
    "vessel_bremerhaven_001", "vessel_bremerhaven_002",
    "vessel_gdansk_001", "vessel_gdansk_002",
    "vessel_gdynia_001", "vessel_gdynia_002",
    "vessel_copenhagen_001", "vessel_copenhagen_002",
    "vessel_esbjerg_001"
]

def generate_historical_data(file_path: str, year: int = 2025):
    """Generates 1 year of hourly telemetry for 15 vessels (131,400 rows)."""
    
    # Ensure the data directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["vessel_id", "timestamp", "speed_knots", "draft_m", "heading_deg", "fuel_rate_lph", "position"])
        
        # 365 days * 24 hours = 8760 iterations
        for hour_offset in range(365 * 24):
            current_time = start_date + timedelta(hours=hour_offset)
            time_str = current_time.isoformat()
            
            for vessel in VESSELS:
                # 99% of the time, generate normal, healthy data
                if random.random() > 0.01:
                    speed = round(random.uniform(0.0, 24.0), 1)
                    draft = round(random.uniform(5.0, 14.0), 1)
                    heading = random.randint(0, 359)
                    fuel = round(random.uniform(100.0, 400.0), 1)
                else:
                    # 1% of the time, inject intentional AIS glitches for your pandas cleaner to catch
                    glitch_type = random.choice(["negative", "speed_high", "heading_high", "missing"])
                    if glitch_type == "negative":
                        speed = -5.0
                        draft = -1.0
                        heading = 180
                        fuel = -50.0
                    elif glitch_type == "speed_high":
                        speed = 65.0  # Over the 50 knot limit
                        draft = 10.0
                        heading = 90
                        fuel = 500.0
                    elif glitch_type == "heading_high":
                        speed = 15.0
                        draft = 10.0
                        heading = 410  # Needs to be modulo 360
                        fuel = 200.0
                    else:
                        # Return a row with missing timestamp to test dropna()
                        writer.writerow([vessel, "", 10.0, 8.0, 180, 150.0, "POINT(4.5 52.0)"])
                        continue
                
                # Generate a random coordinate roughly in the North Sea / Baltic region
                lon = round(random.uniform(3.0, 20.0), 4)
                lat = round(random.uniform(51.0, 56.0), 4)
                position_wkt = f"POINT({lon} {lat})"
                
                writer.writerow([vessel, time_str, speed, draft, heading, fuel, position_wkt])

    print(f"✅ Successfully generated data at {file_path}")

if __name__ == "__main__":
    output_file = "data/historical_readings.csv"
    print(f"Generating 131,400 rows of telemetry data to {output_file}...")
    generate_historical_data(output_file)
"""
View Earthquake Data
Simple script to query and display earthquake data from the database
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from database import get_db_connection

def view_earthquakes(limit=20, min_magnitude=4.0):
    """View recent earthquakes from database"""
    
    print(f"\n🌍 Recent Earthquakes (M{min_magnitude}+)")
    print("=" * 80)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get earthquake count
                cur.execute("SELECT COUNT(*) FROM earthquakes")
                total_count = cur.fetchone()[0]
                
                print(f"\nTotal earthquakes in database: {total_count}")
                
                # Get recent earthquakes
                cur.execute("""
                    SELECT magnitude, place, timestamp, latitude, longitude, 
                           depth_km, tsunami, significance
                    FROM earthquakes
                    WHERE magnitude >= %s
                    ORDER BY magnitude DESC, timestamp DESC
                    LIMIT %s
                """, (min_magnitude, limit))
                
                earthquakes = cur.fetchall()
                
                if not earthquakes:
                    print(f"\nNo earthquakes found with magnitude >= {min_magnitude}")
                    return
                
                print(f"\nShowing top {len(earthquakes)} by magnitude:\n")
                
                for eq in earthquakes:
                    mag, place, timestamp, lat, lon, depth, tsunami, sig = eq
                    
                    # Magnitude emoji
                    if mag >= 6.0:
                        emoji = "🔴"
                        level = "MAJOR"
                    elif mag >= 5.0:
                        emoji = "🟡"
                        level = "STRONG"
                    else:
                        emoji = "🟢"
                        level = "MODERATE"
                    
                    # Tsunami warning
                    tsunami_warning = " 🌊 TSUNAMI" if tsunami else ""
                    
                    print(f"{emoji} M{mag:.1f} - {level}{tsunami_warning}")
                    print(f"   Location: {place}")
                    print(f"   Coordinates: {lat:.2f}°, {lon:.2f}°")
                    print(f"   Depth: {depth:.1f} km")
                    print(f"   Time: {timestamp}")
                    print(f"   Significance: {sig}")
                    print()
                
                # Statistics
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        AVG(magnitude) as avg_mag,
                        MAX(magnitude) as max_mag,
                        COUNT(CASE WHEN tsunami THEN 1 END) as tsunami_count
                    FROM earthquakes
                """)
                stats = cur.fetchone()
                
                print("\n" + "=" * 80)
                print("📊 Statistics:")
                print(f"   Total earthquakes: {stats[0]}")
                print(f"   Average magnitude: {stats[1]:.1f}")
                print(f"   Largest earthquake: M{stats[2]:.1f}")
                print(f"   Tsunami warnings: {stats[3]}")
                
    except Exception as e:
        print(f"❌ Error querying earthquakes: {e}")

if __name__ == "__main__":
    view_earthquakes(limit=20, min_magnitude=4.5)

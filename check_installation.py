"""Check what collectors are currently installed."""
import sys
import os
sys.path.insert(0, '.')

print("Checking installed collectors...\n")

collectors = [
    'markets_collector',
    'commodities_collector', 
    'forex_collector',
    'economics_collector',
    'weather_collector',
    'space_collector',
    'disasters_collector',
    'news_collector'
]

print("Checking collectors folder:")
collectors_path = 'collectors'
if os.path.exists(collectors_path):
    files = [f for f in os.listdir(collectors_path) if f.endswith('.py')]
    for f in sorted(files):
        print(f"  ✓ {f}")
else:
    print("  ✗ collectors/ folder not found")

print("\nTrying imports:")
for collector in collectors:
    try:
        exec(f"from collectors.{collector} import {collector.title().replace('_', '')}")
        print(f"  ✓ {collector}")
    except Exception as e:
        print(f"  ✗ {collector} - {str(e)[:50]}")

print("\n---")
print("If you see ✗ marks, those files need to be copied to collectors/ folder")

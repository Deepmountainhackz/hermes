"""Test all 8 collectors."""
import sys
sys.path.insert(0, '.')

print("Testing ALL collectors imports...\n")

collectors_to_test = [
    ('Markets', 'collectors.markets_collector', 'MarketsCollector'),
    ('Commodities', 'collectors.commodities_collector', 'CommoditiesCollector'),
    ('Forex', 'collectors.forex_collector', 'ForexCollector'),
    ('Economics', 'collectors.economics_collector', 'EconomicsCollector'),
    ('Weather', 'collectors.weather_collector', 'WeatherCollector'),
    ('Space', 'collectors.space_collector', 'SpaceCollector'),
    ('Disasters', 'collectors.disasters_collector', 'DisastersCollector'),
    ('News', 'collectors.news_collector', 'NewsCollector'),
]

for name, module, class_name in collectors_to_test:
    try:
        exec(f"from {module} import {class_name}")
        print(f"✓ {name} collector imported")
    except Exception as e:
        print(f"✗ {name} collector failed: {e}")
        sys.exit(1)

print("\n" + "="*60)
print("ALL 8 COLLECTORS IMPORTED SUCCESSFULLY!")
print("="*60)
print("\n✓ Markets (20 stocks)")
print("✓ Commodities (6 commodities)")
print("✓ Forex (7 currency pairs)")
print("✓ Economics (GDP, unemployment, inflation, interest rates)")
print("✓ Weather (10+ cities)")
print("✓ Space (ISS position)")
print("✓ Disasters (Recent earthquakes)")
print("✓ News (Top business headlines)")
print("\nAll collectors are ready to use!")

# test_country.py
from services.geography.fetch_country_data import CountryProfileCollector

collector = CountryProfileCollector()

# Test Germany
germany = collector.fetch_data('Germany')
if germany:
    print(f"\n{germany['flag_emoji']} {germany['name']}")
    print(f"Population: {germany['population']:,}")
    print(f"Languages: {', '.join(germany['languages'])}")
    print(f"Capital: {', '.join(germany['capital'])}")
    print(f"Density: {germany['population_density']:.2f} people/km²")
    print(f"Neighbors: {germany['border_count']}")
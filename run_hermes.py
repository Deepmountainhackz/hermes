"""
Hermes Master Control - Run all data collectors from one interface
"""

import os
from datetime import datetime

def print_header():
    """Display the Hermes header"""
    print()
    print("=" * 70)
    print("🌍 HERMES - Global Systems Intelligence Platform")
    print("=" * 70)
    print()

def print_menu():
    """Display the main menu"""
    print("Available Data Collectors:")
    print()
    print("  [1] Markets Layer")
    print("      - Fetch stock market data (AAPL, MSFT, GOOGL)")
    print()
    print("  [2] Space Layer - ISS Tracker")
    print("      - Real-time International Space Station position")
    print()
    print("  [3] Space Layer - NEO Monitor")
    print("      - Near-Earth Object (asteroid) tracking")
    print()
    print("  [4] Space Layer - Solar Activity")
    print("      - Solar flares and geomagnetic storms")
    print()
    print("  [5] Run ALL Collectors")
    print("      - Execute complete data collection cycle")
    print()
    print("  [0] Exit")
    print()

def run_market_collector():
    """Run the market data collector"""
    print("\n🚀 Launching Markets Collector...")
    print("-" * 70)
    os.system('python fetch_market_data.py')
    print("-" * 70)
    print("✅ Markets collection complete!\n")

def run_iss_collector():
    """Run the ISS tracker"""
    print("\n🚀 Launching ISS Tracker...")
    print("-" * 70)
    os.system('python fetch_iss_data.py')
    print("-" * 70)
    print("✅ ISS tracking complete!\n")

def run_neo_collector():
    """Run the NEO monitor"""
    print("\n🚀 Launching NEO Monitor...")
    print("-" * 70)
    os.system('python fetch_neo_data.py')
    print("-" * 70)
    print("✅ NEO monitoring complete!\n")

def run_solar_collector():
    """Run the solar activity monitor"""
    print("\n🚀 Launching Solar Activity Monitor...")
    print("-" * 70)
    os.system('python fetch_solar_data.py')
    print("-" * 70)
    print("✅ Solar monitoring complete!\n")

def run_all_collectors():
    """Run all data collectors in sequence"""
    start_time = datetime.now()
    
    print("\n" + "=" * 70)
    print("🚀 FULL HERMES DATA COLLECTION CYCLE")
    print("=" * 70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run each collector
    collectors = [
        ("Markets", run_market_collector),
        ("ISS", run_iss_collector),
        ("NEO", run_neo_collector),
        ("Solar", run_solar_collector)
    ]
    
    completed = []
    failed = []
    
    for name, collector_func in collectors:
        try:
            collector_func()
            completed.append(name)
        except Exception as e:
            print(f"❌ {name} collector failed: {e}\n")
            failed.append(name)
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("=" * 70)
    print("📊 COLLECTION CYCLE SUMMARY")
    print("=" * 70)
    print(f"Completed: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration:.1f} seconds")
    print()
    print(f"✅ Successful: {len(completed)}/{len(collectors)}")
    for name in completed:
        print(f"   - {name}")
    
    if failed:
        print()
        print(f"❌ Failed: {len(failed)}/{len(collectors)}")
        for name in failed:
            print(f"   - {name}")
    
    print()
    print("=" * 70)
    print()

def main():
    """Main function - interactive menu"""
    print_header()
    
    while True:
        print_menu()
        
        choice = input("Select option (0-5): ").strip()
        
        if choice == "1":
            run_market_collector()
        elif choice == "2":
            run_iss_collector()
        elif choice == "3":
            run_neo_collector()
        elif choice == "4":
            run_solar_collector()
        elif choice == "5":
            run_all_collectors()
        elif choice == "0":
            print("\n👋 Shutting down Hermes. Stay curious!\n")
            break
        else:
            print("\n⚠️  Invalid option. Please enter 0-5.\n")
        
        # Pause before showing menu again
        input("Press Enter to continue...")
        print("\n" * 2)

if __name__ == "__main__":
    main()
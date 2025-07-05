#!/usr/bin/env python3
"""
Debug schedule times
"""

import sys
sys.path.insert(0, 'src')

def test_schedule():
    print("🔍 Testing schedule information...")

    try:
        from schedule import Schedule

        print("✅ Creating schedule...")
        schedule = Schedule()

        print("📊 Getting schedule info...")
        info = schedule.get_schedule_info()

        print("Schedule information:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("\n📄 Testing SunTimes directly...")
        from suntimes import SunTimes
        suntime = SunTimes()

        print(f"Dawn: {suntime.get_dawn()}")
        print(f"Sunrise: {suntime.get_sunrise()}")
        print(f"Sunset: {suntime.get_sunset()}")
        print(f"Dusk: {suntime.get_dusk()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schedule()

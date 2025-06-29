import asyncio
import aiohttp
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8001/v2"
METRICS_ENDPOINT = f"{API_BASE_URL}/sensormetrics"
NUM_ENTRIES = 150


def generate_sensor_metrics() -> List[Dict]:
    """Generate semi-random sensor metrics"""
    metrics = []
    base_time = datetime.now()

    for i in range(NUM_ENTRIES):
        # Generate timestamps going backwards in time
        timestamp_offset = timedelta(
            minutes=random.randint(1, 1440))  # 1 min to 24 hours ago
        device_timestamp = base_time - timestamp_offset
        server_timestamp = device_timestamp + \
            timedelta(seconds=random.randint(0, 30))  # Small server delay

        metric = {
            # 10 different sensors
            "device_id": f"sensor_{random.randint(1, 10):03d}",
            "timestamp_device": int(device_timestamp.timestamp()),
            "timestamp_server": int(server_timestamp.timestamp()),
            "temperature": round(random.uniform(15.0, 35.0), 2),  # 15-35°C
            "humidity": round(random.uniform(30.0, 90.0), 2)      # 30-90%
        }
        metrics.append(metric)

    return metrics


async def post_metric(session: aiohttp.ClientSession, metric: Dict) -> bool:
    """Post a single metric to the API"""
    try:
        async with session.post(METRICS_ENDPOINT, json=metric) as response:
            if response.status == 200:
                return True
            else:
                print(f"Failed to post metric: {response.status}")
                return False
    except Exception as e:
        print(f"Error posting metric: {e}")
        return False


async def main():
    """Main function to create and post test metrics"""
    print(f"Generating {NUM_ENTRIES} test sensor metrics...")
    metrics = generate_sensor_metrics()

    print(f"Posting metrics to {METRICS_ENDPOINT}...")

    async with aiohttp.ClientSession() as session:
        success_count = 0

        for i, metric in enumerate(metrics, 1):
            success = await post_metric(session, metric)
            if success:
                success_count += 1

            if i % 10 == 0:
                print(
                    f"Progress: {i}/{NUM_ENTRIES} ({success_count} successful)")

    print(
        f"Completed! Successfully posted {success_count}/{NUM_ENTRIES} metrics")

if __name__ == "__main__":
    asyncio.run(main())

# pyright: reportMissingImports=false
import argparse
import glob
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

try:
    import requests  # type: ignore
except ImportError:
    print("Error: 'requests' package is missing. Please install via: pip install requests")
    sys.exit(1)

DEFAULT_API_URL = "http://127.0.0.1:8000/sensor-alert"
STATUSES = ["NORMAL", "WARNING", "OVERHEATING", "FAILURE"]
MACHINE_PREFIXES = ["TURBINE", "PUMP", "COMPRESSOR", "GENERATOR", "MOTOR"]

class AlertGenerator:
    """Generates synthetic telemetry payloads for equipment alert testing."""
    
    @staticmethod
    def random_payload(anomaly_rate: float = 0.2) -> Dict[str, Any]:
        prefix = random.choice(MACHINE_PREFIXES)
        machine_id = f"{prefix}-{random.randint(1, 99):03d}"
        
        is_anomaly = random.random() < anomaly_rate
        if is_anomaly:
            status = random.choice(["WARNING", "OVERHEATING", "FAILURE"])
            temperature = round(random.uniform(80.0, 140.0), 1)
            vibration = round(random.uniform(4.5, 12.0), 2)
            pressure = round(random.uniform(2.0, 6.0), 2)
        else:
            status = "NORMAL"
            temperature = round(random.uniform(25.0, 65.0), 1)
            vibration = round(random.uniform(0.5, 3.5), 2)
            pressure = round(random.uniform(0.9, 1.5), 2)
            
        return {
            "machine_id": machine_id,
            "temperature": temperature,
            "vibration": vibration,
            "status": status,
            "pressure": pressure,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class AlertClient:
    """Sends requests to FastAPI sensor-alert endpoint and analyzes responses."""
    
    def __init__(self, api_url: str = DEFAULT_API_URL, timeout: float = 5.0):
        self.api_url = api_url
        self.timeout = timeout
        
    def send_alert(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any], float]:
        """Sends JSON payload to FastAPI endpoint. Returns (status_code, response_data, latency_ms)."""
        start_time = time.time()
        try:
            res = requests.post(self.api_url, json=payload, timeout=self.timeout)
            latency_ms = (time.time() - start_time) * 1000.0
            
            try:
                data = res.json()
            except Exception:
                data = {"raw_response": res.text}
                
            return res.status_code, data, round(latency_ms, 2)
        except requests.exceptions.RequestException as e:
            latency_ms = (time.time() - start_time) * 1000.0
            return 0, {"error": str(e)}, round(latency_ms, 2)

class TestRunner:
    """Automates test suite execution covering valid payload edge cases and error scenarios."""
    __test__ = False
    
    def __init__(self, client: AlertClient):
        self.client = client
        
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Scenario 1: Valid Normal Telemetry",
                "payload": {
                    "machine_id": "TURBINE-101",
                    "temperature": 45.0,
                    "vibration": 1.5,
                    "status": "NORMAL"
                },
                "expected_status": 200,
                "description": "Standard baseline telemetry expecting 200 OK."
            },
            {
                "name": "Scenario 2: Valid Overheating Alert",
                "payload": {
                    "machine_id": "PUMP-202",
                    "temperature": 92.5,
                    "vibration": 5.8,
                    "status": "OVERHEATING"
                },
                "expected_status": 200,
                "description": "High temperature alert expecting 200 OK with HIGH severity recommendation."
            },
            {
                "name": "Scenario 3: Valid Critical Failure Alert",
                "payload": {
                    "machine_id": "COMPRESSOR-303",
                    "temperature": 125.0,
                    "vibration": 10.2,
                    "status": "FAILURE"
                },
                "expected_status": 200,
                "description": "Critical failure alert expecting 200 OK with CRITICAL shutdown action."
            },
            {
                "name": "Scenario 4: Error - Invalid Field Type (Temperature as String)",
                "payload": {
                    "machine_id": "TURBINE-404",
                    "temperature": "EXTREME_HOT",
                    "vibration": 2.0,
                    "status": "NORMAL"
                },
                "expected_status": 422,
                "description": "String temperature type invalidation expecting 422 Unprocessable Entity."
            },
            {
                "name": "Scenario 5: Error - Missing Required Field (machine_id)",
                "payload": {
                    "temperature": 75.0,
                    "vibration": 3.0,
                    "status": "WARNING"
                },
                "expected_status": 422,
                "description": "Missing machine_id field expecting 422 Unprocessable Entity."
            },
            {
                "name": "Scenario 6: Error - Negative Vibration (Out of Bounds)",
                "payload": {
                    "machine_id": "MOTOR-505",
                    "temperature": 50.0,
                    "vibration": -10.0,
                    "status": "NORMAL"
                },
                "expected_status": 422,
                "description": "Negative vibration value violating ge=0 constraint expecting 422."
            },
            {
                "name": "Scenario 7: Error - Unrecognized Operational Status",
                "payload": {
                    "machine_id": "PUMP-606",
                    "temperature": 60.0,
                    "vibration": 2.0,
                    "status": "EXPLODING"
                },
                "expected_status": 422,
                "description": "Unregistered status enum expecting 422 Unprocessable Entity."
            }
        ]

    def run_suite(self) -> bool:
        print("\n" + "="*70)
        print(" AUTOMATED IOT ALERT TEST SUITE & SCENARIO VERIFICATION")
        print(" Target URL:", self.client.api_url)
        print("="*70)
        
        scenarios = self.get_test_scenarios()
        passed = 0
        total = len(scenarios)
        
        for idx, sc in enumerate(scenarios, 1):
            print(f"\n[Test {idx}/{total}] {sc['name']}")
            print(f" Description : {sc['description']}")
            print(f" Payload     : {json.dumps(sc['payload'])}")
            
            code, resp, latency = self.client.send_alert(sc['payload'])
            expected = sc['expected_status']
            
            is_pass = (code == expected)
            if is_pass:
                passed += 1
                status_str = f"PASSED ({code} OK)" if code == 200 else f"PASSED ({code} Expected Error Handled)"
                print(f" Result      : \033[92m[✓] {status_str}\033[0m in {latency} ms")
                if code == 200 and "severity" in resp:
                    print(f" Response    : Severity={resp.get('severity')} | Prescription: {resp.get('prescription')}")
                elif code == 422:
                    print(f" Validation  : {resp.get('detail', [{}])[0].get('msg', 'Validation error returned correctly')}")
            else:
                print(f" Result      : \033[91m[✗] FAILED (Got HTTP {code}, expected {expected})\033[0m in {latency} ms")
                print(f" Response    : {json.dumps(resp)}")
                
        print("\n" + "="*70)
        print(f" TEST SUITE SUMMARY: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
        print("="*70 + "\n")
        return passed == total

def run_sample_payloads(client: AlertClient, payload_file: str = None):
    """Loads and sends sample JSON payloads from sample_payloads/ directory or specific file."""
    print("\n" + "="*70)
    print(" SAMPLE JSON PAYLOAD SIMULATION MODE")
    print("="*70)
    
    files = []
    if payload_file:
        files = [payload_file]
    else:
        sample_dir = os.path.join(os.path.dirname(__file__), "sample_payloads")
        if os.path.exists(sample_dir):
            files = sorted(glob.glob(os.path.join(sample_dir, "*.json")))
            
    if not files:
        print("No JSON sample payload files found.")
        return

    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\n---> Sending sample payload: {filename}")
        try:
            with open(filepath, 'r') as f:
                payload = json.load(f)
            print(f" Payload: {json.dumps(payload)}")
            code, resp, latency = client.send_alert(payload)
            print(f" HTTP Status: {code} ({latency} ms)")
            print(f" Response   : {json.dumps(resp, indent=2)}")
        except Exception as e:
            print(f" Error loading/sending {filename}: {e}")

def run_stream_simulation(client: AlertClient, count: int, interval: float, anomaly_rate: float):
    """Streams generated IoT telemetry payloads over time."""
    print("\n" + "="*70)
    print(" STREAMING IOT TELEMETRY SIMULATION MODE")
    print(f" Total Count: {count} | Interval: {interval}s | Anomaly Rate: {anomaly_rate*100:.0f}%")
    print("="*70 + "\n")
    
    success_count = 0
    error_count = 0
    total_latency = 0.0

    for i in range(1, count + 1):
        payload = AlertGenerator.random_payload(anomaly_rate)
        code, resp, latency = client.send_alert(payload)
        total_latency += latency
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_tag = "\033[92mSUCCESS\033[0m" if code == 200 else f"\033[91mHTTP {code}\033[0m"
        
        print(f"[{timestamp}] Alert #{i}/{count} | Machine: {payload['machine_id']} | Status: {payload['status']} | "
              f"Temp: {payload['temperature']}°C | Vib: {payload['vibration']} | -> {status_tag} ({latency} ms)")
        
        if code == 200:
            success_count += 1
            if resp.get("severity") in ["HIGH", "CRITICAL"]:
                print(f"   ↳ ALERT DETECTED! Severity: {resp.get('severity')} | Prescription: {resp.get('prescription')}")
        else:
            error_count += 1
            
        if i < count:
            time.sleep(interval)
            
    avg_latency = round(total_latency / count, 2) if count > 0 else 0
    print("\n" + "="*70)
    print(f" SIMULATION COMPLETE: Sent: {count} | Success (200): {success_count} | Errors: {error_count} | Avg Latency: {avg_latency} ms")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="IoT Equipment Alert Simulator & FastAPI Test Harness")
    parser.add_argument("--url", default=DEFAULT_API_URL, help=f"FastAPI endpoint URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--mode", choices=["test", "sample", "stream", "random"], default="test",
                        help="Simulation mode: 'test' (run test suite), 'sample' (send json payloads), 'stream' (continuous telemetry), 'random' (send N random alerts)")
    parser.add_argument("--count", type=int, default=5, help="Number of telemetry alerts to send in stream/random mode (default: 5)")
    parser.add_argument("--interval", type=float, default=1.0, help="Delay between streaming alerts in seconds (default: 1.0)")
    parser.add_argument("--anomaly-rate", type=float, default=0.2, help="Probability of anomaly generation in stream mode [0.0 - 1.0] (default: 0.2)")
    parser.add_argument("--payload-file", help="Path to specific JSON sample payload file (for sample mode)")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP request timeout in seconds (default: 5.0)")

    args = parser.parse_args()
    client = AlertClient(api_url=args.url, timeout=args.timeout)

    if args.mode == "test":
        runner = TestRunner(client)
        success = runner.run_suite()
        sys.exit(0 if success else 1)
    elif args.mode == "sample":
        run_sample_payloads(client, args.payload_file)
    elif args.mode == "stream" or args.mode == "random":
        run_stream_simulation(client, count=args.count, interval=args.interval, anomaly_rate=args.anomaly_rate)

if __name__ == "__main__":
    main()

import urllib.request
import time
import sys

endpoints = {
    "FastAPI Docs": "http://localhost:8000/docs",
    "FastAPI Metrics": "http://localhost:8000/metrics",
    "Prometheus": "http://localhost:9090",
    "Grafana": "http://localhost:3000",
    "MLflow": "http://localhost:5000",
    "Frontend": "http://localhost:5173"
}

def check_endpoints():
    all_ok = True
    for name, url in endpoints.items():
        try:
            req = urllib.request.Request(url)
            # Some apps might return 401 or 302 (like Grafana) but they are reachable
            response = urllib.request.urlopen(req, timeout=5)
            status = response.getcode()
            print(f"[OK] {name} ({url}) returned {status}")
        except urllib.error.HTTPError as e:
            # 404 for prometheus root is normal, just check if we can reach it
            print(f"[OK] {name} ({url}) reached but returned {e.code}")
        except urllib.error.URLError as e:
            print(f"[FAIL] {name} is unreachable: {e.reason}")
            all_ok = False
        except Exception as e:
            print(f"[FAIL] {name} error: {str(e)}")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    check_endpoints()

import asyncio
import argparse
import json
from pathlib import Path
import httpx

async def replay_run(run_id: str, run_path: Path, delay: float):
    metrics_file = run_path / "round_metrics.json"
    if not metrics_file.exists():
        print(f"Error: {metrics_file} not found.")
        return
        
    with open(metrics_file, "r") as f:
        metrics = json.load(f)
        
    url = f"http://localhost:8000/api/v1/training/runs/{run_id}/events/test"
    
    async with httpx.AsyncClient() as client:
        # Emit training.started
        await client.post(url, json={"event": "training.started", "payload": {"status": "started"}})
        await asyncio.sleep(delay)
        
        rounds = metrics.get("rounds", {})
        for round_num_str in sorted(rounds.keys(), key=int):
            round_num = int(round_num_str)
            
            # Emit round.started
            await client.post(url, json={"event": "round.started", "round": round_num})
            await asyncio.sleep(delay * 0.5)
            
            # Emit some mock client events
            for i in range(3):
                await client.post(url, json={
                    "event": "client.completed", 
                    "round": round_num, 
                    "client_id": f"client_{i}",
                    "payload": {"status": "completed"}
                })
                await asyncio.sleep(delay * 0.2)
                
            # Emit aggregation.started
            await client.post(url, json={"event": "aggregation.started", "round": round_num})
            await asyncio.sleep(delay * 0.5)
            
            # Emit metrics.updated
            round_data = rounds[round_num_str]
            orig_metrics = round_data.get("original", {})
            await client.post(url, json={
                "event": "metrics.updated", 
                "round": round_num,
                "payload": {
                    "accuracy": orig_metrics.get("accuracy"),
                    "loss": round_data.get("loss"),
                    "f1": orig_metrics.get("f1")
                }
            })
            await asyncio.sleep(delay)
            
        # Emit training.completed
        await client.post(url, json={"event": "training.completed", "payload": {"status": "completed"}})
        print("Replay finished.")

async def main():
    parser = argparse.ArgumentParser(description="Replay a federated run via WebSockets.")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID to emit events for")
    parser.add_argument("--run-path", type=str, default=None, help="Path to the federation run folder")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between events in seconds")
    args = parser.parse_args()
    
    run_path = Path(args.run_path) if args.run_path else Path(f"ml/federation/runs/{args.run_id}")
    
    await replay_run(args.run_id, run_path, args.delay)

if __name__ == "__main__":
    asyncio.run(main())

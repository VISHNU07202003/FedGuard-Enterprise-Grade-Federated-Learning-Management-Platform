import asyncio
import argparse
from pathlib import Path
from app.db.session import AsyncSessionLocal
from app.services.ingestion_service import ingest_federation_run

async def main():
    parser = argparse.ArgumentParser(description="Ingest a federated run into the database.")
    parser.add_argument("--run-path", type=str, required=True, help="Path to the federation run folder")
    args = parser.parse_args()
    
    run_path = Path(args.run_path).resolve()
    
    async with AsyncSessionLocal() as session:
        print(f"Ingesting run from {run_path}...")
        try:
            run = await ingest_federation_run(session, run_path)
            print(f"Successfully ingested training run {run.run_id}")
        except Exception as e:
            print(f"Error ingesting run: {e}")

if __name__ == "__main__":
    asyncio.run(main())

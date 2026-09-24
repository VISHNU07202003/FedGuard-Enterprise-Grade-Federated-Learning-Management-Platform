import os
import subprocess
from pathlib import Path

def download_ton_iot():
    ml_dir = Path(__file__).resolve().parent.parent
    data_dir = ml_dir / "data"
    
    # Check if kaggle is installed
    try:
        import kaggle
    except ImportError:
        print("Kaggle package not found. Installing...")
        subprocess.check_call(["pip", "install", "kaggle"])
        
    print("WARNING: This requires a kaggle.json token in ~/.kaggle/kaggle.json")
    print("If you don't have one, please download the dataset manually from:")
    print("https://www.kaggle.com/datasets/khalednasr/ton-iot-network-dataset")
    print(f"And place Train_Test_Network.csv in {data_dir}")
    print("\nAttempting to download via Kaggle API...")
    
    try:
        # Example dataset identifier for ToN-IoT network
        # The user might need to adjust this depending on the exact Kaggle dataset they want
        dataset_id = "khalednasr/ton-iot-network-dataset" 
        
        subprocess.check_call([
            "kaggle", "datasets", "download", "-d", dataset_id,
            "-p", str(data_dir), "--unzip"
        ])
        print("Download complete!")
    except Exception as e:
        print(f"Failed to download automatically: {e}")
        
if __name__ == "__main__":
    download_ton_iot()

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import numpy as np

# Resolve paths relative to this script
ML_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ML_DIR / "data"
REPORT_JSON = DATA_DIR / "dataset_profile.json"
REPORT_MD = DATA_DIR / "dataset_profile.md"
# Typically ToN-IoT network dataset file is named Train_Test_Network.csv
DATASET_FILE = DATA_DIR / "Train_Test_Network.csv"

def convert_to_serializable(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    return obj

def inspect():
    print(f"Looking for dataset at: {DATASET_FILE}")
    if not DATASET_FILE.exists():
        print(f"ERROR: Dataset not found at {DATASET_FILE}")
        print("Please place Train_Test_Network.csv in the ml/data/ directory.")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATASET_FILE)
    
    # 1. Row counts
    total_rows = len(df)
    
    # Assume 'label' or similar column for normal vs anomaly
    # ToN-IoT usually has 'label' (0/1) and 'type' (attack category)
    label_col = 'label' if 'label' in df.columns else None
    if not label_col and 'Label' in df.columns:
        label_col = 'Label'
        
    type_col = 'type' if 'type' in df.columns else None
    if not type_col and 'Type' in df.columns:
        type_col = 'Type'
    
    normal_rows = 0
    anomaly_rows = 0
    class_distribution = {}
    attack_categories = {}
    
    if label_col:
        value_counts = df[label_col].value_counts().to_dict()
        # Normal is usually 0
        normal_rows = value_counts.get(0, 0)
        anomaly_rows = total_rows - normal_rows
        class_distribution = {str(k): v for k, v in value_counts.items()}
        
    if type_col:
        attack_categories = df[type_col].value_counts().to_dict()
        attack_categories = {str(k): v for k, v in attack_categories.items()}
        
    # 2. Duplicate rows
    duplicate_rows = df.duplicated().sum()

    # 3. Columns & Types
    columns = list(df.columns)
    numerical_cols = list(df.select_dtypes(include=['int64', 'float64']).columns)
    categorical_cols = list(df.select_dtypes(include=['object', 'category']).columns)
    
    # 4. Missing values
    missing_counts = df.isnull().sum().to_dict()
    missing_cols = {k: v for k, v in missing_counts.items() if v > 0}
    
    # Build JSON Profile
    profile = {
        "metadata": {
            "file_name": DATASET_FILE.name,
            "generated_at": datetime.utcnow().isoformat(),
            "file_size_bytes": os.path.getsize(DATASET_FILE)
        },
        "rows": {
            "total": total_rows,
            "normal": normal_rows,
            "anomaly": anomaly_rows,
            "duplicates": duplicate_rows
        },
        "columns": {
            "total_count": len(columns),
            "all": columns,
            "numerical": numerical_cols,
            "categorical": categorical_cols,
            "label_column": label_col,
            "attack_category_column": type_col
        },
        "missing_values": missing_cols,
        "distributions": {
            "binary_label": class_distribution,
            "attack_types": attack_categories
        }
    }
    
    profile = convert_to_serializable(profile)
    
    # Write JSON
    with open(REPORT_JSON, 'w') as f:
        json.dump(profile, f, indent=2)
        
    # Write Markdown
    md_content = f"""# Dataset Inspection Report

**File:** `{DATASET_FILE.name}`
**Generated:** {profile['metadata']['generated_at']}
**Size:** {profile['metadata']['file_size_bytes'] / (1024*1024):.2f} MB

## Row Counts
- **Total Rows:** {total_rows:,}
- **Normal Rows (label=0):** {normal_rows:,}
- **Anomaly Rows (label=1):** {anomaly_rows:,}
- **Duplicate Rows:** {duplicate_rows:,}

## Columns
- **Total Columns:** {len(columns)}
- **Label Column:** `{label_col}`
- **Attack Category Column:** `{type_col}`

### Missing Values
"""
    if missing_cols:
        for col, count in missing_cols.items():
            md_content += f"- `{col}`: {count:,} missing\n"
    else:
        md_content += "- None found.\n"
        
    md_content += "\n### Categorical Columns\n"
    for col in categorical_cols:
        md_content += f"- `{col}`\n"
        
    md_content += "\n### Numerical Columns\n"
    # Show first 15 so it's not too long if there are many
    for col in numerical_cols[:15]:
        md_content += f"- `{col}`\n"
    if len(numerical_cols) > 15:
        md_content += f"- *(and {len(numerical_cols) - 15} more...)*\n"

    md_content += "\n## Class Distribution\n"
    if class_distribution:
        for k, v in class_distribution.items():
            md_content += f"- **Label {k}**: {v:,}\n"
    else:
        md_content += "- Label column not found.\n"
        
    if attack_categories:
        md_content += "\n### Attack Categories\n"
        for k, v in attack_categories.items():
            md_content += f"- **{k}**: {v:,}\n"

    with open(REPORT_MD, 'w') as f:
        f.write(md_content)
        
    print(f"Inspection complete.")
    print(f"JSON Report saved to: {REPORT_JSON}")
    print(f"Markdown Report saved to: {REPORT_MD}")

if __name__ == "__main__":
    inspect()

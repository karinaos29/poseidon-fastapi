import json
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def load_json_state(filepath: str) -> list[dict]:
    path = Path(filepath)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Storage file corrupt or unreadable: {e}. Starting fresh.")
        return []

def append_json_state(filepath: str, reading_dict: dict) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    data = load_json_state(filepath)
    data.append(reading_dict)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_historical_csv(filepath: str) -> pd.DataFrame:

    path = Path(filepath)
    if not path.exists():
        logger.error(f"Historical file missing at {filepath}.")
        return pd.DataFrame()
        
    return pd.read_csv(filepath, dtype_backend="pyarrow")
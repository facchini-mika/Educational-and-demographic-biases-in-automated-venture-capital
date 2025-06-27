"""Thread safe persistor for experiment results."""
from __future__ import annotations
from pathlib import Path
import json, os, tempfile
from filelock import FileLock

# Define paths relative to the current script location
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "Data/Output/data.jsonl"
LOCK_PATH = DATA_PATH.with_suffix(".lock")
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

# Global run_id to track each call
run_id = 0

def save_result(answer: dict, config: dict) -> None:
    """Normalize response and append record to JSONL log."""
    global run_id
    # Increment global run counter
    run_id += 1
    record = make_dict(answer, config)
    log_result(record, DATA_PATH)

def make_dict(answer: dict, config: dict) -> dict:
    """Return normalized result dict for logging."""
    raw_response = answer.get("raw_response", "")
    normalized_answer = {"invest": 0, "amount": 0}  # Default values

    if raw_response:
        try:
            # Attempt to parse "key: value" style raw output
            pairs = [item.strip() for item in raw_response.split(",")]
            for pair in pairs:
                key, value = pair.split(":")
                key = key.strip()
                value = value.strip()

                # Assign parsed values to appropriate fields
                if key == "invest":
                    normalized_answer["invest"] = int(value)
                elif key == "amount":
                    normalized_answer["amount"] = int(value) if normalized_answer["invest"] == 1 else None
        except Exception as e:
            # If parsing fails, record the error message but keep default values
            normalized_answer["error"] = f"Failed to parse raw_response: {e}"
            # Ensure invest and amount keys exist even if parsing fails
            if "invest" not in normalized_answer:
                normalized_answer["invest"] = 0
            if "amount" not in normalized_answer:
                normalized_answer["amount"] = 0

    # Construct the full result entry
    record = {
        "run_id": run_id,
        "model_id": config.get("model_id", 0),
        "repetition": config.get("repetition", 0),
        "gender": config.get("gender", ""),
        "ethnicity": config.get("ethnicity", ""),
        "name": config.get("name", ""),
        "specific_eth": config.get("specific_eth", ""),
        "education": config.get("education", ""),
        "specific_university": config.get("uni_version", ""),
        "invest": normalized_answer["invest"],
        "amount": normalized_answer["amount"],
        "raw_response": raw_response,
        "tokens_input": answer.get("tokens_input", 0),
        "tokens_output": answer.get("tokens_output", 0),
        "timestamp_utc": answer.get("timestamp_utc", ""),
        "request_latency_ms": answer.get("request_latency_ms", 0),
        "error": normalized_answer.get("error", ""),
    }

    return record

def log_result(entry: dict, path: Path = None) -> None:
    """Append single record to JSONL file atomically."""
    if path is None:
        path = DATA_PATH

    # Serialize dict to one JSON line
    line = json.dumps(entry, ensure_ascii=False) + "\n"

    # Use a file lock to prevent concurrent write conflicts
    with FileLock(str(LOCK_PATH)):
        # Write to a temporary file in the same directory
        with tempfile.NamedTemporaryFile("w", dir=DATA_PATH.parent, delete=False, encoding="utf-8") as tmp:
            tmp.write(line)
            tmp.flush()
            os.fsync(tmp.fileno())  # Ensure it's written to disk

        # Atomically append the temp file's content to the target file
        with open(path, "a", encoding="utf-8") as target, \
             open(tmp.name, "r", encoding="utf-8") as src:
            target.writelines(src.readlines())
            target.flush()
            os.fsync(target.fileno())

        # Clean up the temp file
        os.remove(tmp.name)

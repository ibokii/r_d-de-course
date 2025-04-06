import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def get_config() -> dict:
    """
    Reads and parses YAML config file.
    
    Returns:
        dict: Parsed configuration as a Python dictionary.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

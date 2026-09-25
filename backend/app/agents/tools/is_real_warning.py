import re
from datetime import datetime

def is_real_warning(record: dict) -> bool:
    """
    Agent tool to determine if the warning is real based on the provided record.

    Args:
        record (dict): A dictionary containing the warning details.
        
    Returns:
        bool: True if the warning is real, False otherwise.
    """

    # Ensures authorised warnings only per Assessment criteria:  "Never invent or replace official warnings"
    description = record["details"]["description"]
    alert_level = extract_alert_level(description)

    if alert_level in ("Not Applicable", "None"):
        return False
    
    if record.get("status") != "active":
        return False
    
    if datetime.datetime.strptime(record["details"]["expires"], "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
        return False
    
    return True


# Helper function to parse the alert level from the description
def extract_alert_level(desc: str) -> str:
    match = re.search(r"ALERT LEVEL:\s*(.*?)<br", desc)
    if match:
        return match.group(1).strip()
    return None
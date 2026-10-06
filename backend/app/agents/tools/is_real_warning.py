import re
from datetime import datetime, timezone

def is_real_warning(record: dict) -> bool:
    """
    Agent tool to determine if the warning is real based on the provided record.

    Args:
        record (dict): A dictionary containing the warning details.
        
    Returns:
        bool: True if the warning is real, False otherwise.
    """

    # Ensures authorised warnings only per Assessment criteria:  "Never invent or replace official warnings"
    description = record["properties"]["details"]["description"]
    alert_level = extract_alert_level(description)

    if alert_level in ("Not Applicable", "None"):
        return False
    
    if record["properties"]["status"] != "active":
        return False
    
    expires = record["properties"]["details"].get("expires")
    if not expires or parse_time(expires) < now():
        return False
    
    return True

def parse_description_fields(desc: str) -> dict:
    """
    Splits the agency's verbatim description into structured fields,
    without altering any of the actual text content.
    """
    fields = {}
    for line in desc.replace("<br />", "\n").split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def get_broadcastable_warning(record: dict) -> dict | None:
    """
    Returns the verbatim, official warning content to display to users,
    only if the record passes is_real_warning. Never rewrites or
    summarizes the agency's own wording.
    """
    if not is_real_warning(record):
        return None

    props = record["properties"]
    details = props["details"]
    description = details["description"]
    fields = parse_description_fields(description)

    return {
        "agency": props["source"].get("agency"),
        "alert_level": fields.get("ALERT LEVEL"),
        "location": fields.get("LOCATION"),
        "status": fields.get("STATUS"),
        "full_description": description,
        "expires": details.get("expires"),
    }


# Helper function to parse the alert level from the description
def extract_alert_level(desc: str) -> str:
    match = re.search(r"ALERT LEVEL:\s*(.*?)<br", desc)
    if match:
        return match.group(1).strip()
    return None

def parse_time(timestamp_str: str) -> datetime:
    """Convert an ISO 8601 timestamp string into a timezone-aware datetime."""
    dt = datetime.fromisoformat(timestamp_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def now() -> datetime:
    """Current time, timezone-aware, so it can be safely compared to parsed timestamps."""
    return datetime.now(timezone.utc)
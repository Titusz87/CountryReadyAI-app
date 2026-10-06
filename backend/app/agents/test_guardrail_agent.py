# test_agent.py — throwaway script, run separately
from app.agents.guardrail_agent import WarningValidationAgent

good_record = {
    "type": "Feature",
    "properties": {
        "status": "active",
        "warningLevel": "watch_and_act",
        "details": {
            "expires": "2026-09-30T00:00:00+10:00",   # far future, won't be expired
            "description": "ALERT LEVEL: Watch and Act<br />LOCATION: Test Suburb<br />STATUS: Not controlled<br />"
        }
    }
}

agent = WarningValidationAgent()
print(agent.act(good_record))   # should print True
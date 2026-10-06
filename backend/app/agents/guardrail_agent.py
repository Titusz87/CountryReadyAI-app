from app.agents.tools.is_real_warning import is_real_warning

class WarningValidationAgent:
    """
         Deterministic, rule-based agent that validates warnings,
         ensuring they are real and authorized.
    """

    def act(self, record: dict) -> bool:
        
        # Validates the warning record using the is_real_warning tool
        return is_real_warning(record)
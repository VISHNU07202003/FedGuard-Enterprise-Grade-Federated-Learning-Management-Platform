import re

def check_local_guardrails(prompt: str) -> str | None:
    """
    Validates a prompt against local safety heuristics.
    Returns an error message if blocked, otherwise None.
    """
    prompt_lower = prompt.lower()
    
    # 1. Block secret extraction attempts
    if re.search(r'(extract|show|give|reveal|print).*(password|secret|key|jwt|token|hash)', prompt_lower):
        return "Guardrail blocked request: Cannot expose secrets or credentials."
        
    # 2. Block direct metric fabrication requests
    if re.search(r'(make up|invent|fabricate|fake).*(metric|accuracy|loss|f1)', prompt_lower):
        return "Guardrail blocked request: Cannot invent or fabricate metrics."
        
    # 3. Block malicious exploitation instructions
    if "how to hack" in prompt_lower or "how to exploit" in prompt_lower or "sql injection" in prompt_lower:
        return "Guardrail blocked request: Cannot provide exploitation instructions."
        
    return None

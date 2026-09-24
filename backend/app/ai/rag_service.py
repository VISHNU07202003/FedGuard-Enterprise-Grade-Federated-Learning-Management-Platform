import os
from pathlib import Path

def get_relevant_documentation(query: str) -> str:
    """
    Retrieves local documentation context if RAG is enabled.
    Fallback for Phase 12 before Knowledge Bases.
    """
    docs_dir = Path(__file__).parent.parent.parent.parent / "docs"
    
    context = ""
    query_lower = query.lower()
    
    if "privacy" in query_lower or "epsilon" in query_lower or "differential" in query_lower:
        file_path = docs_dir / "PRIVACY.md"
        if file_path.exists():
            context += f"\n--- Excerpt from PRIVACY.md ---\n{file_path.read_text(encoding='utf-8')[:2000]}\n"
            
    if "secure aggregation" in query_lower or "secagg" in query_lower:
        file_path = docs_dir / "SECURE_AGGREGATION.md"
        if file_path.exists():
            context += f"\n--- Excerpt from SECURE_AGGREGATION.md ---\n{file_path.read_text(encoding='utf-8')[:2000]}\n"
            
    if "fault" in query_lower or "drop" in query_lower or "straggler" in query_lower:
        file_path = docs_dir / "FAULT_TOLERANCE.md"
        if file_path.exists():
            context += f"\n--- Excerpt from FAULT_TOLERANCE.md ---\n{file_path.read_text(encoding='utf-8')[:2000]}\n"
            
    return context
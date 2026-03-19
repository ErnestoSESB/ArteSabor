import re

def strip_tags(value: str) -> str:
    """Remove todas as tags HTML de uma string."""
    if not isinstance(value, str):
        return value
    return re.sub(r'<[^>]+>', '', value).strip()

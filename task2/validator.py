from pathlib import Path
import re
import yaml


def load_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content. Returns empty dict if none."""
    if not content.startswith("---"):
        return {}
    # Find closing ---
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = content[3:end].strip()
    try:
        result = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML frontmatter: {e}") from e
    return result if isinstance(result, dict) else {}


REQUIRED_FIELDS = ["name", "description", "version", "inputs", "outputs"]


def check_required_fields(fm: dict) -> list[str]:
    """Return list of error strings for missing required fields."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required field: '{field}'")
    return errors


# Patterns that indicate a raw token or Authorization header is embedded
_UNSAFE_PATTERNS = [
    re.compile(r"Authorization\s*:\s*Bearer", re.IGNORECASE),
    re.compile(r"Authorization\s*:\s*Token", re.IGNORECASE),
]


def check_safe_boundary(content: str) -> list[str]:
    """Return warnings if the skill content contains unsafe credential patterns."""
    warnings = []
    for pattern in _UNSAFE_PATTERNS:
        if pattern.search(content):
            warnings.append(
                f"Unsafe pattern detected ('{pattern.pattern}'): "
                "do not embed tokens or Authorization headers in skill files"
            )
    return warnings


def validate_skill(path: Path) -> list[str]:
    """Run all checks on a skill file. Returns combined list of errors/warnings."""
    content = path.read_text()
    errors = []
    try:
        fm = load_frontmatter(content)
    except ValueError as e:
        return [str(e)]
    errors.extend(check_required_fields(fm))
    errors.extend(check_safe_boundary(content))
    return errors

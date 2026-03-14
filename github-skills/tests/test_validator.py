from pathlib import Path
import pytest
from validator import load_frontmatter, check_required_fields, check_safe_boundary, validate_skill

FIXTURES = Path(__file__).parent / "fixtures"


# --- load_frontmatter ---

def test_load_frontmatter_valid():
    content = (FIXTURES / "valid_skill.md").read_text()
    fm = load_frontmatter(content)
    assert fm["name"] == "gh-lint"
    assert fm["version"] == "1.0"
    assert isinstance(fm["inputs"], list)


def test_load_frontmatter_no_frontmatter():
    content = (FIXTURES / "invalid_skill.md").read_text()
    fm = load_frontmatter(content)
    assert fm == {}


def test_load_frontmatter_malformed_yaml():
    content = "---\nname: [unclosed\n---\n"
    with pytest.raises(ValueError):
        load_frontmatter(content)


# --- check_required_fields ---

def test_check_required_fields_all_present():
    fm = {
        "name": "gh-lint",
        "description": "desc",
        "version": "1.0",
        "inputs": [{"repo": "owner/name"}],
        "outputs": [{"conclusion": "success | failure"}],
    }
    assert check_required_fields(fm) == []


def test_check_required_fields_missing_name():
    fm = {
        "description": "desc",
        "version": "1.0",
        "inputs": [],
        "outputs": [],
    }
    errors = check_required_fields(fm)
    assert any("name" in e for e in errors)


def test_check_required_fields_missing_inputs_outputs():
    fm = {"name": "x", "description": "d", "version": "1.0"}
    errors = check_required_fields(fm)
    assert any("inputs" in e for e in errors)
    assert any("outputs" in e for e in errors)


# --- check_safe_boundary ---

def test_check_safe_boundary_token_warning():
    body = "Authorization: Bearer $TOKEN\nsome other text"
    warnings = check_safe_boundary(body)
    assert len(warnings) > 0


def test_check_safe_boundary_clean():
    body = "Run `gh workflow run lint.yml --repo owner/repo`"
    warnings = check_safe_boundary(body)
    assert warnings == []


# --- validate_skill (integration of above) ---

def test_validate_skill_valid_file():
    errors = validate_skill(FIXTURES / "valid_skill.md")
    assert errors == []


def test_validate_skill_invalid_file():
    errors = validate_skill(FIXTURES / "invalid_skill.md")
    assert len(errors) > 0


# --- all skill files pass validate_skill ---

def test_all_skills_valid():
    skills_dir = Path(__file__).parent.parent / "skills"
    skill_files = list(skills_dir.glob("*.md"))
    assert len(skill_files) > 0, "No skill files found"
    for skill_path in skill_files:
        errors = validate_skill(skill_path)
        assert errors == [], f"{skill_path.name} has errors: {errors}"

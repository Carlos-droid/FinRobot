import pytest
import re
from finrobot.data_source.filings_src.sec_filings import get_regex_enum

def test_get_regex_enum_valid_pattern():
    regex_str = r"^Item \d+"
    enum_member = get_regex_enum(regex_str)

    # Check if the returned object has the pattern property and it matches
    assert hasattr(enum_member, "pattern")
    assert enum_member.pattern == re.compile(regex_str)

    # Check if the pattern works with re module
    assert enum_member.pattern.match("Item 1") is not None
    assert enum_member.pattern.match("Other Item") is None

def test_get_regex_enum_invalid_pattern():
    # Should raise re.error on invalid regex compilation
    with pytest.raises(re.error):
        get_regex_enum(r"[")

def test_get_regex_enum_empty_string():
    # Empty string should compile to an empty regex pattern
    enum_member = get_regex_enum("")
    assert enum_member.pattern == re.compile("")
    assert enum_member.pattern.match("anything") is not None

def test_get_regex_enum_none_input():
    # re.compile(None) raises TypeError
    with pytest.raises(TypeError):
        get_regex_enum(None)

def test_get_regex_enum_dynamic_class_creation():
    # Verify that each call creates a new Enum class, even for the same regex
    regex_str = "test"
    enum1 = get_regex_enum(regex_str)
    enum2 = get_regex_enum(regex_str)

    # Their patterns should be identical
    assert enum1.pattern == enum2.pattern

    # But they belong to different dynamically created classes
    assert type(enum1) is not type(enum2)
    assert enum1 is not enum2

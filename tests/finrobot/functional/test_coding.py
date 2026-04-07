import os
import pytest
from pathlib import Path
from finrobot.functional.coding import CodingUtils, _get_safe_path, default_path

def setup_module(module):
    os.makedirs(default_path, exist_ok=True)

def test_get_safe_path():
    base = Path(default_path).resolve()

    # Valid paths
    res1 = _get_safe_path(default_path, "test.txt")
    assert isinstance(res1, Path)
    assert res1 == base / "test.txt"

    res2 = _get_safe_path(default_path, "sub/dir/test.txt")
    assert isinstance(res2, Path)
    assert res2 == base / "sub" / "dir" / "test.txt"

    # Path traversals
    with pytest.raises(ValueError, match=r"Acceso denegado.*"):
        _get_safe_path(default_path, "../test.txt")
    with pytest.raises(ValueError, match=r"Acceso denegado.*"):
        _get_safe_path(default_path, "../../etc/passwd")
    with pytest.raises(ValueError, match=r"Acceso denegado.*"):
        _get_safe_path(default_path, "/etc/passwd")

def test_get_safe_path_fallback():
    from unittest.mock import patch
    base = Path(default_path).resolve()

    # Test valid path via the fallback logic
    with patch("pathlib.Path.is_relative_to", side_effect=AttributeError):
        res1 = _get_safe_path(default_path, "test.txt")
        assert isinstance(res1, Path)
        assert res1 == base / "test.txt"

    # Test path traversal via the fallback logic
    with patch("pathlib.Path.is_relative_to", side_effect=AttributeError):
        with pytest.raises(ValueError, match=r"Acceso denegado.*"):
            _get_safe_path(default_path, "../test.txt")
        with pytest.raises(ValueError, match=r"Acceso denegado.*"):
            _get_safe_path(default_path, "../../etc/passwd")
        with pytest.raises(ValueError, match=r"Acceso denegado.*"):
            _get_safe_path(default_path, "/etc/passwd")

def test_create_file_with_code():
    res = CodingUtils.create_file_with_code("test_create.txt", "hello")
    assert res == "File created successfully"
    assert os.path.exists(os.path.join(default_path, "test_create.txt"))

    res_err = CodingUtils.create_file_with_code("../out.txt", "hacked")
    assert isinstance(res_err, str)
    assert res_err.startswith("Error: Acceso denegado")
    assert not os.path.exists("out.txt")

def test_list_dir():
    # It should work for the root (represented by "" or ".")
    res = CodingUtils.list_dir(".")
    assert "test_create.txt" in res

    res_err = CodingUtils.list_dir("../")
    assert isinstance(res_err, str)
    assert res_err.startswith("Error: Acceso denegado")

def test_see_file():
    CodingUtils.create_file_with_code("see.txt", "line1\nline2")
    res = CodingUtils.see_file("see.txt")
    assert "1:line1" in res
    assert "2:line2" in res

    res_err = CodingUtils.see_file("../test.txt")
    assert isinstance(res_err, str)
    assert res_err.startswith("Error: Acceso denegado")

def test_modify_code():
    CodingUtils.create_file_with_code("mod.txt", "A\nB\nC\n")
    CodingUtils.modify_code("mod.txt", 2, 2, "X")
    res = CodingUtils.see_file("mod.txt")
    assert "2:X" in res

    res_err = CodingUtils.modify_code("../mod.txt", 1, 1, "hacked")
    assert isinstance(res_err, str)
    assert res_err.startswith("Error: Acceso denegado")

def teardown_module(module):
    # Cleanup
    for f in ["test_create.txt", "see.txt", "mod.txt"]:
        path = os.path.join(default_path, f)
        if os.path.exists(path):
            os.remove(path)

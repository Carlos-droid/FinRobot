import os
import pytest
from finrobot.functional.coding import CodingUtils, _get_safe_path, default_path

def setup_module(module):
    os.makedirs(default_path, exist_ok=True)

def test_get_safe_path():
    base = os.path.abspath(default_path)

    # Valid paths
    assert _get_safe_path(default_path, "test.txt") == os.path.join(base, "test.txt")
    assert _get_safe_path(default_path, "sub/dir/test.txt") == os.path.join(base, "sub", "dir", "test.txt")

    # Path traversals
    with pytest.raises(ValueError, match="Path traversal detected"):
        _get_safe_path(default_path, "../test.txt")
    with pytest.raises(ValueError, match="Path traversal detected"):
        _get_safe_path(default_path, "../../etc/passwd")

def test_create_file_with_code():
    res = CodingUtils.create_file_with_code("test_create.txt", "hello")
    assert res == "File created successfully"
    assert os.path.exists(os.path.join(default_path, "test_create.txt"))

    with pytest.raises(ValueError, match="Path traversal detected"):
        CodingUtils.create_file_with_code("../out.txt", "hacked")
    assert not os.path.exists("out.txt")

def test_list_dir():
    # It should work for the root (represented by "" or ".")
    res = CodingUtils.list_dir(".")
    assert "test_create.txt" in res

    with pytest.raises(ValueError, match="Path traversal detected"):
        CodingUtils.list_dir("../")

def test_see_file():
    CodingUtils.create_file_with_code("see.txt", "line1\nline2")
    res = CodingUtils.see_file("see.txt")
    assert "1:line1" in res
    assert "2:line2" in res

    with pytest.raises(ValueError, match="Path traversal detected"):
        CodingUtils.see_file("../test.txt")

def test_modify_code():
    CodingUtils.create_file_with_code("mod.txt", "A\nB\nC\n")
    CodingUtils.modify_code("mod.txt", 2, 2, "X")
    res = CodingUtils.see_file("mod.txt")
    assert "2:X" in res

    with pytest.raises(ValueError, match="Path traversal detected"):
        CodingUtils.modify_code("../mod.txt", 1, 1, "hacked")

def teardown_module(module):
    # Cleanup
    for f in ["test_create.txt", "see.txt", "mod.txt"]:
        path = os.path.join(default_path, f)
        if os.path.exists(path):
            os.remove(path)

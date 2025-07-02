#!/usr/bin/env python3
"""
Simple standalone test that doesn't require conftest.py
"""

import pytest


def test_basic_math():
    """Test basic mathematical operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5


def test_string_operations():
    """Test basic string operations."""
    assert "hello".upper() == "HELLO"
    assert "WORLD".lower() == "world"
    assert len("test") == 4


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1
    assert 2 in test_list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

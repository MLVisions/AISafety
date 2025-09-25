"""
Test configuration and fixtures for AI Safety website tests
"""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content with frontmatter for testing"""
    return """---
title: "Test Page"
tagline: "Test tagline"
description: "Test description"
---

# Test Content

This is a test page with some **bold** text and *italic* text.

## Section 2

Here's a paragraph with a [link](http://example.com).

![Test Image](images/test.png)
"""


@pytest.fixture
def sample_csv_data() -> str:
    """Sample CSV data for plot testing"""
    return """Date,SP500,Bitcoin
2020-01-01,3230.78,7200.17
2020-06-01,3041.31,9483.21
2021-01-01,3756.07,29391.78
2021-06-01,4204.11,35041.88
2022-01-01,4766.18,46306.45
2022-06-01,3785.38,31718.56
2023-01-01,3839.50,16547.50
2023-06-01,4450.38,30513.95
2024-01-01,4769.83,42278.50
2024-06-01,5432.12,65432.10
"""


@pytest.fixture
def sample_portfolio_data() -> str:
    """Sample portfolio CSV data for testing"""
    return """Date,Portfolio_Value
2020-01-01,100000
2021-01-01,125000
2022-01-01,110000
2023-01-01,140000
2024-01-01,165000
2025-01-01,185000
"""

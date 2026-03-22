"""
File operation utilities for the agent system.
Provides safe file handling, backup, and markdown processing functions.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def safe_write_file(
    filepath: str | Path,
    content: str,
    backup: bool = True,
    encoding: str = 'utf-8'
) -> bool:
    """
    Safely write content to a file with optional backup

    Args:
        filepath: Path to the file to write
        content: Content to write
        backup: Whether to create a backup of existing file
        encoding: File encoding to use

    Returns:
        True if successful, False otherwise
    """
    filepath = Path(filepath)

    try:
        # Create backup if requested and file exists
        if backup and filepath.exists():
            backup_file(str(filepath))

        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)

        return True

    except OSError as e:
        print(f"Error writing file {filepath}: {e}")
        return False


def backup_file(filepath: str | Path) -> str | None:
    """
    Create a backup of a file in the project-level backups/ directory.

    Args:
        filepath: Path to the file to backup

    Returns:
        Path to backup file if successful, None otherwise
    """
    original_path = Path(filepath)

    if not original_path.exists():
        return None

    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{original_path.stem}_{timestamp}{original_path.suffix}"
        backup_path = backup_dir / backup_name

        shutil.copy2(original_path, backup_path)
        return str(backup_path)

    except OSError as e:
        print(f"Error creating backup of {filepath}: {e}")
        return None


def read_markdown_file(filepath: str | Path) -> tuple[dict[str, Any], str]:
    """
    Read a markdown file and separate frontmatter from content

    Args:
        filepath: Path to the markdown file

    Returns:
        Tuple of (frontmatter_dict, markdown_content)
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        # Check if file has frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    markdown_content = parts[2].strip()
                    return frontmatter or {}, markdown_content
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML frontmatter in {filepath}: {e}")
                    return {}, content

        # No frontmatter found
        return {}, content

    except OSError as e:
        raise OSError(f"Error reading file {filepath}: {e}") from e


def write_markdown_file(
    filepath: str | Path,
    content: str,
    frontmatter: dict[str, Any] | None = None,
    backup: bool = True
) -> bool:
    """
    Write a markdown file with optional frontmatter

    Args:
        filepath: Path to write the file
        content: Markdown content
        frontmatter: Optional frontmatter dictionary
        backup: Whether to backup existing file

    Returns:
        True if successful, False otherwise
    """
    output_lines = []

    if frontmatter:
        output_lines.append('---')
        output_lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
        output_lines.append('---')
        output_lines.append('')

    output_lines.append(content)

    full_content = '\n'.join(output_lines)
    return safe_write_file(filepath, full_content, backup=backup)


def ensure_directory(dirpath: str | Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary

    Args:
        dirpath: Path to the directory

    Returns:
        True if directory exists/was created, False on error
    """
    try:
        Path(dirpath).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory {dirpath}: {e}")
        return False


def list_content_files(content_dir: str | Path = "src/content") -> list[str]:
    """
    List canonical markdown files in the content directory.

    Excludes timestamped backup files (e.g. references_20260310_004056.md)
    that may linger in the content directory.

    Args:
        content_dir: Path to content directory

    Returns:
        List of markdown file paths
    """
    import re

    content_path = Path(content_dir)

    if not content_path.exists():
        return []

    # Exclude files with timestamp suffixes like _20260310_004056
    timestamp_pattern = re.compile(r"_\d{8}_\d{6}$")
    return [
        str(f)
        for f in content_path.glob("*.md")
        if not timestamp_pattern.search(f.stem)
    ]


def get_file_info(filepath: str | Path) -> dict[str, Any]:
    """
    Get information about a file

    Args:
        filepath: Path to the file

    Returns:
        Dictionary with file information
    """
    filepath = Path(filepath)

    if not filepath.exists():
        return {"exists": False}

    stat = filepath.stat()

    return {
        "exists": True,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "is_file": filepath.is_file(),
        "is_dir": filepath.is_dir(),
        "extension": filepath.suffix
    }

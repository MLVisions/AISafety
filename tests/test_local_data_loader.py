"""
Unit tests for the local data loader.
"""

import base64

import pytest

from agents.utils.local_data_loader import LocalAttachment, load_local_files


class TestLoadLocalFiles:
    """Tests for load_local_files function."""

    def test_load_pdf(self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch) -> None:
        """PDF files should be loaded as document attachments."""
        pdf_content = b"%PDF-1.4 fake content"
        (tmp_path / "test.pdf").write_bytes(pdf_content)
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["test.pdf"])

        assert len(result) == 1
        assert result[0].kind == "document"
        assert result[0].mime == "application/pdf"
        assert result[0].filename == "test.pdf"
        assert base64.b64decode(result[0].data) == pdf_content

    def test_load_png(self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch) -> None:
        """PNG files should be loaded as image attachments."""
        png_content = b"\x89PNG\r\n\x1a\n fake"
        (tmp_path / "chart.png").write_bytes(png_content)
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["chart.png"])

        assert len(result) == 1
        assert result[0].kind == "image"
        assert "image/" in result[0].mime
        assert base64.b64decode(result[0].data) == png_content

    def test_unsupported_format_skipped(
        self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PPTX/DOCX files should be skipped with a warning."""
        (tmp_path / "slides.pptx").write_bytes(b"fake pptx")
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["slides.pptx"])

        assert len(result) == 0

    def test_missing_file_skipped(
        self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing files should be skipped with a warning."""
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["nonexistent.pdf"])

        assert len(result) == 0

    def test_mixed_files(
        self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Mix of valid, unsupported, and missing files."""
        (tmp_path / "doc.pdf").write_bytes(b"%PDF-1.4")
        (tmp_path / "img.png").write_bytes(b"\x89PNG")
        (tmp_path / "slides.pptx").write_bytes(b"pptx")
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["doc.pdf", "img.png", "slides.pptx", "gone.pdf"])

        assert len(result) == 2
        kinds = {a.kind for a in result}
        assert kinds == {"document", "image"}

    def test_unknown_extension_skipped(
        self, tmp_path: "pytest.TempPathFactory", monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Files with unknown extensions should be skipped."""
        (tmp_path / "data.xyz").write_bytes(b"unknown")
        monkeypatch.setattr(
            "agents.utils.local_data_loader.LOCAL_DATA_DIR", tmp_path
        )

        result = load_local_files(["data.xyz"])

        assert len(result) == 0

    def test_empty_list(self) -> None:
        """Empty input should return empty output."""
        result = load_local_files([])
        assert result == []


class TestLocalAttachment:
    """Tests for LocalAttachment dataclass."""

    def test_fields(self) -> None:
        att = LocalAttachment(kind="document", mime="application/pdf", data="abc", filename="test.pdf")
        assert att.kind == "document"
        assert att.mime == "application/pdf"
        assert att.data == "abc"
        assert att.filename == "test.pdf"

"""
Tests for the plot generator module - Core functionality only
"""

import matplotlib
import pytest

matplotlib.use('Agg')  # Use non-interactive backend for testing
# Add src to path for imports
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from builders.plot_generator import create_market_trends_plot, setup_plot_style


class TestPlotGenerator:
    """Test core plot generator functionality"""

    def test_setup_plot_style(self):
        """Test plot style configuration"""
        setup_plot_style()

        # Check that key styles were applied
        assert plt.rcParams['figure.facecolor'] == 'white'
        assert plt.rcParams['axes.facecolor'] == 'white'
        assert not plt.rcParams['axes.spines.top']
        assert not plt.rcParams['axes.spines.right']

    def test_create_market_trends_plot(self, temp_dir, sample_csv_data):
        """Test market trends plot creation"""
        # Create test CSV file
        csv_file = temp_dir / "market_trends.csv"
        csv_file.write_text(sample_csv_data)

        # Create output path
        output_file = temp_dir / "market_trends.png"

        # Generate plot (should not raise exception)
        create_market_trends_plot(str(csv_file), str(output_file))

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_error_handling_missing_csv(self, temp_dir):
        """Test error handling when CSV file is missing"""
        output_file = temp_dir / "test.png"

        with pytest.raises(FileNotFoundError):
            create_market_trends_plot("nonexistent.csv", str(output_file))

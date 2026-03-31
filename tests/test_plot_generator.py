"""
Tests for the plot generator module - Core functionality only
"""

import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend for testing

import matplotlib.pyplot as plt

from agents.utils.constants import setup_plot_style


class TestPlotGenerator:
    """Test core plot generator functionality"""

    def test_setup_plot_style(self) -> None:
        """Test plot style configuration"""
        setup_plot_style()

        # Check that key styles were applied
        assert plt.rcParams['figure.facecolor'] == 'white'
        assert plt.rcParams['axes.facecolor'] == 'white'
        assert not plt.rcParams['axes.spines.top']
        assert not plt.rcParams['axes.spines.right']

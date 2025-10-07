"""
Test cases for the investment strategy pipeline agents
Tests for economic models, portfolio simulation, and historical data analysis
"""

from typing import Any
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.agents.utils.data_sources import (
    DEFAULT_TICKERS,
    analyze_data_availability,
    get_supported_tickers,
)
from src.agents.utils.economic_models import (
    MonteCarloPortfolioSimulator,
    create_default_investment_scenarios,
)
from src.agents.utils.historical_visualization import HistoricalDataVisualizationAgent
from src.agents.utils.portfolio_simulation import PortfolioSimulationAgent


class TestEconomicModels:
    """Test cases for Monte Carlo portfolio simulation"""

    def test_monte_carlo_initialization(self) -> None:
        """Test Monte Carlo simulator initialization"""
        simulator = MonteCarloPortfolioSimulator(random_seed=42)

        assert simulator.asset_params == {}
        assert simulator.correlation_matrix is None
        assert not simulator.is_calibrated

    def test_create_default_scenarios(self) -> None:
        """Test default investment scenario creation"""
        scenarios = create_default_investment_scenarios()

        assert 'PersonA' in scenarios
        assert 'PersonB' in scenarios
        assert 'PersonC' in scenarios

        # Check that weights sum to 1.0 for each scenario
        for scenario_name, weights in scenarios.items():
            total_weight = sum(weights.values())
            assert abs(total_weight - 1.0) < 1e-6, f"{scenario_name} weights don't sum to 1.0"

    def test_calibration_with_mock_data(self) -> None:
        """Test model calibration with mock price data"""
        simulator = MonteCarloPortfolioSimulator(random_seed=42)

        # Create mock price data
        dates = pd.date_range('2020-01-01', '2023-01-01', freq='D')
        mock_data = {
            'ASSET1': pd.DataFrame({
                'Close': np.random.lognormal(0, 0.02, len(dates))
            }),
            'ASSET2': pd.DataFrame({
                'Close': np.random.lognormal(0, 0.03, len(dates))
            })
        }

        # Calibrate
        simulator.calibrate_from_data(mock_data)

        assert simulator.is_calibrated
        assert len(simulator.asset_params) == 2
        assert 'ASSET1' in simulator.asset_params
        assert 'ASSET2' in simulator.asset_params

        # Check parameter structure
        for _asset, params in simulator.asset_params.items():
            assert 'mu' in params  # Expected return
            assert 'sigma' in params  # Volatility
            assert 'current_price' in params

    def test_portfolio_simulation_basic(self) -> None:
        """Test basic portfolio simulation functionality"""
        simulator = MonteCarloPortfolioSimulator(random_seed=42)

        # Create mock data and calibrate
        dates = pd.date_range('2020-01-01', '2023-01-01', freq='D')
        mock_data = {
            'ASSET1': pd.DataFrame({
                'Close': 100 * np.exp(np.cumsum(np.random.normal(0.0008, 0.02, len(dates))))
            }),
            'ASSET2': pd.DataFrame({
                'Close': 50 * np.exp(np.cumsum(np.random.normal(0.0005, 0.015, len(dates))))
            })
        }

        simulator.calibrate_from_data(mock_data)

        # Run simulation with simple portfolio
        weights = {'ASSET1': 0.6, 'ASSET2': 0.4}
        result = simulator.simulate_portfolio(
            weights=weights,
            initial_value=100000,
            num_simulations=100,
            time_horizon_years=1
        )

        # Check result structure
        assert 'portfolio_paths' in result
        assert 'final_values' in result
        assert 'mean_final_value' in result
        assert 'confidence_intervals' in result

        # Check dimensions
        assert result['portfolio_paths'].shape[0] == 100  # num_simulations
        assert len(result['final_values']) == 100

        # Check confidence intervals
        assert 5 in result['confidence_intervals']
        assert 95 in result['confidence_intervals']


class TestHistoricalDataVisualization:
    """Test cases for historical data visualization agent"""

    def test_agent_initialization(self) -> None:
        """Test visualization agent initialization"""
        agent = HistoricalDataVisualizationAgent()

        assert agent.output_dir.exists()
        assert agent.historical_data == {}
        assert agent.data_summaries == {}

    def test_display_name_mapping(self) -> None:
        """Test ticker display name mapping"""
        agent = HistoricalDataVisualizationAgent()

        assert agent._get_display_name('^GSPC') == 'S&P 500'
        assert agent._get_display_name('BTC-USD') == 'Bitcoin'
        assert agent._get_display_name('UNKNOWN') == 'UNKNOWN'

    def test_dropdown_data_structure(self) -> None:
        """Test dropdown data generation structure"""
        agent = HistoricalDataVisualizationAgent()

        # Mock some historical data
        agent.historical_data = {
            'equity': {
                '^GSPC': pd.DataFrame({
                    'Date': pd.date_range('2020-01-01', '2023-01-01', freq='D'),
                    'Close': np.random.uniform(3000, 4000, 1097)
                })
            }
        }

        agent.data_summaries = {
            'equity': {
                '^GSPC': {
                    'start_date': '2020-01-01',
                    'end_date': '2023-01-01',
                    'years_of_data': 3.0,
                    'data_points': 1097
                }
            }
        }

        dropdown_data = agent.generate_dropdown_data()

        assert 'asset_classes' in dropdown_data
        assert 'metadata' in dropdown_data
        assert 'equity' in dropdown_data['asset_classes']
        assert '^GSPC' in dropdown_data['asset_classes']['equity']['assets']


class TestPortfolioSimulationAgent:
    """Test cases for portfolio simulation agent"""

    def test_agent_initialization(self) -> None:
        """Test portfolio simulation agent initialization"""
        agent = PortfolioSimulationAgent()

        assert agent.output_dir.exists()
        assert isinstance(agent.simulator, MonteCarloPortfolioSimulator)
        assert isinstance(agent.viz_agent, HistoricalDataVisualizationAgent)

    @patch('src.agents.utils.portfolio_simulation.fetch_market_data')
    def test_csv_data_generation(self, mock_fetch: Any) -> None:
        """Test CSV data generation for website"""
        # Mock market data for all assets needed by default scenarios
        default_scenarios = create_default_investment_scenarios()
        all_assets: set[str] = set()
        for scenario in default_scenarios.values():
            all_assets.update(scenario.keys())

        mock_data = {}
        for asset in all_assets:
            mock_data[asset] = pd.DataFrame({
                'Close': 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.015, 1000)))
            })

        mock_fetch.return_value = mock_data

        agent = PortfolioSimulationAgent()
        agent.calibrate_simulation_models()

        csv_data = agent.generate_website_csv_data(time_horizon=3)

        # Check structure
        assert 'Month' in csv_data.columns  # Updated to monthly data
        assert 'PersonA_Total' in csv_data.columns
        assert 'PersonB_Total' in csv_data.columns
        assert 'PersonC_Total' in csv_data.columns

        # Check that we have the right number of months (3 years * 12 months + 1 initial)
        assert len(csv_data) == 37  # 2025-01 to 2028-01 for 3-year simulation


class TestDataSources:
    """Test cases for data sources utilities"""

    def test_default_tickers_structure(self) -> None:
        """Test default tickers dictionary structure"""
        tickers = get_supported_tickers()

        expected_categories = ['equity', 'international', 'crypto', 'commodities', 'real_estate', 'bonds']

        for category in expected_categories:
            assert category in tickers
            assert isinstance(tickers[category], list)
            assert len(tickers[category]) > 0

    def test_ticker_coverage(self) -> None:
        """Test that we have good coverage across asset classes"""
        tickers = get_supported_tickers()

        # Check minimum coverage
        assert len(tickers['equity']) >= 10  # Good equity coverage
        assert len(tickers['crypto']) >= 4   # Major crypto assets
        assert len(tickers['commodities']) >= 5  # Key commodities
        assert len(tickers['real_estate']) >= 3  # REIT coverage
        assert len(tickers['bonds']) >= 5    # Bond variety

    def test_analyze_data_availability_structure(self) -> None:
        """Test data availability analysis structure"""
        # Test with a known ticker
        result = analyze_data_availability('^GSPC')

        expected_keys = ['ticker', 'available', 'start_date', 'end_date',
                        'total_days', 'total_years', 'data_points', 'frequency']

        if result['available']:
            for key in expected_keys:
                assert key in result
        else:
            assert 'error' in result


class TestInvestmentPipeline:
    """Integration tests for the complete investment pipeline"""

    @patch('src.agents.utils.data_sources.fetch_market_data')
    def test_pipeline_integration(self, mock_fetch: Any) -> None:
        """Test end-to-end pipeline integration"""
        # Mock market data for key assets
        mock_data = {}
        for _category, tickers in DEFAULT_TICKERS.items():
            for ticker in tickers[:2]:  # Limit to 2 per category for speed
                mock_data[ticker] = pd.DataFrame({
                    'Date': pd.date_range('2020-01-01', '2023-01-01', freq='D'),
                    'Close': 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.015, 1097)))
                })

        mock_fetch.return_value = mock_data

        # Test portfolio simulation agent
        agent = PortfolioSimulationAgent()
        agent.calibrate_simulation_models()

        # Test simulation
        results = agent.run_portfolio_simulation(time_horizon=2)

        assert 'time_horizon' in results
        assert 'scenarios' in results
        assert len(results['scenarios']) == 3  # PersonA, PersonB, PersonC

        # Test CSV generation
        csv_data = agent.generate_website_csv_data(time_horizon=2)
        assert not csv_data.empty
        assert len(csv_data) == 25  # 2025-01 to 2027-01 for 2-year simulation (monthly data)


@pytest.fixture
def sample_price_data() -> dict[str, pd.DataFrame]:
    """Fixture providing sample price data for testing"""
    dates = pd.date_range('2020-01-01', '2023-01-01', freq='D')
    return {
        'STOCK_A': pd.DataFrame({
            'Date': dates,
            'Close': 100 * np.exp(np.cumsum(np.random.normal(0.0008, 0.02, len(dates))))
        }),
        'STOCK_B': pd.DataFrame({
            'Date': dates,
            'Close': 50 * np.exp(np.cumsum(np.random.normal(0.0005, 0.015, len(dates))))
        })
    }


class TestRiskMetrics:
    """Test cases for risk calculation and analysis"""

    def test_confidence_intervals(self, sample_price_data: dict[str, pd.DataFrame]) -> None:
        """Test confidence interval calculations"""
        simulator = MonteCarloPortfolioSimulator(random_seed=42)
        simulator.calibrate_from_data(sample_price_data)

        result = simulator.simulate_portfolio(
            weights={'STOCK_A': 0.7, 'STOCK_B': 0.3},
            initial_value=100000,
            num_simulations=1000,
            time_horizon_years=1
        )

        # Check confidence intervals are ordered correctly
        intervals = result['confidence_intervals']
        assert intervals[5] <= intervals[25] <= intervals[50] <= intervals[75] <= intervals[95]

        # Check they're reasonable relative to mean
        mean_value = result['mean_final_value']
        assert intervals[25] < mean_value < intervals[75]

    def test_success_probability(self, sample_price_data: dict[str, pd.DataFrame]) -> None:
        """Test success probability calculation"""
        simulator = MonteCarloPortfolioSimulator(random_seed=42)
        simulator.calibrate_from_data(sample_price_data)

        result = simulator.simulate_portfolio(
            weights={'STOCK_A': 0.5, 'STOCK_B': 0.5},
            initial_value=100000,
            num_simulations=1000,
            time_horizon_years=1
        )

        success_prob = result['success_probability']
        assert 0 <= success_prob <= 1
        # With positive expected returns, should have good success probability
        assert success_prob > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

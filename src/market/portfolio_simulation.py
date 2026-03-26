"""
Portfolio Simulation Agent
Combines trend analysis, economic models, and investment allocation to generate
PersonA/B/C portfolio simulations with confidence intervals
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .data_sources import fetch_market_data
from .economic_models import (
    MonteCarloPortfolioSimulator,
    create_default_investment_scenarios,
)
from .historical_visualization import HistoricalDataVisualizationAgent


class PortfolioSimulationAgent:
    """
    Agent that orchestrates the complete investment simulation pipeline:
    1. Analyzes historical trends
    2. Applies economic models
    3. Generates PersonA/B/C portfolio simulations
    4. Creates CSV data for website integration
    """

    def __init__(self, output_dir: str = "src/data", random_seed: int | None = 42):
        """
        Initialize the portfolio simulation agent

        Args:
            output_dir: Directory to save simulation outputs
            random_seed: Random seed for reproducible results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.simulator = MonteCarloPortfolioSimulator(random_seed=random_seed)
        self.viz_agent = HistoricalDataVisualizationAgent()

        self.historical_data: dict[str, dict[str, pd.DataFrame]] = {}
        self.trend_analysis: dict[str, dict[str, Any]] = {}
        self.simulation_results: dict[str, Any] = {}

    def calibrate_simulation_models(self, force_refresh: bool = False) -> None:
        """
        Calibrate all simulation models with historical data

        Args:
            force_refresh: Whether to force refresh historical data
        """
        print("Calibrating simulation models with historical data...")

        # Get comprehensive historical data
        if not self.historical_data or force_refresh:
            self.historical_data = self.viz_agent.fetch_all_historical_data(force_refresh)

        # Prepare data for Monte Carlo calibration
        calibration_data = {}

        # Collect all assets that will be used in portfolios
        all_portfolio_assets: set[str] = set()
        default_scenarios = create_default_investment_scenarios()
        for scenario_weights in default_scenarios.values():
            all_portfolio_assets.update(scenario_weights.keys())

        # Get recent data (2-5 years) for calibration to avoid stale parameters
        print("Fetching recent data for calibration...")
        recent_data = fetch_market_data(list(all_portfolio_assets), period='5y')

        for asset, df in recent_data.items():
            if not df.empty and 'Close' in df.columns:
                calibration_data[asset] = df

        # Calibrate Monte Carlo simulator
        self.simulator.calibrate_from_data(calibration_data)

        # Run trend analysis
        self.trend_analysis = self.viz_agent.analyze_trends()

        print(f"Calibrated models for {len(calibration_data)} assets")

    def run_portfolio_simulation(self, time_horizon: int = 5) -> dict[str, Any]:
        """
        Run portfolio simulation for PersonA/B/C scenarios

        Args:
            time_horizon: Years to simulate

        Returns:
            Simulation results
        """
        print(f"Running {time_horizon}-year portfolio simulation...")

        # Use default scenarios
        scenarios = create_default_investment_scenarios()
        initial_values = {
            'PersonA': 102000.0,  # Conservative starter
            'PersonB': 150000.0,  # Moderate with more capital
            'PersonC': 200000.0   # Aggressive with higher risk tolerance
        }

        results = {}

        for scenario_name, weights in scenarios.items():
            try:
                result = self.simulator.simulate_portfolio(
                    weights=weights,
                    initial_value=initial_values[scenario_name],
                    num_simulations=1000,
                    time_horizon_years=time_horizon
                )
                results[scenario_name] = result

                print(f"{scenario_name}: Mean final value ${result['mean_final_value']:,.0f} "
                      f"({result['mean_return']:.1%} return)")

            except Exception as e:
                print(f"Error simulating {scenario_name}: {e}")
                continue

        self.simulation_results = {
            'time_horizon': time_horizon,
            'scenarios': results,
            'generated_at': datetime.now().isoformat()
        }

        return self.simulation_results

    def generate_website_csv_data(self, time_horizon: int = 5) -> pd.DataFrame:
        """Generate CSV data in website format"""
        scenarios = create_default_investment_scenarios()
        initial_values = {
            'PersonA': 102000.0,
            'PersonB': 150000.0,
            'PersonC': 200000.0
        }

        csv_data = self.simulator.generate_csv_data(
            scenarios=scenarios,
            base_year=2025,
            time_horizon=time_horizon,
            initial_values=initial_values
        )

        return csv_data

    def update_existing_csv_files(self) -> dict[str, str]:
        """Update the existing PersonA/B/C CSV files with simulation results"""
        updated_files = {}

        # Generate 5-year simulation data
        csv_data = self.generate_website_csv_data(time_horizon=5)

        # Update each person's CSV file
        person_files = {
            'PersonA': 'personA_portfolio.csv',
            'PersonB': 'personB_portfolio.csv',
            'PersonC': 'personC_portfolio.csv'
        }

        for person, filename in person_files.items():
            filepath = self.output_dir / filename

            # Extract relevant columns for this person - handle both Year and Month formats
            time_column = 'Year' if 'Year' in csv_data.columns else 'Month'
            person_columns = [time_column] + [col for col in csv_data.columns if col.startswith(person)]
            person_data = csv_data[person_columns].copy()

            # Convert Month back to Year for existing file format compatibility
            if time_column == 'Month':
                # Extract years only (take January of each year)
                person_data['Year'] = person_data['Month'].apply(lambda x: int(x.split('-')[0]))
                # Filter to January values only for yearly format
                january_mask = person_data['Month'].str.endswith('-01')
                person_data = person_data[january_mask].copy()
                person_data = person_data.drop('Month', axis=1)

            # Add savings and 401k breakdown (simplified assumptions)
            if f'{person}_Total' in person_data.columns:
                # Assume 60% savings, 40% 401k split
                person_data[f'{person}_Savings'] = (person_data[f'{person}_Total'] * 0.6).round().astype(int)
                person_data[f'{person}_401k'] = (person_data[f'{person}_Total'] * 0.4).round().astype(int)

            # Reorder columns to match existing format
            expected_columns = ['Year', f'{person}_Savings', f'{person}_401k', f'{person}_Total', f'{person}_Lower', f'{person}_Upper']
            person_data = person_data[expected_columns]

            # Save updated file
            person_data.to_csv(filepath, index=False)
            updated_files[person] = str(filepath)

            print(f"Updated {filepath}")

        return updated_files

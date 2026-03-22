"""
Economic models for investment analysis and portfolio simulation
Implements Monte Carlo simulation with Geometric Brownian Motion for AI Safety investment strategies
"""

from typing import Any

import numpy as np
import pandas as pd


class MonteCarloPortfolioSimulator:
    """
    Monte Carlo portfolio simulator using Geometric Brownian Motion

    This class implements a well-documented financial model for simulating
    portfolio performance over time with confidence intervals.
    """

    def __init__(self, random_seed: int | None = None):
        """
        Initialize the simulator

        Args:
            random_seed: Optional seed for reproducible results
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        self.asset_params: dict[str, dict[str, Any]] = {}
        self.correlation_matrix = None
        self.correlation_assets: list[str] = []
        self.is_calibrated = False

    def calibrate_from_data(self, price_data: dict[str, pd.DataFrame]) -> None:
        """
        Calibrate model parameters from historical price data

        Args:
            price_data: Dictionary mapping asset names to DataFrames with 'Close' column
        """
        self.asset_params = {}
        returns_data = {}

        # Calculate returns and parameters for each asset
        for asset_name, df in price_data.items():
            if 'Close' not in df.columns:
                raise ValueError(f"Missing 'Close' column in data for {asset_name}")

            # Calculate daily returns
            prices = df['Close'].dropna()
            returns = prices.pct_change().dropna()

            if len(returns) < 30:  # Minimum data requirement
                print(f"Warning: Insufficient data for {asset_name} ({len(returns)} days)")
                continue

            # Calculate annualized parameters
            annual_return = returns.mean() * 252  # 252 trading days per year
            annual_volatility = returns.std() * np.sqrt(252)

            self.asset_params[asset_name] = {
                'mu': annual_return,  # Drift (expected return)
                'sigma': annual_volatility,  # Volatility
                'current_price': prices.iloc[-1],
                'returns': returns
            }

            returns_data[asset_name] = returns

        # Calculate correlation matrix
        if len(returns_data) > 1:
            returns_df = pd.DataFrame(returns_data).dropna()
            if len(returns_df) > 30:  # Need sufficient data for correlation
                self.correlation_matrix = returns_df.corr().values
                # Store the asset order for correlation matrix
                self.correlation_assets = returns_df.columns.tolist()
            else:
                print("Warning: Insufficient data for correlation calculation")
                self.correlation_matrix = None
                self.correlation_assets = []
        else:
            self.correlation_matrix = None
            self.correlation_assets = []

        self.is_calibrated = True
        print(f"Calibrated model for {len(self.asset_params)} assets")

    def simulate_asset_paths(
        self,
        asset_name: str,
        num_simulations: int = 1000,
        time_horizon_years: float = 5.0,
        num_steps: int = 252
    ) -> np.ndarray:
        """
        Simulate price paths for a single asset using Geometric Brownian Motion

        Args:
            asset_name: Name of the asset
            num_simulations: Number of Monte Carlo simulations
            time_horizon_years: Time horizon in years
            num_steps: Number of time steps per year (252 for daily)

        Returns:
            Array of shape (num_simulations, num_steps + 1) with price paths
        """
        if not self.is_calibrated or asset_name not in self.asset_params:
            raise ValueError(f"Model not calibrated for asset {asset_name}")

        params = self.asset_params[asset_name]
        S0 = params['current_price']
        mu = params['mu']
        sigma = params['sigma']

        dt = 1 / num_steps
        total_steps = int(num_steps * time_horizon_years)

        # Generate random shocks
        dW = np.random.normal(0, np.sqrt(dt), (num_simulations, total_steps))

        # Initialize price paths
        paths = np.zeros((num_simulations, total_steps + 1))
        paths[:, 0] = S0

        # Simulate paths using GBM: dS = mu * S * dt + sigma * S * dW
        for t in range(total_steps):
            paths[:, t + 1] = paths[:, t] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * dW[:, t]
            )

        return paths

    def simulate_portfolio(
        self,
        weights: dict[str, float],
        initial_value: float = 100000,
        num_simulations: int = 1000,
        time_horizon_years: float = 5.0,
        rebalancing_frequency: int = 63  # Quarterly rebalancing (63 trading days)
    ) -> dict[str, Any]:
        """
        Simulate portfolio performance with multiple assets

        Args:
            weights: Dictionary mapping asset names to portfolio weights (must sum to 1)
            initial_value: Initial portfolio value
            num_simulations: Number of Monte Carlo simulations
            time_horizon_years: Time horizon in years
            rebalancing_frequency: Rebalancing frequency in trading days

        Returns:
            Dictionary with simulation results and statistics
        """
        if not self.is_calibrated:
            raise ValueError("Model must be calibrated before simulation")

        # Validate weights
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")

        # Check all assets are available
        missing_assets = set(weights.keys()) - set(self.asset_params.keys())
        if missing_assets:
            raise ValueError(f"Missing calibration data for assets: {missing_assets}")

        num_steps = int(252 * time_horizon_years)  # Daily steps
        portfolio_paths = np.zeros((num_simulations, num_steps + 1))
        portfolio_paths[:, 0] = initial_value

        # Generate correlated random shocks if multiple assets
        asset_names = list(weights.keys())
        dt = 1/252  # Daily time step

        if len(asset_names) > 1 and self.correlation_matrix is not None:
            # Map current assets to correlation matrix indices
            corr_indices = []  # type: ignore[unreachable]
            valid_assets = []

            for asset in asset_names:
                if asset in self.correlation_assets:
                    corr_indices.append(self.correlation_assets.index(asset))
                    valid_assets.append(asset)

            if len(corr_indices) > 1:
                # Extract relevant sub-matrix
                sub_corr_matrix = self.correlation_matrix[np.ix_(corr_indices, corr_indices)]

                # Generate correlated random numbers for valid assets
                independent_shocks = np.random.normal(0, np.sqrt(dt), (num_simulations, num_steps, len(valid_assets)))

                try:
                    chol = np.linalg.cholesky(sub_corr_matrix)
                    valid_correlated_shocks = np.dot(independent_shocks, chol.T)

                    # Map back to full asset list
                    correlated_shocks = np.random.normal(0, np.sqrt(dt), (num_simulations, num_steps, len(asset_names)))

                    for i, asset in enumerate(asset_names):
                        if asset in valid_assets:
                            valid_idx = valid_assets.index(asset)
                            correlated_shocks[:, :, i] = valid_correlated_shocks[:, :, valid_idx]

                except np.linalg.LinAlgError:
                    print("Warning: Correlation sub-matrix not positive definite, using independent shocks")
                    correlated_shocks = np.random.normal(0, np.sqrt(dt), (num_simulations, num_steps, len(asset_names)))
            else:
                correlated_shocks = np.random.normal(0, np.sqrt(dt), (num_simulations, num_steps, len(asset_names)))
        else:
            correlated_shocks = np.random.normal(0, np.sqrt(dt), (num_simulations, num_steps, len(asset_names)))

        # Simulate portfolio paths
        for sim in range(num_simulations):
            current_weights = weights.copy()

            for t in range(num_steps):
                portfolio_return = 0

                # Calculate portfolio return for this time step
                for i, asset_name in enumerate(asset_names):
                    params = self.asset_params[asset_name]
                    mu = params['mu'] / 252  # Daily return
                    sigma = params['sigma'] / np.sqrt(252)  # Daily volatility

                    # Asset return using GBM
                    asset_return = mu + sigma * correlated_shocks[sim, t, i]
                    portfolio_return += current_weights[asset_name] * asset_return

                # Update portfolio value
                portfolio_paths[sim, t + 1] = portfolio_paths[sim, t] * (1 + portfolio_return)

                # Rebalance periodically (weights drift due to different asset performance)
                if (t + 1) % rebalancing_frequency == 0:
                    current_weights = weights.copy()  # Reset to target weights

        # Calculate statistics
        final_values = portfolio_paths[:, -1]
        returns = (final_values / initial_value) - 1

        # Calculate confidence intervals
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        confidence_intervals = np.percentile(final_values, percentiles)

        # Calculate path statistics
        path_means = np.mean(portfolio_paths, axis=0)
        path_stds = np.std(portfolio_paths, axis=0)

        return {
            'portfolio_paths': portfolio_paths,
            'path_means': path_means,
            'path_stds': path_stds,
            'final_values': final_values,
            'mean_final_value': np.mean(final_values),
            'median_final_value': np.median(final_values),
            'std_final_value': np.std(final_values),
            'mean_return': np.mean(returns),
            'median_return': np.median(returns),
            'std_return': np.std(returns),
            'confidence_intervals': dict(zip(percentiles, confidence_intervals, strict=False)),
            'success_probability': np.mean(final_values > initial_value),
            'time_horizon': time_horizon_years,
            'num_simulations': num_simulations,
            'weights': weights
        }

    def generate_csv_data(
        self,
        scenarios: dict[str, dict[str, float]],
        base_year: int = 2025,
        time_horizon: int = 5,
        initial_values: dict[str, float] | None = None
    ) -> pd.DataFrame:
        """
        Generate CSV data in the format expected by the website (PersonA/B/C format)

        Args:
            scenarios: Dictionary mapping scenario names to portfolio weights
            base_year: Starting year for simulation
            time_horizon: Number of years to simulate
            initial_values: Optional initial portfolio values for each scenario

        Returns:
            DataFrame in PersonA/B/C format with confidence intervals
        """
        if initial_values is None:
            initial_values = dict.fromkeys(scenarios.keys(), 100000)

        results = {}
        # Generate monthly timestamps for more granular data
        months = []
        for year in range(base_year, base_year + time_horizon + 1):
            for month in range(1, 13):
                if year == base_year + time_horizon and month > 1:
                    break  # Only include January of final year
                months.append(f"{year}-{month:02d}")
        months = months[:time_horizon * 12 + 1]  # Ensure exact length

        for scenario_name, weights in scenarios.items():
            # Run simulation
            sim_result = self.simulate_portfolio(
                weights=weights,
                initial_value=initial_values[scenario_name],
                time_horizon_years=time_horizon,
                num_simulations=1000
            )

            # Extract monthly values for more granular data
            monthly_indices = [int(i * 21) for i in range(time_horizon * 12 + 1)]  # Monthly snapshots (21 trading days/month)
            monthly_means = [sim_result['path_means'][min(i, len(sim_result['path_means'])-1)] for i in monthly_indices]
            monthly_lowers = [np.percentile(sim_result['portfolio_paths'][:, min(i, sim_result['portfolio_paths'].shape[1]-1)], 25) for i in monthly_indices]
            monthly_uppers = [np.percentile(sim_result['portfolio_paths'][:, min(i, sim_result['portfolio_paths'].shape[1]-1)], 75) for i in monthly_indices]

            results[f'{scenario_name}_Total'] = monthly_means
            results[f'{scenario_name}_Lower'] = monthly_lowers
            results[f'{scenario_name}_Upper'] = monthly_uppers

        df = pd.DataFrame(results)
        df['Month'] = months
        df = df[['Month'] + [col for col in df.columns if col != 'Month']]

        # Round to nearest thousand for readability
        for col in df.columns:
            if col != 'Month':
                df[col] = df[col].round(0).astype(int)

        return df

    def validate_model(self, test_data: dict[str, pd.DataFrame], validation_period_years: float = 1.0) -> dict[str, dict[str, Any]]:
        """
        Validate model accuracy against historical data

        Args:
            test_data: Dictionary mapping asset names to test DataFrames
            validation_period_years: Period to validate against

        Returns:
            Dictionary with validation metrics
        """
        if not self.is_calibrated:
            raise ValueError("Model must be calibrated before validation")

        results = {}

        for asset_name, df in test_data.items():
            if asset_name not in self.asset_params:
                continue

            # Get actual returns for validation period
            prices = df['Close'].dropna()
            if len(prices) < 30:
                continue

            actual_final_price = prices.iloc[-1]
            actual_initial_price = prices.iloc[0]
            actual_return = (actual_final_price / actual_initial_price) - 1

            # Run simulation for same period
            sim_paths = self.simulate_asset_paths(
                asset_name,
                num_simulations=1000,
                time_horizon_years=validation_period_years
            )

            predicted_returns = (sim_paths[:, -1] / sim_paths[:, 0]) - 1
            predicted_mean_return = np.mean(predicted_returns)

            # Calculate error metrics
            mae = abs(actual_return - predicted_mean_return)

            # Check if actual return falls within confidence interval
            ci_lower = np.percentile(predicted_returns, 25)
            ci_upper = np.percentile(predicted_returns, 75)
            in_ci = ci_lower <= actual_return <= ci_upper

            results[asset_name] = {
                'actual_return': actual_return,
                'predicted_mean_return': predicted_mean_return,
                'mae': mae,
                'in_confidence_interval': in_ci,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper
            }

        return results


def create_default_investment_scenarios() -> dict[str, dict[str, float]]:
    """
    Create default investment scenarios for PersonA, PersonB, PersonC

    Returns:
        Dictionary with default portfolio allocations
    """
    return {
        'PersonA': {  # Conservative
            '^GSPC': 0.30,  # S&P 500
            'AGG': 0.25,    # Bonds
            'VNQ': 0.15,    # REITs
            'GLD': 0.10,    # Gold
            'XRP-USD': 0.05, # Utility crypto
            'SHY': 0.15     # Short-term bonds (cash equivalent)
        },
        'PersonB': {  # Moderate
            '^GSPC': 0.35,  # S&P 500
            'QQQ': 0.15,    # Tech/Growth
            'VNQ': 0.15,    # REITs
            'AGG': 0.15,    # Bonds
            'GLD': 0.10,    # Gold
            'XRP-USD': 0.05, # Utility crypto
            'ETH-USD': 0.05  # Smart-contract platform
        },
        'PersonC': {  # Aggressive
            '^GSPC': 0.25,  # S&P 500
            'QQQ': 0.20,    # Tech/Growth
            'VTI': 0.10,    # Total market
            'VNQ': 0.10,    # REITs
            'XRP-USD': 0.10, # Utility crypto
            'ETH-USD': 0.05, # Smart-contract platform
            'LINK-USD': 0.05, # DeFi oracle
            'BTC-USD': 0.05, # Store of value
            'GLD': 0.10     # Gold
        }
    }

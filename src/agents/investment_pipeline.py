#!/usr/bin/env python3
"""
Investment Strategy Pipeline
Master script that orchestrates the complete investment analysis pipeline:
1. Historical data analysis and visualization
2. Economic model calibration and simulation
3. Portfolio scenario generation
4. Website integration and plot generation
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.agents.utils.historical_visualization import HistoricalDataVisualizationAgent
from src.agents.utils.portfolio_simulation import PortfolioSimulationAgent
from src.builders.plot_generator import create_comparative_wealth_plot


def run_complete_investment_pipeline(
    output_dir: str = "src/data",
    generate_visualizations: bool = True,
    update_plots: bool = True,
    time_horizons: list[int] | None = None
) -> dict[str, Any]:
    """
    Run the complete investment strategy pipeline

    Args:
        output_dir: Directory for output files
        generate_visualizations: Whether to create historical visualizations
        update_plots: Whether to update website plots
        time_horizons: List of years to simulate (default: [3, 5, 10])

    Returns:
        Dictionary with pipeline results
    """
    if time_horizons is None:
        time_horizons = [3, 5, 10]

    print("=" * 60)
    print("AI SAFETY INVESTMENT STRATEGY PIPELINE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results: dict[str, Any] = {
        'started_at': datetime.now().isoformat(),
        'pipeline_steps': {},
        'files_generated': {},
        'errors': []
    }

    # Step 1: Historical Data Analysis and Visualization
    if generate_visualizations:
        print("Step 1: Historical Data Analysis and Visualization")
        print("-" * 50)

        try:
            viz_agent = HistoricalDataVisualizationAgent()

            # Fetch all historical data
            print("Fetching maximum historical data for all assets...")
            historical_data = viz_agent.fetch_all_historical_data()

            # Generate visualizations
            print("Creating comprehensive visualizations...")
            charts = viz_agent.create_all_visualizations()

            # Generate dropdown data for website
            dropdown_file = viz_agent.save_dropdown_data()

            # Analyze trends
            print("Analyzing historical trends...")
            _trends = viz_agent.analyze_trends()

            results['pipeline_steps']['historical_analysis'] = {
                'status': 'completed',
                'assets_analyzed': sum(len(data) for data in historical_data.values()),
                'charts_created': sum(len(charts) for charts in charts.values()),
                'dropdown_file': dropdown_file
            }

            results['files_generated']['dropdown_data'] = dropdown_file
            results['files_generated']['visualizations'] = charts

            print(f"✓ Analyzed {results['pipeline_steps']['historical_analysis']['assets_analyzed']} assets")
            print(f"✓ Created {results['pipeline_steps']['historical_analysis']['charts_created']} visualizations")
            print()

        except Exception as e:
            print(f"✗ Error in historical analysis: {e}")
            results['errors'].append(f"Historical analysis: {e}")
            results['pipeline_steps']['historical_analysis'] = {'status': 'failed', 'error': str(e)}

    # Step 2: Portfolio Simulation and Economic Modeling
    print("Step 2: Portfolio Simulation and Economic Modeling")
    print("-" * 50)

    try:
        portfolio_agent = PortfolioSimulationAgent(output_dir=output_dir)

        # Calibrate models
        print("Calibrating economic models with historical data...")
        portfolio_agent.calibrate_simulation_models()

        # Run simulations for different time horizons
        simulation_results = {}

        for years in time_horizons:
            print(f"Running {years}-year portfolio simulation...")
            sim_result = portfolio_agent.run_portfolio_simulation(time_horizon=years)
            simulation_results[f'{years}_years'] = sim_result

            # Generate and save CSV data
            csv_data = portfolio_agent.generate_website_csv_data(time_horizon=years)
            csv_file = Path(output_dir) / f"portfolio_simulation_{years}year.csv"
            csv_data.to_csv(csv_file, index=False)

            results['files_generated'][f'simulation_{years}y_csv'] = str(csv_file)

            print(f"✓ Completed {years}-year simulation, saved to {csv_file}")

        # Update existing PersonA/B/C CSV files with 5-year simulation
        print("Updating existing portfolio CSV files...")
        updated_files = portfolio_agent.update_existing_csv_files()

        results['pipeline_steps']['portfolio_simulation'] = {
            'status': 'completed',
            'time_horizons': time_horizons,
            'scenarios_simulated': len(simulation_results[f'{time_horizons[0]}_years']['scenarios']),
            'csv_files_updated': len(updated_files)
        }

        results['files_generated'].update({f'person_{k}': v for k, v in updated_files.items()})

        print(f"✓ Simulated {len(time_horizons)} time horizons")
        print(f"✓ Updated {len(updated_files)} portfolio CSV files")
        print()

    except Exception as e:
        print(f"✗ Error in portfolio simulation: {e}")
        results['errors'].append(f"Portfolio simulation: {e}")
        results['pipeline_steps']['portfolio_simulation'] = {'status': 'failed', 'error': str(e)}

    # Step 3: Update Website Plots
    if update_plots:
        print("Step 3: Updating Website Plots")
        print("-" * 50)

        try:
            # Update the comparative wealth plot with new data
            csv_file = Path(output_dir) / "comparative_wealth.csv"

            if csv_file.exists():
                print("Updating comparative wealth plot...")
                create_comparative_wealth_plot(
                    data_dir=output_dir,
                    save_path="src/static/images/comparative_wealth.png"
                )

                results['pipeline_steps']['plot_generation'] = {
                    'status': 'completed',
                    'plots_updated': ['comparative_wealth.png']
                }

                results['files_generated']['comparative_wealth_plot'] = "src/static/images/comparative_wealth.png"

                print("✓ Updated comparative wealth plot")
            else:
                print("⚠ Comparative wealth CSV not found, skipping plot update")
                results['pipeline_steps']['plot_generation'] = {
                    'status': 'skipped',
                    'reason': 'CSV file not found'
                }

            print()

        except Exception as e:
            print(f"✗ Error updating plots: {e}")
            results['errors'].append(f"Plot generation: {e}")
            results['pipeline_steps']['plot_generation'] = {'status': 'failed', 'error': str(e)}

    # Step 4: Generate Summary Report
    print("Step 4: Generating Pipeline Summary")
    print("-" * 50)

    try:
        summary_file = Path(output_dir) / f"investment_pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(summary_file, 'w') as f:
            f.write("AI Safety Investment Strategy Pipeline Summary\\n")
            f.write("=" * 60 + "\\n\\n")
            f.write(f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")

            # Pipeline status
            f.write("Pipeline Steps Status:\\n")
            for step_name, step_data in results['pipeline_steps'].items():
                status = step_data['status']
                f.write(f"  {step_name}: {status.upper()}\\n")
                if status == 'failed':
                    f.write(f"    Error: {step_data.get('error', 'Unknown')}\\n")
            f.write("\\n")

            # Files generated
            f.write("Files Generated:\\n")
            for file_type, file_path in results['files_generated'].items():
                f.write(f"  {file_type}: {file_path}\\n")
            f.write("\\n")

            # Errors
            if results['errors']:
                f.write("Errors Encountered:\\n")
                for error in results['errors']:
                    f.write(f"  - {error}\\n")
            else:
                f.write("No errors encountered.\\n")

        results['files_generated']['summary_report'] = str(summary_file)

        print(f"✓ Generated summary report: {summary_file}")
        print()

    except Exception as e:
        print(f"✗ Error generating summary: {e}")
        results['errors'].append(f"Summary generation: {e}")

    # Final status
    results['completed_at'] = datetime.now().isoformat()
    total_steps = len(results['pipeline_steps'])
    completed_steps = sum(1 for step in results['pipeline_steps'].values() if step['status'] == 'completed')

    print("=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)
    print(f"Steps completed: {completed_steps}/{total_steps}")
    print(f"Files generated: {len(results['files_generated'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"Total runtime: {datetime.fromisoformat(results['completed_at']) - datetime.fromisoformat(results['started_at'])}")

    if results['errors']:
        print("\\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
        return results
    else:
        print("\\n✓ All steps completed successfully!")
        return results


def main() -> None:
    """Main entry point for the investment pipeline"""
    parser = argparse.ArgumentParser(
        description="AI Safety Investment Strategy Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python investment_pipeline.py                    # Run full pipeline
  python investment_pipeline.py --no-viz           # Skip visualizations
  python investment_pipeline.py --years 3 5        # Only 3 and 5 year simulations
  python investment_pipeline.py --output-dir data  # Custom output directory
        """
    )

    parser.add_argument(
        '--output-dir',
        default='src/data',
        help='Directory for output files (default: src/data)'
    )

    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip historical data visualizations'
    )

    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip website plot updates'
    )

    parser.add_argument(
        '--years',
        nargs='+',
        type=int,
        default=[3, 5, 10],
        help='Time horizons to simulate in years (default: 3 5 10)'
    )

    args = parser.parse_args()

    try:
        results = run_complete_investment_pipeline(
            output_dir=args.output_dir,
            generate_visualizations=not args.no_viz,
            update_plots=not args.no_plots,
            time_horizons=args.years
        )

        # Exit with error code if there were failures
        if results['errors']:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\\n\\nPipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\\n\\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

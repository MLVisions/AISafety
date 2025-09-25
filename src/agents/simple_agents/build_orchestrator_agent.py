"""
Build Orchestrator Agent - Simple Agent for coordinating website builds
Manages the build process, plot generation, and deployment coordination
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from crewai import Agent, Task
from crewai_tools import DirectoryReadTool, FileReadTool


class BuildOrchestratorAgent:
    """Agent responsible for orchestrating website builds and deployments"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.src_dir = self.project_root / "src"

        # Initialize CrewAI agent
        self.agent = Agent(
            role="Build and Deployment Coordinator",
            goal=(
                "Orchestrate the complete website build process including plot generation, "
                "content processing, and deployment preparation. Ensure all components "
                "work together seamlessly and handle build errors gracefully."
            ),
            backstory=(
                "You are an experienced DevOps engineer and build automation specialist. "
                "You understand the intricacies of static site generation, dependency "
                "management, and deployment pipelines. Your expertise ensures reliable, "
                "reproducible builds."
            ),
            tools=[DirectoryReadTool(), FileReadTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )

    def create_build_task(
        self,
        regenerate_plots: bool = True,
        validate_content: bool = True,
        deploy_ready: bool = False
    ) -> Task:
        """
        Create a task to orchestrate the website build

        Args:
            regenerate_plots: Whether to regenerate all plots
            validate_content: Whether to validate content before building
            deploy_ready: Whether to prepare for deployment

        Returns:
            CrewAI Task for build orchestration
        """
        description = f"""
        Orchestrate a complete website build with the following steps:

        1. Pre-build validation:
           - Check that all required source files exist
           - Validate project structure
           {"- Run content validation if requested" if validate_content else ""}

        2. Asset generation:
           {"- Regenerate all plots and charts" if regenerate_plots else "- Verify existing plots are current"}
           - Generate navigation icons
           - Process any updated data files

        3. Build execution:
           - Run the main build script (build.py)
           - Monitor for build errors and warnings
           - Verify output directory structure

        4. Post-build verification:
           - Check that all expected HTML files were generated
           - Verify all assets are properly copied
           - Test that generated site loads correctly

        {"5. Deployment preparation:" if deploy_ready else ""}
        {"   - Validate deployment prerequisites" if deploy_ready else ""}
        {"   - Generate deployment summary" if deploy_ready else ""}
        {"   - Prepare any necessary deployment artifacts" if deploy_ready else ""}

        Project root: {self.project_root}
        Output directory: {self.docs_dir}

        Provide detailed logging of each step and handle any errors gracefully.
        """

        return Task(
            description=description,
            agent=self.agent,
            expected_output=(
                "A detailed build report including success/failure status, "
                "build metrics, any errors encountered, and verification results. "
                f"{'Include deployment readiness status if requested.' if deploy_ready else ''}"
            )
        )

    def build_website_direct(
        self,
        regenerate_plots: bool = True,
        validate_content: bool = False,
        clean_build: bool = False
    ) -> dict[str, Any]:
        """
        Direct method to build the website without CrewAI task orchestration

        Args:
            regenerate_plots: Whether to regenerate all plots
            validate_content: Whether to validate content first
            clean_build: Whether to clean output directory first

        Returns:
            Build report dictionary
        """
        build_start = datetime.now()
        print(f"🚀 Starting website build at {build_start.strftime('%Y-%m-%d %H:%M:%S')}")

        build_report: dict[str, Any] = {
            "build_timestamp": build_start.isoformat(),
            "project_root": str(self.project_root),
            "steps": [],
            "success": False,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }

        try:
            # Step 1: Pre-build validation
            print("📋 Step 1: Pre-build validation...")
            validation_result = self._validate_prebuild()
            build_report["steps"].append({
                "step": "prebuild_validation",
                "status": "success" if validation_result["valid"] else "warning",
                "details": validation_result
            })

            if not validation_result["valid"]:
                build_report["warnings"].extend(validation_result["issues"])

            # Step 2: Content validation (if requested)
            if validate_content:
                print("🔍 Step 2: Content validation...")
                # Would call content validator here
                print("   Content validation skipped in direct build")

            # Step 3: Clean build (if requested)
            if clean_build:
                print("🧹 Step 3: Cleaning output directory...")
                self._clean_output_directory()
                build_report["steps"].append({
                    "step": "clean_output",
                    "status": "success",
                    "details": {"cleaned": str(self.docs_dir)}
                })

            # Step 4: Execute main build
            print("🔨 Step 4: Executing main build...")
            build_result = self._execute_build()
            build_report["steps"].append({
                "step": "main_build",
                "status": "success" if build_result["success"] else "failed",
                "details": build_result
            })

            if not build_result["success"]:
                build_report["errors"].append(f"Build failed: {build_result.get('error', 'Unknown error')}")
                return build_report

            # Step 5: Post-build verification
            print("✅ Step 5: Post-build verification...")
            verification_result = self._verify_build_output()
            build_report["steps"].append({
                "step": "verification",
                "status": "success" if verification_result["valid"] else "warning",
                "details": verification_result
            })

            if not verification_result["valid"]:
                build_report["warnings"].extend(verification_result["issues"])

            # Build successful
            build_report["success"] = True
            build_end = datetime.now()
            build_duration = (build_end - build_start).total_seconds()

            build_report["metrics"] = {
                "build_duration_seconds": build_duration,
                "output_files": len(list(self.docs_dir.glob("*.html"))),
                "asset_files": len(list(self.docs_dir.glob("**/*"))) - len(list(self.docs_dir.glob("*.html")))
            }

            print(f"✅ Website build completed successfully in {build_duration:.1f} seconds")

        except Exception as e:
            build_report["errors"].append(f"Build process failed: {str(e)}")
            print(f"❌ Build failed: {e}")

        # Save build report
        report_file = self.project_root / "build_report.json"
        with open(report_file, 'w') as f:
            json.dump(build_report, f, indent=2)

        return build_report

    def _validate_prebuild(self) -> dict[str, Any]:
        """Validate prerequisites for building"""
        validation: dict[str, Any] = {"valid": True, "issues": []}

        # Check required directories
        required_dirs = [
            self.src_dir / "content",
            self.src_dir / "templates",
            self.src_dir / "static",
            self.src_dir / "builders"
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                validation["valid"] = False
                validation["issues"].append(f"Missing required directory: {dir_path}")

        # Check for build script
        build_script = self.project_root / "build.py"
        if not build_script.exists():
            validation["valid"] = False
            validation["issues"].append("Missing build.py script")

        # Check for content files
        content_files = list((self.src_dir / "content").glob("*.md"))
        if len(content_files) == 0:
            validation["issues"].append("No markdown content files found")

        validation["content_files_found"] = len(content_files)
        return validation

    def _clean_output_directory(self) -> None:
        """Clean the output directory"""
        if self.docs_dir.exists():
            import shutil
            shutil.rmtree(self.docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def _execute_build(self) -> dict[str, Any]:
        """Execute the main build script"""
        try:
            # Change to project root and run build script
            result = subprocess.run(
                [sys.executable, "build.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None if result.returncode == 0 else result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Build script timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute build script: {str(e)}"
            }

    def _verify_build_output(self) -> dict[str, Any]:
        """Verify the build output is complete"""
        verification: dict[str, Any] = {"valid": True, "issues": []}

        # Check output directory exists
        if not self.docs_dir.exists():
            verification["valid"] = False
            verification["issues"].append("Output directory does not exist")
            return verification

        # Check for expected HTML files
        expected_files = ["index.html"]
        content_files = list((self.src_dir / "content").glob("*.md"))

        for content_file in content_files:
            if content_file.stem != "index":
                expected_files.append(f"{content_file.stem}.html")

        missing_files = []
        for expected in expected_files:
            if not (self.docs_dir / expected).exists():
                missing_files.append(expected)

        if missing_files:
            verification["valid"] = False
            verification["issues"].extend([f"Missing output file: {f}" for f in missing_files])

        # Check for assets
        required_assets = ["style.css", "script.js"]
        for asset in required_assets:
            if not (self.docs_dir / asset).exists():
                verification["issues"].append(f"Missing asset: {asset}")

        # Check for images directory
        if not (self.docs_dir / "images").exists():
            verification["issues"].append("Missing images directory")

        verification["html_files_generated"] = len(list(self.docs_dir.glob("*.html")))
        verification["total_files"] = len(list(self.docs_dir.glob("**/*")))

        return verification


def create_build_orchestrator_agent(project_root: str = ".") -> BuildOrchestratorAgent:
    """Factory function to create a BuildOrchestratorAgent"""
    return BuildOrchestratorAgent(project_root=project_root)


if __name__ == "__main__":
    # Test the agent
    agent = create_build_orchestrator_agent()

    # Test direct build
    report = agent.build_website_direct(
        regenerate_plots=False,  # Skip plot regeneration for quick test
        validate_content=False,
        clean_build=True
    )

    print(f"Build {'succeeded' if report['success'] else 'failed'}")
    if report['errors']:
        print("Errors:", report['errors'])
    if report['warnings']:
        print("Warnings:", report['warnings'])

    print(f"Generated {report.get('metrics', {}).get('output_files', 0)} HTML files")

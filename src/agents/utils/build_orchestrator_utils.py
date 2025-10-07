"""
Build Orchestrator Utilities
Direct build coordination functions without CrewAI agent overhead
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class BuildOrchestratorUtils:
    """Utility class for direct build operations"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.src_dir = self.project_root / "src"

    def build_website_direct(
        self,
        regenerate_plots: bool = True,
        validate_content: bool = True,
        clean_output: bool = False
    ) -> dict[str, Any]:
        """
        Build website directly without CrewAI agent

        Args:
            regenerate_plots: Whether to regenerate plots
            validate_content: Whether to validate content first
            clean_output: Whether to clean output directory first

        Returns:
            Dictionary with build results
        """
        build_start = datetime.now()
        print(f"Starting website build at {build_start}")

        build_results = {
            'build_start': build_start.isoformat(),
            'stages': {},
            'success': False,
            'errors': []
        }

        try:
            # Stage 1: Pre-build validation
            if validate_content:
                print("Stage 1: Pre-build validation")
                validation_result = self._validate_prebuild()
                build_results['stages']['validation'] = validation_result

                if not validation_result['success']:
                    build_results['errors'].append("Pre-build validation failed")

            # Stage 2: Clean output directory
            if clean_output:
                print("Stage 2: Cleaning output directory")
                self._clean_output_directory()

            # Stage 3: Execute build
            print("Stage 3: Building website")
            build_result = self._execute_build()
            build_results['stages']['build'] = build_result

            if not build_result['success']:
                build_results['errors'].append("Build execution failed")
                return build_results

            # Stage 4: Verify build output
            print("Stage 4: Verifying build output")
            verification_result = self._verify_build_output()
            build_results['stages']['verification'] = verification_result

            build_results['success'] = (
                build_result['success'] and
                verification_result['success']
            )

            build_end = datetime.now()
            build_results['build_end'] = build_end.isoformat()
            build_results['total_duration'] = str(build_end - build_start)

            if build_results['success']:
                print(f"✅ Build completed successfully in {build_results['total_duration']}")
            else:
                print(f"❌ Build completed with issues in {build_results['total_duration']}")

        except Exception as e:
            error_msg = f"Build failed with exception: {str(e)}"
            build_results['errors'].append(error_msg)
            build_results['build_end'] = datetime.now().isoformat()
            print(f"❌ {error_msg}")

        return build_results

    def _validate_prebuild(self) -> dict[str, Any]:
        """Validate project structure before building"""
        validation_result = {
            'success': True,
            'checks': {},
            'warnings': []
        }

        # Check essential directories
        essential_dirs = ['src', 'src/content', 'src/templates', 'src/static']
        for dir_name in essential_dirs:
            dir_path = self.project_root / dir_name
            validation_result['checks'][dir_name] = dir_path.exists()
            if not dir_path.exists():
                validation_result['success'] = False
                validation_result['warnings'].append(f"Missing directory: {dir_name}")

        # Check for build script
        build_script = self.project_root / "build.py"
        validation_result['checks']['build_script'] = build_script.exists()
        if not build_script.exists():
            validation_result['success'] = False
            validation_result['warnings'].append("Missing build.py script")

        return validation_result

    def _clean_output_directory(self) -> None:
        """Clean the output directory"""
        if self.docs_dir.exists():
            import shutil
            shutil.rmtree(self.docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def _execute_build(self) -> dict[str, Any]:
        """Execute the build script"""
        build_result = {
            'success': False,
            'return_code': None,
            'stdout': '',
            'stderr': ''
        }

        try:
            # Execute build.py
            result = subprocess.run(
                [sys.executable, "build.py"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            build_result['return_code'] = result.returncode
            build_result['stdout'] = result.stdout
            build_result['stderr'] = result.stderr
            build_result['success'] = result.returncode == 0

            if not build_result['success']:
                print(f"Build script failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error output: {result.stderr}")

        except subprocess.TimeoutExpired:
            build_result['stderr'] = "Build timed out after 5 minutes"
            print("❌ Build timed out")
        except Exception as e:
            build_result['stderr'] = str(e)
            print(f"❌ Build execution failed: {e}")

        return build_result

    def _verify_build_output(self) -> dict[str, Any]:
        """Verify that the build produced the expected output"""
        verification_result = {
            'success': True,
            'files_generated': [],
            'missing_files': [],
            'issues': []
        }

        # Expected files
        expected_files = [
            'index.html',
            'economy.html',
            'technology.html',
            'llm.html',
            'privacy.html',
            'society.html',
            'action.html',
            'references.html',
            'style.css',
            'script.js'
        ]

        # Check for generated files
        for filename in expected_files:
            file_path = self.docs_dir / filename
            if file_path.exists():
                verification_result['files_generated'].append(filename)
            else:
                verification_result['missing_files'].append(filename)
                verification_result['success'] = False

        # Check for images directory
        images_dir = self.docs_dir / "images"
        if images_dir.exists():
            image_count = len(list(images_dir.glob("*.png")))
            verification_result['images_generated'] = image_count
            if image_count == 0:
                verification_result['issues'].append("No images found in images directory")
        else:
            verification_result['success'] = False
            verification_result['missing_files'].append("images/")

        return verification_result

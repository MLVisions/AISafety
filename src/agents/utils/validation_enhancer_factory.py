"""
Factory for creating page-specific validation enhancers
Provides domain-specific validation logic for different page types
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ValidationEnhancer(ABC):
    """Abstract base class for page-specific validation enhancers"""

    @abstractmethod
    def validate_content(self, content: str) -> dict[str, Any]:
        """Validate content and return validation results"""
        pass


class ActionValidationEnhancer(ValidationEnhancer):
    """Validation enhancer for action.md content"""

    def validate_content(self, content: str) -> dict[str, Any]:
        """Validate action content for strategy feasibility and actionability"""
        try:
            # Check for malformed content sections
            malformed_issues = self._detect_malformed_sections(content)

            # Strategy feasibility validation
            strategy_score = self._validate_strategy_feasibility(content)

            # Resource accessibility validation
            resource_score = self._validate_resource_accessibility(content)

            # Clarity validation
            clarity_score = self._validate_clarity(content)

            # Actionability validation
            actionability_score = self._validate_actionability(content)

            # Penalize score if malformed content is found
            malformed_penalty = 0.5 if malformed_issues else 0.0

            # Overall score
            overall_score = (strategy_score + resource_score + clarity_score + actionability_score) / 4
            overall_score = max(0.0, overall_score - malformed_penalty)

            result = {
                "score": overall_score,
                "strategy_feasibility": strategy_score,
                "resource_accessibility": resource_score,
                "clarity": clarity_score,
                "actionability": actionability_score,
                "details": {
                    "strategies_found": len(re.findall(r"###.*(?:strategy|approach|method)", content, re.IGNORECASE)),
                    "action_items": len(re.findall(r"\*\*.*\*\*", content)),
                    "word_count": len(content.split())
                }
            }

            if malformed_issues:
                result["malformed_sections"] = malformed_issues
                result["warnings"] = ["Content contains malformed or incomplete sections"]

            return result

        except Exception as e:
            logger.error(f"Action validation failed: {e}")
            return {"score": 0.0, "error": str(e)}

    def _validate_strategy_feasibility(self, content: str) -> float:
        """Validate feasibility of presented strategies"""
        feasible_indicators = [
            "step-by-step", "gradual", "practical", "achievable",
            "realistic", "accessible", "start", "begin"
        ]

        score = 0.0
        for indicator in feasible_indicators:
            if indicator in content.lower():
                score += 0.1

        return min(score, 1.0)

    def _validate_resource_accessibility(self, content: str) -> float:
        """Validate accessibility of mentioned resources"""
        accessible_resources = [
            "free", "online", "course", "tutorial", "guide",
            "community", "local", "available", "accessible"
        ]

        score = 0.0
        for resource in accessible_resources:
            if resource in content.lower():
                score += 0.1

        return min(score, 1.0)

    def _validate_clarity(self, content: str) -> float:
        """Validate clarity of action recommendations"""
        # Count clear action verbs
        action_verbs = [
            "build", "learn", "develop", "create", "join", "start",
            "practice", "engage", "participate", "contribute"
        ]

        verb_count = sum(1 for verb in action_verbs if verb in content.lower())
        clarity_score = min(verb_count * 0.1, 1.0)

        # Check for specific examples
        if "example" in content.lower() or "for instance" in content.lower():
            clarity_score = min(clarity_score + 0.2, 1.0)

        return clarity_score

    def _detect_malformed_sections(self, content: str) -> list[str]:
        """Detect malformed or incomplete content sections"""
        issues = []

        # Check for incomplete sentences at the start of italicized sections
        incomplete_italic = re.findall(r"\*([a-z][^\*]{1,20})\*", content)
        for match in incomplete_italic:
            if not match.strip().endswith(('.', '!', '?', ':')):
                # Very short incomplete italic text
                issues.append(f"Incomplete italic section: '*{match}*'")

        # Check for multiple consecutive "Recent Development" sections
        recent_dev_count = len(re.findall(r"### Recent Development", content))
        if recent_dev_count > 1:
            issues.append(f"Multiple 'Recent Development' sections found ({recent_dev_count})")

        # Check for very short sections (likely truncated)
        short_sections = re.findall(r"###\s+([^\n]+)\n\*([^\*]{1,20})\*", content)
        for heading, text in short_sections:
            if len(text.strip()) < 15 and not text.strip().endswith(('.', '!', '?')):
                issues.append(f"Suspiciously short section under '{heading}': '{text}'")

        return issues

    def _validate_actionability(self, content: str) -> float:
        """Validate how actionable the content is"""
        # Look for concrete steps
        step_patterns = [
            r"\d+\.\s", r"first", r"then", r"next", r"finally",
            r"step \d+", r"stage \d+"
        ]

        step_count = sum(1 for pattern in step_patterns
                        if re.search(pattern, content, re.IGNORECASE))

        actionability_score = min(step_count * 0.15, 1.0)

        # Bonus for direct calls to action
        if re.search(r"you (?:should|can|must|need to)", content, re.IGNORECASE):
            actionability_score = min(actionability_score + 0.3, 1.0)

        return actionability_score


class TechnologyValidationEnhancer(ValidationEnhancer):
    """Validation enhancer for technology.md and llm.md content"""

    def validate_content(self, content: str) -> dict[str, Any]:
        """Validate technology content for accuracy and technical depth"""
        try:
            # Technical accuracy validation
            accuracy_score = self._validate_technical_accuracy(content)

            # Model claims validation
            model_score = self._validate_model_claims(content)

            # Benchmark accuracy validation
            benchmark_score = self._validate_benchmark_accuracy(content)

            # Release date validation
            date_score = self._validate_release_dates(content)

            # Overall score
            overall_score = (accuracy_score + model_score + benchmark_score + date_score) / 4

            return {
                "score": overall_score,
                "technical_accuracy": accuracy_score,
                "model_claims": model_score,
                "benchmark_accuracy": benchmark_score,
                "release_dates": date_score,
                "details": {
                    "models_mentioned": len(re.findall(r"(?:GPT|Claude|LLaMA|PaLM|Gemini)", content, re.IGNORECASE)),
                    "benchmarks_found": len(re.findall(r"\d+(?:\.\d+)?%", content)),
                    "technical_terms": len(re.findall(r"(?:neural|transformer|attention|parameter)", content, re.IGNORECASE)),
                    "word_count": len(content.split())
                }
            }

        except Exception as e:
            logger.error(f"Technology validation failed: {e}")
            return {"score": 0.0, "error": str(e)}

    def _validate_technical_accuracy(self, content: str) -> float:
        """Validate technical accuracy of claims"""
        technical_terms = [
            "neural network", "transformer", "attention", "parameter",
            "training", "inference", "model", "algorithm"
        ]

        score = 0.0
        for term in technical_terms:
            if term in content.lower():
                score += 0.1

        return min(score, 1.0)

    def _validate_model_claims(self, content: str) -> float:
        """Validate model-related claims"""
        # Look for specific model mentions with proper context
        model_patterns = [
            r"GPT-\d+", r"Claude \d+", r"LLaMA \d+", r"PaLM \d+", r"Gemini"
        ]

        model_count = sum(1 for pattern in model_patterns
                         if re.search(pattern, content, re.IGNORECASE))

        return min(model_count * 0.2, 1.0)

    def _validate_benchmark_accuracy(self, content: str) -> float:
        """Validate benchmark claims"""
        # Look for percentage scores
        percentages = re.findall(r"\d+(?:\.\d+)?%", content)

        if percentages:
            # Check if percentages are realistic (0-100%)
            valid_percentages = [p for p in percentages
                               if 0 <= float(p.rstrip('%')) <= 100]
            score = min(len(valid_percentages) * 0.2, 1.0)
        else:
            score = 0.0

        return score

    def _validate_release_dates(self, content: str) -> float:
        """Validate release date mentions"""
        # Look for year mentions (2020-2025 range)
        years = re.findall(r"20(?:2[0-5]|1[0-9])", content)

        if years:
            score = min(len(set(years)) * 0.2, 1.0)
        else:
            score = 0.0

        return score


class ValidationEnhancerFactory:
    """Factory for creating page-specific validation enhancers"""

    @staticmethod
    def create_enhancer(page_name: str) -> ValidationEnhancer:
        """Create appropriate validation enhancer for page type"""
        enhancer_map = {
            "action": ActionValidationEnhancer(),
            "technology": TechnologyValidationEnhancer(),
            "llm": TechnologyValidationEnhancer(),  # LLM uses same as technology
            "economy": TechnologyValidationEnhancer(),  # Can be specialized later
            "society": ActionValidationEnhancer(),  # Similar to action for now
            "privacy": TechnologyValidationEnhancer(),  # Use technology enhancer for now
        }

        if page_name not in enhancer_map:
            raise ValueError(f"No validation enhancer for page: {page_name}")

        return enhancer_map[page_name]

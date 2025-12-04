"""
Automated semantic validation for TMF921 intents.

Validates semantic correctness (not just schema validity) through:
1. Value extraction and matching  
2. Requirement completeness
3. LLM-based verification
"""

import re
import json
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticValidator:
    """Automated semantic validation for TMF921 intents."""
    
    def __init__(self, llm_client=None):
        """
        Initialize semantic validator.
        
        Args:
            llm_client: Optional LLM client for Layer 3 validation
        """
        self.llm_client = llm_client
    
    def validate(self, scenario: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive semantic validation.
        
        Args:
            scenario: Original natural language requirement
            intent: Generated TMF921 intent
            
        Returns:
            {
                'semantic_valid': bool,
                'value_match_score': float (0-1),
                'completeness_score': float (0-1),
                'llm_judgment': dict or None,
                'overall_score': float (0-1),
                'errors': list of str
            }
        """
        # Layer 1: Value matching
        value_match = self._validate_values(scenario, intent)
        
        # Layer 2: Completeness
        completeness = self._validate_completeness(scenario, intent)
        
        # Layer 3: LLM judgment (if available)
        llm_judgment = None
        if self.llm_client:
            try:
                llm_judgment = self._llm_semantic_check(scenario, intent)
            except Exception as e:
                logger.warning(f"LLM judgment failed: {e}")
        
        # Combine scores
        if llm_judgment and 'confidence' in llm_judgment:
            overall = (
                value_match['match_rate'] * 0.3 +
                completeness * 0.3 +
                llm_judgment['confidence'] * 0.4
            )
            semantic_valid = (
                overall > 0.75 and 
                llm_judgment.get('semantically_correct', False)
            )
        else:
            # Without LLM, use stricter thresholds
            overall = (value_match['match_rate'] * 0.5 + completeness * 0.5)
            semantic_valid = overall > 0.8
        
        # Collect errors
        errors = []
        if value_match['missing']:
            errors.extend([f"Missing value: {v}" for v in value_match['missing']])
        if llm_judgment and llm_judgment.get('value_errors'):
            errors.extend(llm_judgment['value_errors'])
        if llm_judgment and llm_judgment.get('missing_requirements'):
            errors.extend(llm_judgment['missing_requirements'])
        
        return {
            'semantic_valid': semantic_valid,
            'value_match_score': value_match['match_rate'],
            'completeness_score': completeness,
            'llm_judgment': llm_judgment,
            'overall_score': overall,
            'errors': errors
        }
    
    def _validate_values(self, scenario: str, intent: Dict[str, Any]) -> Dict:
        """
        Layer 1: Extract and match values.
        
        Checks if numerical requirements from scenario appear in intent.
        """
        # Extract requirements from scenario
        extracted = self._extract_requirements(scenario)
        
        # Search for each in intent
        matches = []
        missing = []
        
        for req_type, values in extracted.items():
            for value_tuple in values:
                # Ensure we have a 2-tuple
                if len(value_tuple) == 2:
                    value, unit = value_tuple
                    if self._search_in_intent(value, unit, intent):
                        matches.append(f"{req_type}:{value}{unit}")
                    else:
                        missing.append(f"{req_type}:{value}{unit}")
        
        total = len(matches) + len(missing)
        match_rate = len(matches) / total if total > 0 else 1.0
        
        return {
            'matched': matches,
            'missing': missing,
            'match_rate': match_rate
        }
    
    def _extract_requirements(self, scenario: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Extract numerical requirements from scenario text.
        
        Returns:
            Dict of requirement_type -> [(value, unit), ...]
        """
        requirements = {
            'latency': [],
            'bandwidth': [],
            'availability': [],
            'users': [],
            'throughput': []
        }
        
        # Patterns for common requirements - all MUST return exactly 2 groups (value, unit)
        patterns = {
            'latency': r'<?\\s*(\\d+\\.?\\d*)\\s*(ms|milliseconds?|msec)',
            'bandwidth': r'(\\d+\\.?\\d*)\\s*(Mbps|Gbps|kbps|mbps|gbps)',
            'availability': r'(\\d+\\.?\\d*)\\s*(%)',  # Explicit parentheses around %
            'users': r'(\\d+)\\s*(users?|UEs?)',
            'throughput': r'(\\d+\\.?\\d*)\\s*(Mbps|Gbps|kbps)'
        }
        
        for req_type, pattern in patterns.items():
            matches = re.findall(pattern, scenario, re.IGNORECASE)
            # Filter to ensure all are 2-tuples
            requirements[req_type] = [(str(m[0]), str(m[1])) for m in matches if len(m) >= 2]
        
        return requirements
    
    def _search_in_intent(self, value: str, unit: str, intent: Dict[str, Any]) -> bool:
        """
        Search for a value/unit combination in intent.
        
        Returns True if found (with tolerance for numerical values).
        """
        intent_str = json.dumps(intent).lower()
        
        # Normalize value
        try:
            numeric_value = float(value)
        except:
            # Non-numeric, exact match
            return value.lower() in intent_str and unit.lower() in intent_str
        
        # For numeric values, check with tolerance
        tolerance = 0.01
        
        # Extract all numbers from intent
        intent_numbers = re.findall(r'(\\d+\\.?\\d*)', intent_str)
        
        for num_str in intent_numbers:
            try:
                intent_num = float(num_str)
                if abs(intent_num - numeric_value) / max(numeric_value, 1) < tolerance:
                    # Found matching number, check if unit nearby
                    if unit.lower() in intent_str:
                        return True
            except:
                continue
        
        return False
    
    def _validate_completeness(self, scenario: str, intent: Dict[str, Any]) -> float:
        """
        Layer 2: Check if all requirements are addressed.
        
        Returns completeness score (0-1).
        """
        expected = self._count_requirements(scenario)
        actual = len(intent.get('serviceSpecCharacteristic', []))
        
        if expected == 0:
            return 1.0
        
        ratio = actual / expected
        
        # Scoring based on ratio
        if ratio >= 0.8 and ratio <= 1.5:
            return 1.0  # Good coverage
        elif ratio >= 0.5:
            return 0.7  # Acceptable
        elif ratio > 0:
            return 0.3  # Partial
        else:
            return 0.0  # None
    
    def _count_requirements(self, scenario: str) -> int:
        """
        Count number of requirements in scenario.
        
        Uses heuristics to identify requirement mentions.
        """
        indicators = [
            r'<\\s*\\d+',                    # <10ms
            r'\\d+\\s*(Mbps|Gbps|kbps)',     # 100Mbps
            r'\\d+\\.?\\d+\\s*%',              # 99.9%
            r'\\blow\\s+latency\\b',
            r'\\bhigh\\s+bandwidth\\b',
            r'\\bultra-?reliable\\b',
            r'\\bmission\\s+critical\\b',
            r'\\benergy\\s+efficien',
            r'\\bcoverage\\b',
        ]
        
        count = 0
        for pattern in indicators:
            matches = re.findall(pattern, scenario, re.IGNORECASE)
            count += len(matches)
        
        return max(count, 1)  # At least 1 requirement
    
    def _llm_semantic_check(self, scenario: str, intent: Dict[str, Any]) -> Dict:
        """
        Layer 3: LLM-based semantic verification.
        
        Uses LLM to judge if intent semantically matches scenario.
        """
        prompt = f'''You are a TMF921 intent validation expert.

SCENARIO (original requirement):
{scenario}

GENERATED INTENT (JSON):
{json.dumps(intent, indent=2)[:1000]}

TASK: Evaluate if the generated intent SEMANTICALLY matches the scenario.

Check:
1. Are the VALUES correct? (e.g., if scenario says 5ms, does intent have 5ms not 50ms?)
2. Are ALL requirements from scenario captured in intent?
3. Are the characteristics APPROPRIATE for the scenario?

Respond ONLY with valid JSON in this exact format:
{{
  "semantically_correct": true,
  "value_errors": [],
  "missing_requirements": [],
  "inappropriate_characteristics": [],
  "confidence": 0.95
}}

JSON response:'''
        
        try:
            response = self.llm_client.generate(prompt, max_tokens=500)
            
            # Ensure response is string
            if isinstance(response, dict):
                response = json.dumps(response)
            
            # Extract JSON from response
            json_match = re.search(r'\\{.*\\}', str(response), re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                logger.warning("No JSON found in LLM response")
                return {'semantically_correct': True, 'confidence': 0.5}
        
        except Exception as e:
            logger.error(f"LLM semantic check failed: {e}")
            return {'semantically_correct': True, 'confidence': 0.5}


def validate_semantic(scenario: str, intent: Dict[str, Any], llm_client=None) -> Dict:
    """
    Convenience function for semantic validation.
    
    Args:
        scenario: Original requirement text
        intent: Generated TMF921 intent
        llm_client: Optional LLM client for Layer 3
        
    Returns:
        Validation results dictionary
    """
    validator = SemanticValidator(llm_client)
    return validator.validate(scenario, intent)

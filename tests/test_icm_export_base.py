"""
Unit test for ICM export functionality in BaseExperiment.

Tests the ICM export logic without requiring LLM connectivity.
"""

import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.base_experiment import BaseExperiment
from src.tmf921.icm.converter import SimpleToICMConverter


def test_icm_converter_initialization():
    """Test that ICM converter is initialized when export_icm=True."""
    # Mock base experiment class
    class MockExperiment(BaseExperiment):
        def build_prompt(self, scenario):
            return "system", "user"
    
    # Test with ICM disabled
    exp_no_icm = MockExperiment(
        experiment_name="test",
        model_name="test",
        num_scenarios=1,
        export_icm=False
    )
    assert exp_no_icm.export_icm is False
    assert exp_no_icm.icm_converter is None
    
    # Test with ICM enabled
    exp_with_icm = MockExperiment(
        experiment_name="test",
        model_name="test",
        num_scenarios=1,
        export_icm=True
    )
    assert exp_with_icm.export_icm is True
    assert exp_with_icm.icm_converter is not None
    assert hasattr(exp_with_icm.icm_converter, 'convert')  # Has convert method


def test_icm_export_parameter():
    """Test that export_icm parameter is properly stored."""
    class MockExperiment(BaseExperiment):
        def build_prompt(self, scenario):
            return "system", "user"
    
    exp = MockExperiment(
        experiment_name="test",
        model_name="llama3:8b",
        num_scenarios=5,
        export_icm=True
    )
    
    assert hasattr(exp, 'export_icm')
    assert exp.export_icm is True
    assert hasattr(exp, 'icm_converter')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

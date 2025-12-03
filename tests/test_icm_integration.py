"""
Test ICM Export Integration

Tests that the ICM export functionality works correctly when integrated
with the existing experiment pipeline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.base_experiment import BaseExperiment
from src.tmf921.prompting import TMF921PromptBuilder


class TestICMExperiment(BaseExperiment):
    """Simple test experiment to verify ICM export."""
    
    def __init__(self, export_icm=False):
        super().__init__(
            experiment_name="test_icm_export",
            model_name="llama3:8b",
            num_scenarios=3,  # Just 3 for quick test
            export_icm=export_icm
        )
        self.prompt_builder = None
    
    def setup(self):
        """Setup experiment."""
        super().setup()
        self.prompt_builder = TMF921PromptBuilder(self.gst.spec)
    
    def build_prompt(self, scenario: str):
        """Build simple zero-shot prompt."""
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_zero_shot_prompt(scenario)
        return system_prompt, user_prompt


def test_without_icm():
    """Test normal operation without ICM export."""
    print("\n" + "=" * 80)
    print("TEST 1: Normal operation (no ICM export)")
    print("=" * 80)
    
    exp = TestICMExperiment(export_icm=False)
    exp.setup()
    exp.run()
    
    # Check results
    results_dir = Path("results/test_icm_export")
    assert (results_dir / "metrics_summary.json").exists(), "Metrics file should exist"
    assert not (results_dir / "checkpoint_3_icm.json").exists(), "ICM checkpoint should NOT exist"
    
    print("\n✓ Test 1 PASSED: Normal operation works without ICM")
    return True


def test_with_icm():
    """Test with ICM export enabled."""
    print("\n" + "=" * 80)
    print("TEST 2: With ICM export enabled")
    print("=" * 80)
    
    exp = TestICMExperiment(export_icm=True)
    exp.setup()
    
    # Verify ICM converter initialized
    assert exp.icm_converter is not None, "ICM converter should be initialized"
    assert exp.export_icm is True, "export_icm flag should be True"
    
    exp.run()
    
    # Check results
    results_dir = Path("results/test_icm_export")
    assert (results_dir / "metrics_summary.json").exists(), "Metrics file should exist"
    assert (results_dir / "checkpoint_3_icm.json").exists(), "ICM checkpoint SHOULD exist"
    
    # Verify ICM metrics in summary
    import json
    with open(results_dir / "metrics_summary.json") as f:
        metrics = json.load(f)
    
    assert 'icm_export' in metrics, "ICM export metrics should be present"
    assert metrics['icm_export']['enabled'] is True
    print(f"\n✓ ICM Conversions: {metrics['icm_export']['successful_conversions']}/3")
    print(f"✓ Conversion Rate: {metrics['icm_export']['conversion_rate']*100:.1f}%")
    
    print("\n✓ Test 2 PASSED: ICM export works correctly")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TESTING ICM EXPORT INTEGRATION")
    print("=" * 80)
    
    try:
        # Test 1: Without ICM
        test1_ok = test_without_icm()
        
        # Test 2: With ICM
        test2_ok = test_with_icm()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Test 1 (No ICM):  {'✓ PASSED' if test1_ok else '✗ FAILED'}")
        print(f"Test 2 (With ICM): {'✓ PASSED' if test2_ok else '✗ FAILED'}")
        
        if test1_ok and test2_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("=" * 80)
            return 0
        else:
            print("\n✗ SOME TESTS FAILED")
            print("=" * 80)
            return 1
            
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

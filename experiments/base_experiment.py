"""
Base experiment class for TMF921 intent translation.

All experiments inherit from this base class which provides
common functionality for running experiments, tracking metrics,
and saving results.
"""

import json
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.core import ScenarioDataset, GSTSpecification, TMF921Validator, OllamaClient
from tmf921.post_processing import CharacteristicNameMapper
from tmf921.utils import load_config, compute_feaci_metrics, print_feaci_metrics
from tmf921.icm.converter import SimpleToICMConverter


class BaseExperiment(ABC):
    """Abstract base class for all TMF921 intent translation experiments."""
    
    def __init__(
        self,
        experiment_name: str,
        model_name: str,
        num_scenarios: int,
        config_path: str = "config.yaml",
        results_dir: str = "results",
        export_icm: bool = False
    ):
        """
        Initialize experiment.
        
        Args:
            experiment_name: Name of the experiment
            model_name: Name of the LLM model to use
            num_scenarios: Number of scenarios to process
            config_path: Path to configuration file
            results_dir: Directory to save results
            export_icm: If True, also export ICM JSON-LD format
        """
        self.experiment_name = experiment_name
        self.model_name = model_name
        self.num_scenarios = num_scenarios
        self.config_path = config_path
        self.results_dir = Path(results_dir) / experiment_name
        self.export_icm = export_icm
        
        # Components (initialized in setup())
        self.config = None
        self.gst = None
        self.validator = None
        self.name_mapper = None
        self.client = None
        self.scenarios = None
        self.icm_converter = None if not export_icm else SimpleToICMConverter()
        
        # Results storage
        self.results = []
        
    def setup(self):
        """Initialize all components."""
        print(f"\n[1/4] Loading configuration and components...")
        
        # Load config
        self.config = load_config(self.config_path)
        
        # Load GST specification
        self.gst = GSTSpecification("gst.json")
        print(f"  [OK] Loaded GST specification: {self.gst.spec.get('name', 'Unknown')}")
        
        # Initialize validator
        self.validator = TMF921Validator(self.gst.spec)
        
        # Initialize name mapper
        self.name_mapper = CharacteristicNameMapper(self.gst.spec)
        
        # Load scenarios
        dataset = ScenarioDataset("data/val.json")
        self.scenarios = dataset.scenarios[:self.num_scenarios]
        print(f"  [OK] Loaded {len(self.scenarios)} scenarios")
        
        # Initialize LLM client
        print(f"\n[2/4] Initializing LLM client...")
        self.client = OllamaClient(model=self.model_name)
        
        if not self.client._check_connection():
            raise ConnectionError("Cannot connect to Ollama. Make sure it's running.")
        
        print(f"  [OK] Connected using model: {self.client.model}")
        
        # Create results directory
        print(f"\n[3/4] Preparing experiment...")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Results will be saved to: {self.results_dir}/")
        
    @abstractmethod
    def build_prompt(self, scenario: str) -> tuple[str, str]:
        """
        Build prompt for a scenario.
        
        Args:
            scenario: Natural language scenario
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        pass
    
    def process_scenario(self, scenario: str, idx: int) -> Dict[str, Any]:
        """
        Process a single scenario.
        
        Args:
            scenario: Natural language scenario
            idx: Scenario index (1-indexed)
            
        Returns:
            Result dictionary
        """
        print(f"\nScenario {idx}/{len(self.scenarios)}:")
        print(f"  Input: {scenario[:70]}...")
        
        try:
            # Build prompt
            system_prompt, user_prompt = self.build_prompt(scenario)
            
            # Generate
            response = self.client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2048
            )
            
            # Extract JSON
            intent_json = self.client.extract_json(response['response'])
            
            if not intent_json:
                print(f"  [FAIL] Could not extract JSON")
                return {
                    'scenario': scenario,
                    'generated_intent': None,
                    'error': 'Failed to extract JSON'
                }
            
            # Apply name correction
            corrected_intent, corrections = self.name_mapper.correct_intent(intent_json)
            
            # Validate
            validation = self.validator.validate_all(corrected_intent)
            
            # Build result
            result = {
                'scenario': scenario,
                'generated_intent': corrected_intent,
                'name_corrections': corrections,
                'validation': validation,
                'metrics': {
                    'tokens': response['tokens'],
                    'time_seconds': response['time_seconds']
                }
            }
            
            # Print status
            status = "[OK]" if validation['overall_valid'] else "[FAIL]"
            print(f"  {status} Valid: {validation['overall_valid']}, "
                  f"Corrections: {len(corrections)}, "
                  f"Time: {response['time_seconds']:.1f}s")
            
            if not validation['overall_valid'] and validation['errors']:
                print(f"    Errors: {validation['errors'][:1]}")
            
            return result
            
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return {
                'scenario': scenario,
                'generated_intent': None,
                'error': str(e)
            }
    
    def run(self):
        """Run the full experiment."""
        print(f"\n[4/4] Running {self.experiment_name} on {len(self.scenarios)} scenarios...")
        print("=" * 80)
        
        for i, scenario in enumerate(self.scenarios, 1):
            result = self.process_scenario(scenario, i)
            self.results.append(result)
            
            # Save checkpoint every 10 scenarios
            if i %10 == 0:
                self.save_checkpoint(i)
        
        # Compute and save final metrics
        self.compute_and_save_metrics()
        
        print(f"\n[SUCCESS] Experiment complete!")
        print("=" * 80 + "\n")
    
    def save_checkpoint(self, num_scenarios: int):
        """Save checkpoint in both formats if ICM export enabled."""
        # Save simple JSON format (always)
        checkpoint_file = self.results_dir / f"checkpoint_{num_scenarios}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"  [CHECKPOINT] Saved {num_scenarios} results")
        
        # Also save ICM format if enabled
        if self.export_icm and self.icm_converter:
            icm_results = []
            for result in self.results:
                if result.get('generated_intent'):
                    try:
                        icm_intent = self.icm_converter.convert(result['generated_intent'])
                        icm_results.append({
                            'scenario': result['scenario'],
                            'generated_intent_icm': icm_intent,
                            'generated_intent_simple': result['generated_intent'],
                            'validation': result.get('validation'),
                            'metrics': result.get('metrics')
                        })
                    except Exception as e:
                        print(f"    [WARNING] ICM conversion failed for result: {e}")
                        icm_results.append(result)  # Keep original
                else:
                    icm_results.append(result)
            
            icm_checkpoint_file = self.results_dir / f"checkpoint_{num_scenarios}_icm.json"
            with open(icm_checkpoint_file, 'w') as f:
                json.dump(icm_results, f, indent=2)
            print(f"  [ICM] Saved ICM format checkpoint")
    
    def compute_and_save_metrics(self):
        """Compute FEACI metrics with full transparency and honest reporting."""
        print(f"\nComputing metrics...")
        
        # HONEST COUNTS
        total_scenarios = len(self.scenarios)
        successfully_processed = len([r for r in self.results if r.get('generated_intent')])
        json_failures = total_scenarios - successfully_processed
        
        # Of successfully processed, how many are valid?
        valid_results = [r for r in self.results if r.get('validation', {}).get('overall_valid', False)]
        
        # FEACI on successfully processed only
        feaci = compute_feaci_metrics(self.results)
        
        print("\n" + "="*80)
        print("HONEST METRICS REPORTING")
        print("="*80)
        
        print(f"\nTotal Scenarios:        {total_scenarios}")
        print(f"Processing Failures:    {json_failures} ({json_failures/total_scenarios*100:.1f}%)")
        print(f"Successfully Processed: {successfully_processed} ({successfully_processed/total_scenarios*100:.1f}%)")
        if successfully_processed > 0:
            print(f"Valid Intents:          {len(valid_results)} ({len(valid_results)/successfully_processed*100:.1f}% of processed)")
        else:
            print(f"Valid Intents:          {len(valid_results)} (N/A - no scenarios processed)")
        
        print(f"\n**Overall Success Rate: {len(valid_results)}/{total_scenarios} = {len(valid_results)/total_scenarios*100:.1f}%**")
        
        # Print FEACI metrics
        print_feaci_metrics(feaci)
        
        # Save COMPREHENSIVE metrics
        metrics_summary = {
            'experiment': self.experiment_name,
            'model': self.model_name,
            'honest_counts': {
                'total_scenarios': total_scenarios,
                'processing_failures': json_failures,
                'processing_failure_rate': json_failures / total_scenarios,
                'successfully_processed': successfully_processed,
                'processing_success_rate': successfully_processed / total_scenarios,
                'valid_intents': len(valid_results),
                'validation_success_rate_on_processed': len(valid_results) / successfully_processed if successfully_processed > 0 else 0,
                'overall_success_rate': len(valid_results) / total_scenarios
            },
            'num_corrections': sum(len(r.get('name_corrections', [])) for r in self.results if r.get('name_corrections')),
            'feaci': feaci,
            'timestamp': datetime.now().isoformat()
        }
        
        summary_file = self.results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        # Save ICM summary if export enabled
        if self.export_icm and self.icm_converter:
            icm_success_count = 0
            for result in self.results:
                if result.get('generated_intent'):
                    try:
                        self.icm_converter.convert(result['generated_intent'])
                        icm_success_count += 1
                    except:
                        pass
            
            print(f"[ICM] Successfully converted {icm_success_count}/{successfully_processed} intents to ICM format")
            metrics_summary['icm_export'] = {
                'enabled': True,
                'successful_conversions': icm_success_count,
                'conversion_rate': icm_success_count / successfully_processed if successfully_processed > 0 else 0
            }
            
            # Re-save with ICM metrics
            with open(summary_file, 'w') as f:
                json.dump(metrics_summary, f, indent=2)
        
        print(f"[OK] Results saved to: {self.results_dir}/")

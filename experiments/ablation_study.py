"""
Ablation study to isolate component contributions.

Systematically removes components to determine individual contributions
to overall performance.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from datetime import datetime
from typing import Dict, List

from tmf921.core import ScenarioDataset, GSTSpecification, TMF921Validator, OllamaClient
from tmf921.prompting import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from tmf921.rag import GSTRetriever
from tmf921.post_processing import CharacteristicNameMapper
from tmf921.utils import compute_feaci_metrics


class AblationStudy:
    """
    Systematic ablation study to isolate component contributions.
    
    Tests configurations:
    1. Baseline (zero-shot, no corrections)
    2. Few-shot only
    3. RAG only
    4. Name correction only
    5. RAG + correction
    6. Few-shot + correction
    7. Full system (all components)
    """
    
    def __init__(
        self,
        model_name: str = "gpt-oss:20b-cloud",
        num_scenarios: int = 50
    ):
        self.model_name = model_name
        self.num_scenarios = num_scenarios
        self.results = {}
        
        # Initialize components
        self.gst = GSTSpecification("gst.json")
        self.validator = TMF921Validator(self.gst.spec)
        self.prompt_builder = TMF921PromptBuilder(self.gst.spec)
        self.name_mapper = CharacteristicNameMapper(self.gst.spec)
        self.client = OllamaClient(model=model_name)
        
        try:
            self.retriever = GSTRetriever()
        except:
            print("[WARNING] RAG not available - run setup_rag.py")
            self.retriever = None
    
    def run(self):
        """Run all ablation configurations."""
        
        # Load scenarios
        dataset = ScenarioDataset("data/val.json")
        scenarios = dataset.scenarios[:self.num_scenarios]
        
        print("\n" + "="*80)
        print("ABLATION STUDY")
        print("="*80)
        print(f"\nModel: {self.model_name}")
        print(f"Scenarios: {len(scenarios)}")
        print("")
        
        # Define configurations
        configs = [
            {
                'name': '1_baseline',
                'use_rag': False,
                'use_name_correction': False,
                'use_examples': False,
                'description': 'Baseline (zero-shot)'
            },
            {
                'name': '2_few_shot',
                'use_rag': False,
                'use_name_correction': False,
                'use_examples': True,
                'description': 'Few-shot (3 examples)'
            },
            {
                'name': '3_rag',
                'use_rag': True,
                'use_name_correction': False,
                'use_examples': False,
                'description': 'RAG only'
            },
            {
                'name': '4_correction',
                'use_rag': False,
                'use_name_correction': True,
                'use_examples': False,
                'description': 'Name correction only'
            },
            {
                'name': '5_rag_correction',
                'use_rag': True,
                'use_name_correction': True,
                'use_examples': False,
                'description': 'RAG + correction'
            },
            {
                'name': '6_few_shot_correction',
                'use_rag': False,
                'use_name_correction': True,
                'use_examples': True,
                'description': 'Few-shot + correction'
            },
            {
                'name': '7_full_system',
                'use_rag': True,
                'use_name_correction': True,
                'use_examples': True,
                'description': 'Full system'
            },
        ]
        
        # Run each configuration
        for config in configs:
            if config['use_rag'] and not self.retriever:
                print(f"\n[SKIP] {config['description']} (RAG not available)")
                continue
            
            print(f"\n{'='*80}")
            print(f"Running: {config['description']}")
            print(f"{'='*80}")
            
            accuracy = self.run_config(config, scenarios)
            
            self.results[config['name']] = {
                'config': config,
                'accuracy': accuracy
            }
        
        # Analyze contributions
        self.analyze_contributions()
    
    def run_config(self, config: Dict, scenarios: List[str]) -> float:
        """Run experiment with specific configuration."""
        
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(scenarios)}")
            
            # Build prompt based on config
            system_prompt = self.prompt_builder.build_system_prompt()
            
            if config['use_rag'] and self.retriever:
                retrieved = self.retriever.retrieve_for_scenario(scenario, n_results=8)
                user_prompt = self.prompt_builder.build_rag_prompt(
                    scenario, retrieved, include_examples=config['use_examples']
                )
            elif config['use_examples']:
                user_prompt = self.prompt_builder.build_few_shot_prompt(
                    scenario, EXAMPLE_SCENARIOS[:3], max_examples=3
                )
            else:
                user_prompt = self.prompt_builder.build_zero_shot_prompt(scenario)
            
            # Generate
            try:
                response = self.client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.1
                )
                
                intent = self.client.extract_json(response['response'])
                
                if not intent:
                    results.append(False)
                    continue
                
                # Apply name correction if enabled
                if config['use_name_correction']:
                    corrected, _ = self.name_mapper.correct_intent(intent)
                else:
                    corrected = intent
                
                # Validate
                validation = self.validator.validate_all(corrected)
                results.append(validation['overall_valid'])
                
            except Exception as e:
                results.append(False)
        
        # Compute accuracy
        accuracy = (sum(results) / len(results)) * 100 if results else 0
        
        print(f"\n  Accuracy: {accuracy:.1f}% ({sum(results)}/{len(results)})")
        
        return accuracy
    
    def analyze_contributions(self):
        """Analyze individual component contributions."""
        
        print("\n" + "="*80)
        print("ABLATION ANALYSIS - COMPONENT CONTRIBUTIONS")
        print("="*80)
        
        baseline = self.results.get('1_baseline', {}).get('accuracy', 0)
        
        print(f"\nBaseline (zero-shot): {baseline:.1f}%")
        
        if '2_few_shot' in self.results:
            few_shot = self.results['2_few_shot']['accuracy']
            gain = few_shot - baseline
            print(f"\n+ Few-shot examples: {few_shot:.1f}% (+{gain:.1f}%)")
        
        if '3_rag' in self.results:
            rag = self.results['3_rag']['accuracy']
            gain = rag - baseline
            print(f"+ RAG retrieval: {rag:.1f}% (+{gain:.1f}%)")
        
        if '4_correction' in self.results:
            correction = self.results['4_correction']['accuracy']
            gain = correction - baseline
            print(f"+ Name correction: {correction:.1f}% (+{gain:.1f}%)")
        
        if '5_rag_correction' in self.results:
            rag_corr = self.results['5_rag_correction']['accuracy']
            print(f"\nRAG + Correction: {rag_corr:.1f}%")
            
            # Interaction effect
            if '3_rag' in self.results and '4_correction' in self.results:
                rag_only = self.results['3_rag']['accuracy']
                corr_only = self.results['4_correction']['accuracy']
                expected_additive = rag_only + corr_only - baseline
                interaction = rag_corr - expected_additive
                
                print(f"  Expected (additive): {expected_additive:.1f}%")
                print(f"  Actual: {rag_corr:.1f}%")
                print(f"  Interaction effect: {interaction:+.1f}%")
                
                if abs(interaction) > 2:
                    if interaction > 0:
                        print(f"  [SYNERGY] Components work better together")
                    else:
                        print(f"  [INTERFERENCE] Components interfere")
        
        if '7_full_system' in self.results:
            full = self.results['7_full_system']['accuracy']
            total_gain = full - baseline
            
            print(f"\nFull System: {full:.1f}%")
            print(f"Total Improvement: +{total_gain:.1f}%")
        
        # Save results
        output_dir = Path("results") / "ablation_study"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary = {
            'model': self.model_name,
            'num_scenarios': self.num_scenarios,
            'results': self.results,
            'timestamp':datetime.now().isoformat()
        }
        
        with open(output_dir / "ablation_results.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n[OK] Results saved to: {output_dir}/")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    study = AblationStudy(
        model_name="gpt-oss:20b-cloud",
        num_scenarios=30  # Start with 30 for quick test
    )
    
    study.run()

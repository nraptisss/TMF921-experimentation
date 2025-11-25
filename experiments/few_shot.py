"""
Few-shot learning experiment.

Uses few-shot prompting with example scenarios to improve accuracy.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.prompting import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from base_experiment import BaseExperiment


class FewShotExperiment(BaseExperiment):
    """Few-shot learning experiment with example scenarios."""
    
    def __init__(self, model_name: str, num_scenarios: int, num_examples: int = 3, **kwargs):
        """
        Initialize few-shot experiment.
        
        Args:
            model_name: Name of LLM model
            num_scenarios: Number of scenarios to process
            num_examples: Number of few-shot examples to use
            **kwargs: Additional arguments for BaseExperiment
        """
        super().__init__(
            experiment_name=f"few_shot_{num_scenarios}_scenarios",
            model_name=model_name,
            num_scenarios=num_scenarios,
            **kwargs
        )
        self.num_examples = num_examples
        self.prompt_builder = None
        
    def setup(self):
        """Initialize components including prompt builder."""
        super().setup()
        
        # Initialize prompt builder
        self.prompt_builder = TMF921PromptBuilder(self.gst.spec)
        print(f"  [OK] Prompt builder initialized with {self.num_examples} examples")
    
    def build_prompt(self, scenario: str) -> tuple[str, str]:
        """
        Build few-shot prompt.
        
        Args:
            scenario: Natural language scenario
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_few_shot_prompt(
            scenario,
            EXAMPLE_SCENARIOS[:self.num_examples],
            max_examples=self.num_examples
        )
        
        return system_prompt, user_prompt


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run few-shot experiment")
    parser.add_argument("--model", default="llama3:latest", help="Model name")
    parser.add_argument("--scenarios", type=int, default=10, help="Number of scenarios")
    parser.add_argument("--examples", type=int, default=3, help="Number of few-shot examples")
    
    args = parser.parse_args()
    
    experiment = FewShotExperiment(
        model_name=args.model,
        num_scenarios=args.scenarios,
        num_examples=args.examples
    )
    
    experiment.setup()
    experiment.run()

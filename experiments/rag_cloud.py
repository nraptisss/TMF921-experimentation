"""
RAG experiment with cloud model.

Uses RAG retrieval with gpt-oss:20b-cloud for faster, more accurate translation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.prompting import TMF921PromptBuilder
from tmf921.rag import GSTRetriever
from base_experiment import BaseExperiment


class RAGCloudExperiment(BaseExperiment):
    """RAG experiment with Ollama Cloud model."""
    
    def __init__(self, model_name: str = "gpt-oss:20b-cloud", num_scenarios: int = 50, **kwargs):
        """
        Initialize RAG + Cloud experiment.
        
        Args:
            model_name: Name of cloud model
            num_scenarios: Number of scenarios to process
            **kwargs: Additional arguments for BaseExperiment
        """
        super().__init__(
            experiment_name=f"rag_cloud_{num_scenarios}_scenarios",
            model_name=model_name,
            num_scenarios=num_scenarios,
            **kwargs
        )
        self.prompt_builder = None
        self.retriever = None
        
    def setup(self):
        """Initialize components including RAG retriever."""
        super().setup()
        
        # Initialize prompt builder
        self.prompt_builder = TMF921PromptBuilder(self.gst.spec)
        
        # Initialize RAG retriever
        self.retriever = GSTRetriever()
        print(f"  [OK] RAG retriever initialized")
    
    def build_prompt(self, scenario: str) -> tuple[str, str]:
        """
        Build RAG-enhanced prompt.
        
        Args:
            scenario: Natural language scenario
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Retrieve relevant characteristics
        retrieved_chars = self.retriever.retrieve_for_scenario(scenario, n_results=8)
        
        # Build RAG prompt
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_rag_prompt(
            scenario,
            retrieved_chars,
            include_examples=True
        )
        
        return system_prompt, user_prompt
    
    def process_scenario(self, scenario: str, idx: int):
        """Override to track retrieved characteristics."""
        # Call parent method
        result = super().process_scenario(scenario, idx)
        
        # Add retrieved characteristics to result
        if result.get('generated_intent'):
            retrieved_chars = self.retriever.retrieve_for_scenario(scenario, n_results=8)
            result['retrieved_characteristics'] = [c['name'] for c in retrieved_chars]
            
            # Update print output
            if idx <= len(self.scenarios):
                retrieved_count =len(retrieved_chars)
                # Already printed, just noting for result
        
        return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG + Cloud experiment")
    parser.add_argument("--model", default="gpt-oss:20b-cloud", help="Model name")
    parser.add_argument("--scenarios", type=int, default=50, help="Number of scenarios")
    
    args = parser.parse_args()
    
    experiment = RAGCloudExperiment(
        model_name=args.model,
        num_scenarios=args.scenarios
    )
    
    experiment.setup()
    experiment.run()

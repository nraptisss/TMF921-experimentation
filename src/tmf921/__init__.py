"""TMF921 Intent Translation - Research Experimentation Suite."""

__version__ = "1.0.0"
__author__ = "TMF921 Research Team"

# Export main APIs
from .core import ScenarioDataset, GSTSpecification, TMF921Validator, OllamaClient
from .prompting import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from .rag import GSTIndexer, GSTRetriever
from .post_processing import CharacteristicNameMapper
from .utils import load_config, compute_feaci_metrics

__all__ = [
    # Core
    "ScenarioDataset",
    "GSTSpecification", 
    "TMF921Validator",
    "OllamaClient",
    # Prompting
    "TMF921PromptBuilder",
    "EXAMPLE_SCENARIOS",
    # RAG
    "GSTIndexer",
    "GSTRetriever",
    # Post-processing
    "CharacteristicNameMapper",
    # Utils
    "load_config",
    "compute_feaci_metrics",
]

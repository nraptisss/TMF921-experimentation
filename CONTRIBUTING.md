# Contributing to TMF921 Intent Translation

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

- Check existing issues first
- Provide clear description and reproduction steps
- Include environment details (Python version, OS, etc.)

### Proposing Changes

1. **Fork the repository**
2. **Create a branch** for your feature/fix
3. **Make your changes** following the code style
4. **Test your changes** thoroughly
5. **Submit a pull request**

## Development Setup

```powershell
# Clone repository
git clone https://github.com/yourusername/tmf921-intent-translation.git
cd tmf921-intent-translation

# Install in development mode
pip install -e ".[dev]"

# Setup pre-commit hooks (optional)
pre-commit install
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions/classes
- Keep functions focused and small

## Testing

Before submitting:

1. **Test your changes:**
```powershell
python test_structure.py
```

2. **Run experiments:**
```powershell
python scripts/run_experiment.py --experiment few_shot --scenarios 10
```

3. **Verify results match expected accuracy**

## Adding New Experiments

1. Create new file in `experiments/`
2. Inherit from `BaseExperiment`
3. Implement `build_prompt()` method
4. Register in `scripts/run_experiment.py`
5. Add documentation

Example:
```python
from base_experiment import BaseExperiment

class MyExperiment(BaseExperiment):
    def build_prompt(self, scenario):
        # Your implementation
        return system_prompt, user_prompt
```

## Documentation

- Update README.md if adding major features
- Add docstrings to new code
- Update API.md for new public APIs
- Include examples in TUTORIAL.md

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add zero-shot experiment implementation
fix: Correct RAG retrieval threshold issue
docs: Update API reference for new methods
test: Add unit tests for prompt builder
```

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

## Code Review

- Be respectful and constructive
- Address feedback promptly
- Ask questions if unclear

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue or contact the maintainers.

Thank you for contributing! 🎉

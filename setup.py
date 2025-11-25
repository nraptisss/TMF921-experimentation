"""Setup configuration for TMF921 Intent Translation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="tmf921-intent-translation",
    version="1.0.0",
    author="TMF921 Research Team",
    author_email="your.email@example.com",
    description="Translate natural language network requirements into TMF921-compliant Intent JSON using lightweight LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tmf921-intent-translation",
    project_urls={
        "Documentation": "https://github.com/yourusername/tmf921-intent-translation/tree/main/docs",
        "Source": "https://github.com/yourusername/tmf921-intent-translation",
        "Issues": "https://github.com/yourusername/tmf921-intent-translation/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "notebook": [
            "jupyter>=1.0",
            "matplotlib>=3.7",
            "seaborn>=0.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "tmf921-experiment=scripts.run_experiment:main",
            "tmf921-analyze=scripts.analyze_results:main",
            "tmf921-setup-rag=scripts.setup_rag:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
    keywords="tmf921 intent translation llm rag telecom network-slicing",
)

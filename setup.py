from setuptools import setup, find_packages

setup(
    name="learning-intelligence-tool",
    version="1.0.0",
    description="AI-powered Learning Intelligence Tool for course completion prediction and learner analytics",
    author="AI Kata Submission",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "click>=8.0.0",
        "joblib>=1.1.0",
        "colorama>=0.4.4",
        "tabulate>=0.8.9",
        "imbalanced-learn>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "learning-intelligence-tool=src.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

"""Setup script for CardiacYOLO."""

from setuptools import setup, find_packages
from pathlib import Path

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
REQUIREMENTS = [
    line.strip()
    for line in (ROOT / "requirements.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]

setup(
    name="cardiacyolo",
    version="1.0.0",
    description="AI-Powered Valvular Regurgitation Detection in Echocardiography",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Shih-Hsin Chen, Ting-Yi Kao, Ken-Pen Weng",
    license="MIT",
    url="https://github.com/yourusername/CardiacYOLO",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "cardiacyolo=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
)

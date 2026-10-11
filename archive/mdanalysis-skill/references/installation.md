# MDAnalysis Installation Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
   - 2.1 [Using pip (recommended)](#using-pip-recommended)
   - 2.2 [Using conda](#using-conda)
   - 2.3 [From source](#from-source)
3. [Dependencies](#dependencies)
   - 3.1 [Core dependencies](#core-dependencies)
   - 3.2 [Optional dependencies](#optional-dependencies)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.6 or higher
- NumPy >= 1.16.0
- Working C compiler (for C extensions)
- Cython >= 0.16 (for building from source)

## Installation Methods

### Using pip (recommended)

```bash
pip install MDAnalysis
```

For the bundled scripts in this skill directory, also install the common helper packages used by the included workflows:

```bash
pip install MDAnalysis numpy matplotlib pandas scipy pyyaml tqdm
```

### Using conda

```bash
conda install -c conda-forge mdanalysis
```

### From source

```bash
git clone https://github.com/MDAnalysis/mdanalysis.git
cd mdanalysis/package
python setup.py install
```

## Dependencies

### Core dependencies

```
numpy>=1.16.0
scipy
matplotlib
griddataformats
networkx
joblib>=0.12
threadpoolctl
```

### Optional dependencies

```
biopython
gsd
mmtf-python
netcdf4
parmed
scikit-learn
tqdm
```

### Development dependencies

```
cython
pytest
hypothesis
codecov
sphinx==1.8.5
sphinx_rtd_theme
```

## Development Setup

```bash
# Clone repository
git clone https://github.com/MDAnalysis/mdanalysis.git
cd mdanalysis/package

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest ../testsuite/
```

## Skill Script Verification

After dependencies are installed, the bundled script entry points should expose help successfully from the skill root:

```bash
python scripts/Plot_RDF/residue_rdf_all_pairs.py --help
python scripts/plot_orientation/water_orientation_z_analysis.py --help
python -m scripts.hb_distribution_analysis --help
```

## Troubleshooting

### Import Error: No module named 'MDAnalysis'

**Solution**: Ensure MDAnalysis is installed:
```bash
pip install MDAnalysis
```

### Cython Build Fails

**Solution**: Ensure you have a working C compiler and Cython:
```bash
pip install cython
# Install build tools (Ubuntu/Debian)
sudo apt-get install build-essential
```

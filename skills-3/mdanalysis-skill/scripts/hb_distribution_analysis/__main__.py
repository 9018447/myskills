#!/usr/bin/env python3
"""Run the hydrogen-bond analysis package as a module.

Invoke with:
    python -m scripts.hb_distribution_analysis [options]
"""

from .main import main

if __name__ == "__main__":
    main()

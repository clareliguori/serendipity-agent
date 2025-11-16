#!/usr/bin/env python3

import sys
from src.orchestrator_agent import main

if __name__ == "__main__":
    parameters_file = sys.argv[1] if len(sys.argv) > 1 else None
    results_file = sys.argv[2] if len(sys.argv) > 2 else None
    main(parameters_file, results_file)

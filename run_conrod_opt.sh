#!/bin/bash
cd /home/nenuka/.openclaw/workspace/david-version-1
timeout 120 python3 -m src.optimization.conrod_opt > conrod_opt_results_$(date +%s).txt 2>&1
echo "Optimization finished with exit code $?"
#!/bin/bash
cd /home/nenuka/.openclaw/workspace/fea_thermal
ccx -i piston_crown_thermomech 2>&1 | tee ccx.log
echo "Exit code: $?"
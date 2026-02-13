import sys
sys.path.insert(0, '.')

from src.optimization.cylinder_block_opt import compare_materials

# Run only forged aluminum (lightest)
results = compare_materials(materials=["A356_T6"])
print("Done.")
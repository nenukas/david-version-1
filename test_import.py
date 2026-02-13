try:
    import numpy
    print("numpy OK")
except ImportError:
    print("numpy missing")
try:
    import deap
    print("deap OK")
except ImportError:
    print("deap missing")
try:
    from src.engine.piston_am import PistonGeometryAM, PistonAnalyzerAM
    print("piston_am OK")
except ImportError as e:
    print(f"piston_am missing: {e}")
import os
import glob


modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = []
for f in modules:
    if os.path.basename(f) == '__init__.py':
        continue
    module = os.path.basename(f)[:-3]
    __all__.append(module)
    __import__(module, globals=globals())

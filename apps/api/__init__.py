import sys, os, pathlib

# Garante que o diretório 'apps/api' esteja no PYTHONPATH para facilitar imports "flat" (database, models, services, etc.)
_current_dir = pathlib.Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.append(str(_current_dir))

del sys, os, pathlib

# Arquivo para tornar o diretório um pacote Python 
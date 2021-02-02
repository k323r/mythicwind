import sys
from os import path

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

print(sys.path)

try:
    import mythicwind
except:
    print('failed to import mythicwind')


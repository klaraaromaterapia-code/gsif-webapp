"""Runner cu encoding corect pentru Windows"""
import sys
import os

# Fix encoding Windows
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.argv = ['certificat.py'] + sys.argv[1:]

# Import si ruleaza generatorul
sys.path.insert(0, os.path.dirname(__file__))
from certificat import main
main()

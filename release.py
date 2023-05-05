import os
import sys


def tag():
    os.system(f'git tag {sys.argv[1]}')
    os.system(f'poetry version {sys.argv[1]}')

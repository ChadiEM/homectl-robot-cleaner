import os
import sys


def release():
    target_version = sys.argv[1]

    os.system(f'poetry version {target_version}')
    os.system('git add pyproject.toml')
    os.system(f'git commit -m "Bump {target_version}"')
    os.system(f'git tag {target_version}')
    os.system('git push origin master')
    os.system(f'git push origin {target_version}')

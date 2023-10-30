import os
import sys
import tomllib


def release():
    bump_type = sys.argv[1]

    os.system(f'poetry version {bump_type}')

    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
        target_version = data['tool']['poetry']['version']

    os.system('git add pyproject.toml')
    os.system(f'git commit -m "Bump {target_version}"')
    os.system(f'git tag {target_version}')
    os.system('git push origin master')
    os.system(f'git push origin {target_version}')

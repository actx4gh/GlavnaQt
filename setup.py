from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name='GlavnaQt',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required_packages,
    entry_points={
        'console_scripts': [
            # Define any command-line scripts here
        ],
    },
)


from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='YoTech Python Application',
    version='0.1.0',
    description='YoLauncher & Stripe Python Application',
    packages=find_packages(),
    install_requires=requirements
)

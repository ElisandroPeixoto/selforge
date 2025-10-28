from setuptools import setup

with open('README.md', 'r', encoding="utf-8") as arq:
    readme = arq.read()

setup(
    name='selforge',
    version='0.3.3',
    author='Elisandro Peixoto',
    long_description=readme,
    long_description_content_type='text/markdown',
    author_email='elisandropeixoto21@gmail.com',
    packages=['selforge'],
    python_requires='<3.13',
)
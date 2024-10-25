from setuptools import setup

with open('README.md', 'r') as arq:
    readme = arq.read()

setup(
    name='sel_relays',
    version='0.1.1',
    author='Elisandro Peixoto',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='SEL relays telnet',
    description='Library to use Telnet commands in SEL relays',
    packages=['sel_relays'],
    install_requires=[]
)
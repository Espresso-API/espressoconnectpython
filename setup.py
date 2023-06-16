from setuptools import setup, find_packages
about={}
with open("README.md", "r") as readme_file:
    readme = readme_file.read()
requirements = [
        "requests>=2.18.4",
        "six>=1.11.0",
        "Crypto",
        "cryptography",
        "pycryptodome"
]
setup(
    name='espressoconnect',
    version='1.0.0.5',
    author='rg-espressoapi',
    author_email='espressoconnect@myespresso.com',
    description='Espresso API Server',
    packages=find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries"
    ],
)


from setuptools import setup

setup(
    name="wordpool",
    description="Word pool generation and tools for memory experiments",
    author="Michael V. DePalatis",
    author_email="depalati@sas.upenn.edu",
    packages=["wordpool"],
    package_data={
        "": ["*.txt", "*.json"]
    }
)

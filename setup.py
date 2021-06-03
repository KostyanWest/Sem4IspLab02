from setuptools import setup

with open("README.md", "r") as fp:
    readme = fp.read()

setup(
    name="lab2",
    version=1.0,
    description="Lab2 -- Serialization tool",
    long_description=readme,
    author="Kostyan West",
    packages=["lab2", "lab2.serializer", "lab2.serializer.serialize_tools"]
)

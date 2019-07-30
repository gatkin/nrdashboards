import setuptools


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name="nrdash",
    description="New Relic Dashboard Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gatkin/nrdashboards",
    version="0.0.2rc1",
    author="Greg Atkin",
    author_email="greg.scott.atkin@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)

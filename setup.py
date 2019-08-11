import setuptools


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name="nrdash",
    description="New Relic Dashboard Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gatkin/nrdashboards",
    version="0.1.0",
    author="Greg Atkin",
    author_email="greg.scott.atkin@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["pyyaml", "attrs", "typing", "requests", "click"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": ["nrdash=nrdash.main:main"]},
)

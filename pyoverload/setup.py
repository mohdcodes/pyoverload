from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="methodoverload",
    version="0.1.0",
    author="Mohd Arbaaz Siddiqui",
    author_email="arbaazcode@gmail.com",
    description="Python method and function overloading library with type hint resolution.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohdcodes/pyoverload",
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    install_requires=[],
    project_urls={
        "Bug Tracker": "https://github.com/mohdcodes/pyoverload/issues",
        "Documentation": "https://github.com/mohdcodes/pyoverload/blob/main/docs",
        "Source Code": "https://github.com/mohdcodes/pyoverload",
    },
)



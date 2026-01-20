from setuptools import setup, find_packages

setup(
    name="pyoverload",
    version="0.1.0",
    author="Mohd Arbaaz Siddiqui",
    author_email="arbaazcode@gmail.com",
    description="Python method and function overloading library with type hint resolution.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyoverload",
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=[],
)



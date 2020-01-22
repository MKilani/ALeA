import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ALeA",
    version="0.0.1b",
    author="Marwan Kilani",
    author_email="kilani.edu@gmail.com",
    description="Automatic Lexical Aligner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MKilani/ASeT",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["py4j"],
    install_requires=["gensim"],
    install_requires=["json"],
    python_requires='>=3.0',
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pixel-pas",
    version="0.0.1",
    author="rqueraud",
    author_email="r.queraud@catie.fr",
    description="Port activity scenario",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitpixel.satrdlab.upv.es/Erwan/pas_modelling",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
    ],
)
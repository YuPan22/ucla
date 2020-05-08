import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="binfilepy",
    version="0.1.7",
    author="Peter Li@HuLab UCSF",
    author_email="peter0306@gmail.com",
    description="Package for read/write binary file (.adibin format)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="ECG EKG binary chart adibin",
    url="https://github.com/hulab-ucsf/binfilepy.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4'
)

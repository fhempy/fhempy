from distutils.util import convert_path

import setuptools

main_ns = {}
ver_path = convert_path("FHEM/bindings/python/fhempy/lib/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="fhempy",
    version=main_ns["__version__"],
    author="Dominik Karall",
    author_email="dominik.karall@gmail.com",
    description="Python binding for FHEM to support Python modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fhempy/fhempy/",
    package_dir={"": "FHEM/bindings/python"},
    packages=setuptools.find_packages(where="FHEM/bindings/python"),
    install_requires=required,
    scripts=["FHEM/bindings/python/bin/fhempy"],
    include_package_data=True,
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

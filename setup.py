import setuptools
import re

with open('restmon/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open("./README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="rest-mon",
    version=version,
    author="itsmewulf",
    author_email="wulf.developer@gmail.com",
    description="Tool for monitoring changes in RESTful APIs quickly and easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itsmewulf/rest-mon",
    keywords="api-wrapper, http, request, api, monitor",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9'
)

from setuptools import setup
from io import open
from toddleocr import VERSION


def load_requirements(file_list=None):
    if file_list is None:
        file_list = ["requirements.txt"]
    if isinstance(file_list, str):
        file_list = [file_list]
    requirements = []
    for file in file_list:
        with open(file, encoding="utf-8-sig") as f:
            requirements.extend(f.readlines())
    return requirements


def readme():
    with open("README.md", encoding="utf-8-sig") as f:
        README = f.read()
    return README


setup(
    name="toddleocr",
    packages=["toddleocr"],
    package_dir={"toddleocr": ""},
    include_package_data=True,
    entry_points={"console_scripts": ["toddleocr= paddleocr.toddleocr:main"]},
    version=VERSION,
    install_requires=load_requirements(),
    license="Apache License 2.0",
    description="Awesome OCR toolkits based on Torch （8.6M ultra-lightweight pre-trained model, support training and deployment among server, mobile, embedded and IoT devices",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/arry-lee/ToddleOCR",
    download_url="https://github.com/arry-lee/ToddleOCR.git",
    keywords=[
        "ocr textdetection textrecognition toddleocr crnn east star-net rosetta ocrlite db chineseocr chinesetextdetection chinesetextrecognition"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
)

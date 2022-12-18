from pathlib import Path

from setuptools import find_packages, setup

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="mobrukk-pride-bruiser",
    version="1.0.0",
    author="Rohit Pagedar",
    author_email="rohitpagedar@gmail.com",
    description="PostgreSQL helper for chatbot user and image metadata tables.",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "psycopg2>=2.9",
    ],
)

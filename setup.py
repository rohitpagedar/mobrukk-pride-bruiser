from setuptools import setup

setup(
    name="mobrukk-pride-bruiser",
    version="1.0.0",
    author="Rohit Pagedar",
    author_email="rohitpagedar@gmail.com",
    description="Small PostgreSQL helper for user and image metadata tables.",
    packages=["mobrukk-pride-bruiser"],
    install_requires=[
        'setuptools',
        'twine',
        'psycopg2',
    ],
)

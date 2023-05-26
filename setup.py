from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = "__VERSION__"
name = "__NAME__"

print(f"Version: {version}")
print(f"Name: {name}")

setup(
    name=name,
    version=version,
    author='Eugenio Parodi',
    author_email='ceccopierangiolieugenio@googlemail.com',
    description='A fast, advanced log explorer',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ceccopierangiolieugenio/tlogg",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Terminals",
        "Topic :: Software Development :: User Interfaces"],
    include_package_data=False,
    packages=['tlogg','tlogg.app'],
    python_requires=">=3.8",
    install_requires=[
        'pyTermTk>=0.30.0a71',
        'appdirs',
        'pyyaml'],
    entry_points={
        'console_scripts': [
            'tlogg = tlogg:main',
        ],
    },
)
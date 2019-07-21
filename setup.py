from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nimses-adimate',
    version='1.2',
    packages=find_packages(),
    url='https://github.com/GiantTreeLP/nimses-adimate',
    license='MIT',
    author='GiantTree',
    author_email='gianttree@groundmc.net',
    description='This is a simple script that automatically clicks ads in the Nimses Android app.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Home Automation"
    ],
    install_requires=[
        'opencv-python',
        'numpy',
        'adbutils'
    ]
)

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nimses-adimate',
    version='1.0',
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
        "DEVELOPMENT STATUS :: 4 - BETA",
        "ENVIRONMENT :: CONSOLE",
        "LICENSE :: OSI APPROVED :: MIT LICENSE",
        "PROGRAMMING LANGUAGE :: PYTHON :: 3.7",
        "TOPIC :: HOME AUTOMATION"
    ],
    install_requires=[
        'opencv-python',
        'numpy',
        'adbutils'
    ]
)

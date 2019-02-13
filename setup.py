import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

requires = [
    'cx-Oracle>=7.0.0',
    'jxa-jkedra>=0.0.1',
]

setuptools.setup(
    name="rdspump-jkedra",
    version="0.0.6",
    author="Jurek Kedra",
    author_email="jurek.kedra@gmail.com",
    description="Upload/Download into Oracle Database using directory",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/jkedra/rdspump",
    packages=['rdspump'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        'rdspump': ['*.cfg'],
    },
    install_requires=requires,
    python_requires='>=3.7, <4',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'console_scripts': [
            'rdspump = rdspump.rdspump:entry_point'
        ]
    },
)

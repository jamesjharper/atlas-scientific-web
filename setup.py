
from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="atlas-scientific-web", # Replace with your own username
    version="0.0.1",
    author="James Harper",
    description="A small microservice used to host atlas-scientific devices in a I2C configuration.",
    license='GNU',
    url="https://github.com/jamesjharper/atlas-scientific-web",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "atlas-scientific-web/static": ["*.html", "*.js", "*.css"],
    },
    classifiers=[

        #  Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',

        'Operating System :: OS Independent',

        # How mature is this project ?
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',

        # Frameworks
        'Framework :: Flask'
        
        # License
        'License :: OSI Approved :: GNU General Public License (GPL)',

        
    ],
    python_requires='>=3.7',
)
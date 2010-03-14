from setuptools import setup, find_packages

setup(
    name = "dumper",
    version = "0.1",
    author = "Gareth Rushgrove",
    author_email = "gareth@morethanseven.net",
    url = "http://github.com/garethr/dumper",
    install_requires = [
        "simplejson",
        "MySQL-python",
    ],
    license = "MIT License",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    scripts = ['src/dumper/bin/dumper'],
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
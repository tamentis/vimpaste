try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from vimpaste import __version__

setup(
    name="vimpaste",
    version=__version__,
    description="Web App for vimpaste.com",
    author="Bertrand Janin",
    author_email="tamentis@neopulsar.org",
    url="http://vimpaste.com/",
    license="LICENSE.txt",
    install_requires=[
        "couchdb>=0.8",
    ],
    packages=find_packages(exclude=['ez_setup']),
    scripts=[
        "tools/vimpaste-serve",
    ],
    include_package_data=True,
    test_suite="nose.collector",
)

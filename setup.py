try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import carpse

setup(
    name="carpse",
    version=carpse.__version__,
    description="Carpse.com website",
    author="Bertrand Janin",
    author_email="tamentis@carpse.com",
    url="http://www.carpse.com/",
    license="LICENSE.txt",
    install_requires=[
        "Pylons>0.9.9",
        "Routes>=1.10,<1.12",
        "SQLAlchemy>=0.6",
        "boto>1.8",
        "PIL>=1.1.6",
        "Markdown>=2",
        "pycrypto>=2.0.0",
        "recaptcha_client>1.0.0",
        "psycopg2>2.0"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=["ez_setup"]),
    scripts=[
        "scripts/blast.sh",
        "scripts/cron_sendmails.sh",
        "scripts/sendmails.py",
        #"scripts/sendmails_py2.py"
    ],
    include_package_data=True,
    test_suite="nose.collector",
    package_data={"carpse": ["i18n/*/LC_MESSAGES/*.mo"]},
    #message_extractors={"carpse": [
    #        ("**.py", "python", None),
    #        ("templates/**.mako", "mako", {"input_encoding": "utf-8"}),
    #        ("public/**", "ignore", None)]},
    zip_safe=False,
    paster_plugins=["PasteScript", "Pylons"],
    entry_points="""
    [paste.app_factory]
    main = carpse.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)

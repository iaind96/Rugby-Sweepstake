from setuptools import find_packages, setup


setup(
    name="rugby_sweepstake",
    version="1.0.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-wtf",
        "flask-migrate",
        "flask-login",
        "email_validator"
    ],
)
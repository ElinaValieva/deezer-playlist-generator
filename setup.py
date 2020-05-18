from setuptools import setup


def readme():
    with open('README.md') as f:
        readme = f.read()
    return readme


def requirements():
    with open('requirements.txt') as f:
        requirement = f.read().splitlines()
    return requirement


version = '1.0.1'
setup(
    name='deezer-playlist-generator',
    version=version,
    description='Library for working with Deezer API for creating a playlist by your preferences in Deezer',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Valieva Elina",
    author_email="valievaelinaaa@gmail.com",
    url="https://github.com/ElinaValieva/deezer-playlist-generator",
    download_url="https://github.com/browniebroke/deezer-python/tarball/{}".format(
        version
    ),
    license="MIT",
    packages=["deezer_api"],
    install_requires=requirements(),
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

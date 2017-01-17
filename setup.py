from setuptools import find_packages, setup
setup(name="txcgate",
      version="0.1.0",
      description="Clipsal C-Gate Protocol for Twisted",
      author="Chris Burn",
      author_email='chrisburn@fastmail.net',
      platforms=["any"],
      packages=find_packages(),
      license = "GPL-3.0",
      install_requires = ['parsimonious', 'Twisted'],
)

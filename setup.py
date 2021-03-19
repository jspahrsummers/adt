from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='algebraic-data-types',
      version='0.2.1',
      author='Justin Spahr-Summers',
      author_email='justin@jspahrsummers.com',
      description='Algebraic data types for Python',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='MIT',
      url='https://github.com/jspahrsummers/adt',
      packages=['adt'],
      package_data={'adt': ['py.typed']},
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Typing :: Typed",
      ],
      install_requires=[],
      keywords='adt algebraic data types sum union tagged')

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='DotDict',
    version='0.0.1',
    author='Borre Pol Meeuwisse',
    author_email='me@borrepol.nl',
    description='Dictionary that enables referencing of items using `<dict>.<key>`.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Borrepol/DotDict',
    project_urls={
        'Bug Tracker': 'https://github.com/Borrepol/DotDict/issues'
    },
    license='GPLv3',
    packages=['DotDict'],
    install_requires=['collections', 'typing'],
)

# TODO: Change this to setup.cfg.
# https://setuptools.pypa.io/en/latest/userguide/quickstart.html#transitioning-from-setup-py-to-setup-cfg
# Counterargument(?): https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/

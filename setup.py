from codecs import open
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name='slack_responder',
    description='A slack bot that responds to regex patterns',
    long_description=long_desc,
    version='0.1.1',
    author='Josh Smeaton',
    author_email='josh.smeaton@gmail.com',
    url='https://github.com/jarshwah/slack-pattern-responder',
    license='MIT',
    platforms=['unix', 'linux', 'osx'],
    py_modules=['slack_responder'],
    install_requires=[
        'click',
        'pyyaml',
        'slackclient'
    ],
    entry_points='''
        [console_scripts]
        slack_responder=slack_responder:cli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

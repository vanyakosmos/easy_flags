from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='easy_flags',
    version='0.1.4',
    packages=['easy_flags'],
    url='https://github.com/vaniakosmos/easy_flags',
    license='MIT',
    author='Bachynin Ivan',
    author_email='bachynin.i@gmail.com',
    description='Simplified flags definition.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    keywords=[
        'flags', 'argparse'
    ],
)

from distutils.core import setup

setup(
    name='django-push-notify',
    version='0.1.0',
    author='Nathan Jhaveri',
    author_email='jhaveri@umich.edu',
    url='https://github.com/n8j/django-push-notify',
    packages=['push_notify',],
    license='MIT',
    description='Django app for sending ios push notifications',
    long_description=open('README.txt').read(),
    install_requires=['Django>=1.4.0', 'django-json-field==0.5.1',],
)


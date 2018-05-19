# https://packaging.python.org/tutorials/distributing-packages/#scripts


from setuptools import setup

setup(name='tr_downloader',
      version='0.1',
      description='A download tool for Trio',
      url='',
      author='Liu Shi',
      author_email='liushie@gmail.com',
      license='MIT',
      packages=['tr_downloader'],
      package_dir={'': 'src'},
      python_requires='~=3.6',
      entry_points={
          'console_scripts': [
              'tr_downloader=tr_downloader.tr_downloader:main_func'
          ]
      },
      install_requires=['aiohttp'],
      zip_safe=False)

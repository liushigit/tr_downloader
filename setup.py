from setuptools import setup

# https://packaging.python.org/tutorials/distributing-packages/#scripts

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
              'tr-lists=tr_downloader.tr_download_lists:main_func'
          ]
      },
      install_requires=['aiohttp'],
      zip_safe=False)

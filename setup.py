from distutils.core import setup
setup(name='pysqlitebkup',
      version='0.0.1',
      py_modules=['pysqlitebkup'],
      author='Suresh Sundriyal',
      author_email='sureshsundriyal <at> gmail <dot> com',
      url='https://github.com/sureshsundriyal/pysqlitebkup',
      keywords=['sqlite3', 'backup', 'online backup', 'pure python'],
      license="CC0 - No rights reserved.",
      description=('A pure python library that exposes the online sqlite3 '
                   'backup functions.'),
      classifiers=[
          'Topic :: Database',
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
          ],
      )

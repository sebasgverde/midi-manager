from setuptools import setup
setup(name='midi_manager',
      version='2.0',
      description='A python library to clean, process and convert midi datasets in ready to use formats like python lists, dictionaries and pickles for machine learning models',
      url='https://github.com/sebasgverde/midi-manager',
      author='Sebastian Garcia Valencia',
      author_email='sebasgverde@gmail.com',
      license='MIT',
      packages=['midi_manager'],
      python_requires='>=2.7',
      install_requires=['MIDIUtil>=1.1.3', 
                        'python-midi>=0.2.4',
                        'numpy>=1.13.0'])

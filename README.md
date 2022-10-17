# midi-manager
A python library to clean, process and convert midi datasets in ready to use formats like python lists, dictionaries and pickles for machine learning models.
It also provides the methods to transform a midi dataset in interval and data augmented variations (see this paper: [A framework to compare music generative models using automatic evaluation metrics extended to rhythm](https://sebasgverde.github.io/rnn-time-music-paper/))

See the library in PyPI: [https://pypi.python.org/pypi/midi-manager](https://pypi.python.org/pypi/midi-manager)

Intall it with:
```
pip install midi_manager
```

Note: In some cases, midi files which can be used (a lot from musescore for example), can give a problem about a "Unknown Meta MIDI Event", this is a problem in the python-midi library version 0.2.4, in this case, you can already do the next [work around](https://github.com/vishnubob/python-midi/issues/33):

- Find the dolder where you installed python-midi (like virtualenv)
- In an editor, open the file: 'lib/python2.7/site-packages/midi/fileio.py'
- from line 64, replace this code

```
if MetaEvent.is_event(stsmsg):
if MetaEvent.is_event(stsmsg):
    cmd = ord(trackdata.next())
    if cmd not in EventRegistry.MetaEvents:
        raise Warning, "Unknown Meta MIDI Event: " + `cmd`
    cls = EventRegistry.MetaEvents[cmd]
    datalen = read_varlen(trackdata)
    data = [ord(trackdata.next()) for x in range(datalen)]
    return cls(tick=tick, data=data)
```
With this other:

```
if MetaEvent.is_event(stsmsg):
    cmd = ord(trackdata.next())
    if cmd not in EventRegistry.MetaEvents:
        # raise Warning, "Unknown Meta MIDI Event: " + `cmd`
        cls = MetaEvent
    else:
        cls = EventRegistry.MetaEvents[cmd]
    datalen = read_varlen(trackdata)
    data = [ord(trackdata.next()) for x in range(datalen)]
    return cls(tick=tick, data=data)
```

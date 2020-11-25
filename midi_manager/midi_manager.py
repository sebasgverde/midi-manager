# --------------------------------------------
# Copyright (c) 2018 sebastian garcia valencia
# --------------------------------------------

import midi
import numpy as np
import os
from midiutil.MidiFile import MIDIFile
import cPickle
import pickle
import math

#########################################################
######## variations of methods with time support#########
#########################################################

standard_resoultion = 16
def midi2sequenceVectorWithTimeTuple(midifile='test.mid'):
    pattern = midi.read_midifile(midifile)
    sequence = []
    resolution_midi = pattern.resolution
    resolution = resolution_midi * 4 / standard_resoultion
    for track in pattern:
        for evt in track:
            # In this case I'm interested in time, therefore, need the note on
            # event with the final tick
            if isinstance(evt, midi.NoteOnEvent) and evt.tick > 1:
                key_in_dict = int(round(evt.tick / float(resolution)))
                sequence.append([evt.pitch,key_in_dict])

    return sequence

# tranform a list of notes [pitch, duration] in the interval changes
# [interval, duration], it uses the duration of the first note of the interval
def sequence_melody_vector_2_interval_melody_vector_with_time(note_sequence_vector):
    tensor = []

    for i in range(len(note_sequence_vector)-1):
        interval = note_sequence_vector[i+1][0] - note_sequence_vector[i][0]
        duration = note_sequence_vector[i][1]
        tensor.append([interval, duration])

    return tensor

# transform a list of notes, in 12 vectors in every tonality taking into
# account the min and max note in song, and spreding the notes optimal in the midi space

def sequence_melody_vector_2_DB12_melody_vector_with_time(sequence_vector):
    durations = [elem[1] for elem in sequence_vector]
    note_sequence_vector = [elem[0] for elem in sequence_vector]

    # min_midi = 0
    # max_midi = 127
    up_transp = 0
    down_transp = 0

    min_note = min(note_sequence_vector)
    max_note = max(note_sequence_vector)

    middle_song_point = int(math.floor((max_note - min_note)/2))+min_note

    # how far is the middle point form central C4?
    general_middle_gap = 60 - middle_song_point

    # after reaching central C how many tranpositions remains?
    remaining_transp = 11 - abs(general_middle_gap)

    if remaining_transp >= 0:
        # if is none, the extra for up
        up_transp = int(math.ceil(remaining_transp/2))
        down_transp = remaining_transp - up_transp

        if general_middle_gap < 0:
            down_transp += abs(general_middle_gap)
        else:
            up_transp += abs(general_middle_gap)
    else:
        if general_middle_gap <= 0:
            down_transp = 11
        else:
            up_transp = 11


    tensors = [note_sequence_vector]

    for i in range(down_transp):
        new_note_vector = [x-(i+1) for x in note_sequence_vector]
        tensors.append(new_note_vector)
    for i in range(up_transp):
        new_note_vector = [x+(i+1) for x in note_sequence_vector]
        tensors.append(new_note_vector)

    db12_sequences = []
    for seq in tensors:
        db12_sequences.append([[pitch, duration] for pitch, duration in zip(seq, durations)])

    return db12_sequences

class MidiLoader():
    def __init__(self, data_dir):
        self.data_dir = data_dir

        self.harmony_dict = {'2m': 0, '2M' : 1, '3m' : 2, '3M' : 3, 
                                '4J' : 4, '4aug' : 5, '5J' : 6, '6m':7, 
                                '6M' : 8, '7m' : 9, '7M' : 10, '8' : 11}
        self.time_notation_dict = {'64th':1, '32th':2, '16th':3, '8th':4, 'quarter':5, 'half':6, 'whole':7 }
        self.time_dict = {'0.0625' : 1, '0.125' : 2, '0.25' : 3, '0.5' : 4, '1.0': 5, '2.0': 6, '4.0': 7}
        self.midi_note_dict = {"C0" : 0, "C#0" : 1, "D0" : 2,
                                "D#0" : 3, "E0" : 4, "F0" : 5,
                                "F#0" : 6, "G0" : 7, "G#0" : 8,
                                "A0" : 9, "A#0" : 10, "B0" : 11,
                                "C1" : 12, "C#1" : 13, "D1" : 14,
                                "D#1" : 15, "E1" : 16, "F1" : 17,
                                "F#1" : 18, "G1" : 19, "G#1" : 20,
                                "A1" : 21, "A#1" : 22, "B1" : 23,
                                "C2" : 24, "C#2": 25, "D2" : 26,
                                "D#2" : 27, "E2" : 28, "F2" : 29,
                                "F#2" : 30, "G2" : 31, "G#2" : 32,
                                "A2" : 33, "A#2" : 34, "B2" : 35,
                                "C3" : 36, "C#3" : 37, "D3" : 38,
                                "D#3" : 39, "E3" : 40, "F3" : 41,
                                "F#3" : 42, "G3" : 43, "G#3" : 44,
                                "A3" : 45, "A#3" : 46, "B3" : 47,
                                "C4" : 48, "C#4" : 49, "D4" : 50,
                                "D#4" : 51, "E4" : 52, "F4" : 53,
                                "F#4" : 54, "G4" : 55, "G#4" : 56,
                                "A4" : 57, "A#4" : 58, "B4" : 59,
                                "C5" : 60, "C#5" : 61, "D5" : 62,
                                "D#5" : 63, "E5" : 64, "F5" : 65,
                                "F#5" : 66, "G5" : 67, "G#5" : 68,
                                "A5" : 69, "A#5" : 70, "B5" : 71,
                                "C6" : 72, "C#6" : 73, "D6" : 74,
                                "D#6" : 75, "E6" : 76, "F6" : 77,
                                "F#6" : 78, "G6" : 79, "G#6" : 80,
                                "A6" : 81, "A#6" : 82, "B6" : 83,
                                "C7" : 84, "C#7" : 85, "D7" : 86,
                                "D#7" : 87, "E7" : 88, "F7" : 89,
                                "F#7" : 90, "G7" : 91, "G#7" : 92,
                                "A7" : 93, "A#7" : 94, "B7" : 95,
                                "C8" : 96, "C#8" : 97, "D8" : 98,
                                "D#8" : 99, "E8" : 100, "F8" : 101,
                                "F#8" : 102, "G8" : 103, "G#8" : 104,
                                "A8" : 105, "A#8" : 106, "B8" : 107,
                                "C9" : 108, "C#9" : 109, "D9" : 110,
                                "D#9" : 111, "E9" : 112, "F9" : 113,
                                "F#9" : 114, "G9" : 115, "G#9" : 116,
                                "A9" : 117, "A#9" : 118, "B9" : 119,
                                "C10" : 120, "C#10" : 121, "D10" : 122,
                                "D#10" : 123, "E10" : 124, "F10" : 125,
                                "F#10" : 126, "G10" : 127}
        self.inverse_time_notation_dict = dict(zip(self.time_notation_dict.values(), self.time_notation_dict))
        self.inverse_time_dict = dict(zip(self.time_dict.values(), self.time_dict))
        self.inverse_midi_note_dict = dict(zip(self.midi_note_dict.values(), self.midi_note_dict))
        self.inverse_harmony_dict = dict(zip(self.harmony_dict.values(), self.harmony_dict))
        # {'semifusa', 'fusa', 'semicorchea', 'corchea', 'negra', 'blanca', 'redonda'}

    # concatenates the vectors in a list in only one list
    def list_of_vectors_2_vector(self, vector_list):
        # # this looks very elegant but don't fall in temptation is absurdly
        # # inefficient for big list
        # new_vector2 = reduce(lambda x,y:x+y,vector_list)

        new_vector = []
        for x in vector_list:
            new_vector += x

        return new_vector

    # converts a midi file in an array with the notes (monofonic, if the midi
    # is polifonic it sequence the notes)
    # https://github.com/vishnubob/python-midi
    def midi2sequenceVector(self, midifile='test.mid'):
        pattern = midi.read_midifile(midifile)
        sequence = []

        for track in pattern:
            for evt in track:
                # the and evt.tick == 1 is to not duplicate the notes, basically every note has
                # tick 1 with the specific velocity (dinamyc) and after the time passes,
                # the same note with the apropiate tick and velocity 0, as I only take here
                # the pitch I use any of them, but not both
                if isinstance(evt, midi.NoteOnEvent) and evt.tick == 1:
                    sequence.append(evt.pitch)

        return sequence

    # The Resolution is also known as the Pulses per Quarter note (PPQ) (pulsos por nota negra). 
    # It analogous to Ticks per Beat (TPM).
    # So I can use the resolution and the tick in noteOffEvent to know the time
    def midi2sequenceVectorWithTime(self, midifile='test.mid'):
        pattern = midi.read_midifile(midifile)
        sequence = []
        resolution = pattern.resolution
        for track in pattern:
            for evt in track:
                if isinstance(evt, midi.NoteOnEvent):
                    sequence.append(evt.pitch)
                if isinstance(evt, midi.NoteOffEvent):
                    key_in_dict = str(evt.tick/float(resolution))
                    sequence.append(self.time_dict[key_in_dict])

        return zip(sequence[0::2], sequence[1::2])

    def wordsTxt2Vector(self, file):
        with open(file, 'r') as content_file:
            content = content_file.read()

        # windows use '\r\n' so first I convert it to unix like
        # but I better use \r, cause the \n is a problem when I want
        # to write a metadata.tsv file
        # content.replace('\r\n', '\r')       
        # if is linux 
        # content.replace('\n', '\r')   
        #now, I don't want a special embedding for word+new line
        # so I transfor the new line in another word
        # content.replace('\r', ' \r ') 
        # better in only 2 lines, and to avoid problems that some
        # software doesn't recognize \r as line
        content = content.replace('\r\n', ' +++***newline***+++ ')       
        content = content.replace('\n', ' +++***newline***+++ ')     

        # replace the EOF '' character
        # after see a generated text like this  Todos encontraba Quisiera +++***EOF***+++ jamas 
        # i think is better exclude the character for now, could be usefull if you use multiple
        # documents to notice they change but now is just garbage
        words_list = [x if x!='' else '+++***EOF***+++' for x in content.split(' ')]
        return filter(lambda a: a != '+++***EOF***+++', words_list)


    def read_dataset_words(self):
        tensor = []
        for words_file in os.listdir(self.data_dir):
            tensor += self.wordsTxt2Vector(self.data_dir+ '/' +words_file)

        return tensor       

    def text_words_folder_2_list_of_sequences(self):
        tensor = []
        for words_file in os.listdir(self.data_dir):
            print words_file            
            tensor.append(self.wordsTxt2Vector(self.data_dir+ '/' +words_file))

        return tensor 

    # converts a folder with midis to a vector with the sequence of all notes
    def read_dataset_as_melody(self):
        tensor = []
        for midifile in os.listdir(self.data_dir):
            print midifile
            tensor += self.midi2sequenceVector(self.data_dir+ '/' +midifile)

        return tensor

    # returns a list, every position is one of the songs as a sequence of notes
    # very usefull for statistics and testing
    def midi_folder_2_list_of_sequences(self):
        tensor = []
        for midifile in os.listdir(self.data_dir):
            print midifile            
            tensor.append(self.midi2sequenceVector(self.data_dir+ '/' +midifile))

        return tensor

    # tranform a list of notes in the interval changes
    def sequence_melody_vector_2_interval_melody_vector(self, note_sequence_vector):
        tensor = []

        for i in range(len(note_sequence_vector)-1):
            tensor.append(note_sequence_vector[i+1] - note_sequence_vector[i])

        return tensor

    def create_dict_x_y_from_list(self, tensor):
        
        #creates a dict with unique elements which can be used to transform to notes        
        notes_dict = dict(enumerate(sorted(set(self.list_of_vectors_2_vector(tensor)))))

        # erase the last element for x and the first for y
        xdata = [a[:-1] for a in tensor]
        ydata = [a[1:] for a in tensor]

        xdata = self.list_of_vectors_2_vector(xdata)
        ydata = self.list_of_vectors_2_vector(ydata)

        return {'notes_dict' : notes_dict, 'x' : xdata, 'y' : ydata}

    # transform a list of notes, in 12 vectors in every tonality taking into
    # account the min and max note in song, and spreding the notes optimal in the midi space
    def sequence_melody_vector_2_DB12_melody_vector(self, note_sequence_vector):
        min_midi = 0
        max_midi = 127
        up_transp = 0
        down_transp = 0

        min_note = min(note_sequence_vector)
        max_note = max(note_sequence_vector)

        middle_song_point = int(math.floor((max_note - min_note)/2))+min_note

        # how far is the middle point form central C4?
        general_middle_gap = 60 - middle_song_point

        # after reaching central C how many tranpositions remains?
        remaining_transp = 11 - abs(general_middle_gap)

        if remaining_transp >= 0:
            # if is none, the extra for up
            up_transp = int(math.ceil(remaining_transp/2))
            down_transp = remaining_transp - up_transp

            if general_middle_gap < 0:
                down_transp += abs(general_middle_gap)
            else:
                up_transp += abs(general_middle_gap)
        else:
            if general_middle_gap <= 0:
                down_transp = 11
            else:
                up_transp = 11


        tensors = [note_sequence_vector]

        for i in range(down_transp):
            new_note_vector = [x-(i+1) for x in note_sequence_vector]
            tensors.append(new_note_vector)
        for i in range(up_transp):
            new_note_vector = [x+(i+1) for x in note_sequence_vector]
            tensors.append(new_note_vector)

        return tensors

    # transform a list of songs (as note list), in a version with the songs
    # in every tonality
    def song_list_vector_2_DB12_melody(self):
        return 0
    # this 2 methods should transform a folder of midis in sequence vector
    # for now I will use the pickles
    def read_dataset_as_interval_melody(self):
        return 0

    def read_dataset_as_DB12_melody(self):
        return 0

    def read_dataset_as_melody_with_time(self):
        tensor = []
        for midifile in os.listdir(self.data_dir):
            tensor += self.midi2sequenceVectorWithTime(self.data_dir+ '/' +midifile)

        return tensor

    def read_piano_roll_dataset_as_melody(self):
        tensor = []
        datasets = cPickle.load(file(self.data_dir))
        for dataset in datasets:
            for song in datasets[dataset]:
                for notes in song:                
                    if len(notes) > 0:
                        # I use -1 cause usually the melody in songs corresponds to the highest notes
                        tensor.append(notes[-1])
                    # I ignore len(notes) = 0, that [] is for the time, which isn't important here

        return tensor

    def read_piano_roll_dataset_as_harmony(self):
        tensor = []
        datasets = cPickle.load(file(self.data_dir))
        for dataset in datasets:
            for song in datasets[dataset]:
                for notes in song:

                    if len(notes) > 1:
                        # only use the 12 fundamental harmonies, it reduce a lot the vocab size
                        # and is what i want to study, but harmonies are far less interesting
                        tensor += (notes[0], abs(notes[1]-notes[0])%12)
                    elif len(notes) > 0:
                        # if only one note, use the octave, 0 is the octave, cause abs(difference)%12 is 0
                        tensor += (notes[0], 0)
                    # I ignore len(notes) = 0, that [] is for the time, which isn't important here

        return zip(tensor[0::2], tensor[1::2])

    def read_piano_roll_dataset_as_melody_with_time(self):
        tensor = []
        datasets = cPickle.load(file(self.data_dir))
        for dataset in datasets:
            for song in datasets[dataset]:

                # only use songs with important number of silences so they have
                # enough time information    
                # if [] in song:             
                if song.count([]) > 100 :
                    for notes in song:                
                        if len(notes) > 0:
                            # I use -1 cause usually the melody in songs corresponds to the highest notes
                            # by defect I use eight notes (JSB chorales are quarter note so I don't use that
                            # dataset)
                            tensor += (notes[-1], 4)
                        else:

                            # if the first element is [] ignore it
                            try: 
                                # max whole notes, no silences or legatos supported 
                                if tensor[-1] < 7:                    
                                    tensor[-1] += 1

                            except:
                                print 'initial silence found'
                            # I ignore len(notes) = 0, that [] is for the time, which isn't important here
   
        return zip(tensor[0::2], tensor[1::2])

class MidiWriter():

    # https://code.google.com/archive/p/midiutil/
    def sequenceVector2midiMelody(self, seqVector, file_dir):
        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        for note in seqVector:
            # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            MyMIDI.addNote(0,0,note,time,1,100)
            time = time + 1

        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()

        #save also as pickle
        pickle.dump(seqVector, open(file_dir + '.p','wb'))

    def sequenceVectorInterval2midiMelody(self, seqVector, file_dir, first_note):
        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        pickle_sequence = []

        current_note = first_note
        MyMIDI.addNote(0,0,current_note,time,1,100)
        pickle_sequence.append(current_note)
        print current_note
        time = time + 1        
        for interval in seqVector:
            # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            current_note += interval
            print current_note
            if current_note > 12:
                MyMIDI.addNote(0,0,current_note,time,1,100)
                pickle_sequence.append(current_note)
            else:
                current_note = 60
            time = time + 1


        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()

        #save also as pickle
        pickle.dump(pickle_sequence, open(file_dir + '.p','wb'))        

    def sequenceVector2midiMelodyWithTime(self, seqVector, file_dir):
        self.time_dict = {'0.0625' : 1, '0.125' : 2, '0.25' : 3, '0.5' : 4, '1.0': 5, '2.0': 6, '4.0': 7}
        self.inverse_time_dict = dict(zip(self.time_dict.values(), self.time_dict))
       
        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        for note in seqVector:
            try:
                # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
                duration = float(self.inverse_time_dict[note[1]])
                MyMIDI.addNote(0,0,note[0],time, duration,100)
                print (time, duration)
                time = time + duration

            except:
                MyMIDI.addNote(0,0,note,time,1,100)
                time = time + 1
        
        # # some testing                
        # MyMIDI.addNote(0,0,60,0,1,100)
        # MyMIDI.addNote(0,0,60,1,1,100)
        # MyMIDI.addNote(0,0,60,2,0.5,100)
        # MyMIDI.addNote(0,0,60,2.5,2,100)
        # deinterleave = True
        # time = 0
        # duration = 1
        # MyMIDI.addNote(0,0,60,time,duration,100)
        # time = 0.5
        # MyMIDI.addNote(0,0,62,time,duration,100)        

        # MyMIDI.addNote(0,0,60,0,1,100)
        # MyMIDI.addNote(0,0,60,0,1,100)
        # MyMIDI.addNote(0,0,60,0,1,100)
        # MyMIDI.addNote(0,0,60,0,1,100)
        # MyMIDI.addNote(0,0,60,0,1,100)


        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()        

    def sequenceVector2midiWithTime(self, seqVector, file_dir):
        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        for note in seqVector:
            # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            MyMIDI.addNote(0,0,note,time,1,100)
            time = time + 1

        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()


    def sequenceVector2midiHarmony(self, seqVector, file_dir):
        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        for harmonies in seqVector:
            # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            # this use all the notes
            # for note in notes:
            #     MyMIDI.addNote(0,0,note,time,2,100)
            
            try:
                MyMIDI.addNote(0,0,harmonies[0],time,2,100)
                # if harmony is 0, add 12 for octave, else add the harmony
                MyMIDI.addNote(0,0,harmonies[0]+12 if harmonies[1] == 0 else harmonies[0]+harmonies[1],time,2,100)
            except:
                MyMIDI.addNote(0,0,harmonies,time,2,100)
                MyMIDI.addNote(0,0,harmonies+12,time,2,100)

            time = time + 1

        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()          

    # converts an array of notes in a midi file where all the are whole notes in 120 tempo
    def sequenceVector2midi(self, seqVector):
        # Instantiate a MIDI Pattern (contains a list of tracks)
        pattern = midi.Pattern()
        # Instantiate a MIDI Track (contains a list of MIDI events)
        track = midi.Track()
        # Append the track to the pattern
        pattern.append(track)

        for note in seqVector:
            # Instantiate a MIDI note on event, append it to the track
            on = midi.NoteOnEvent(tick=0, velocity=20, pitch=note)
            track.append(on)
            # Instantiate a MIDI note off event, append it to the track
            off = midi.NoteOffEvent(tick=220, pitch=note)
            # seems 220 is the default resolution and 120 the tempo, so
            # if I want whole notes I used 220 (120 beats per minute every one
            # 220 ticks)
            track.append(off)
        # Add the end of track event, append it to the track
        eot = midi.EndOfTrackEvent(tick=1)
        track.append(eot)
        # Print out the pattern
        print pattern
        # Save the pattern to disk
        midi.write_midifile("example.mid", pattern)  


    # transforms the first song in a pianoroll dataset in a midi file with harmonies
    def pianoRoll2midi(selfn, pianoroll_pickle_uri):
        dataset = cPickle.load(file(pianoroll_pickle_uri))
        seqVector = dataset['train'][0]
        file_dir = 'test.mid'

        MyMIDI = MIDIFile(1)
        track = 0 
        time = 0
        MyMIDI.addTrackName(track,time,"Sample Track") 
        MyMIDI.addTempo(track,time,120)
        time = 0
        for notes in seqVector:
            # MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            # this use all the notes
            # for note in notes:
            #     MyMIDI.addNote(0,0,note,time,2,100)
            MyMIDI.addNote(0,0,notes[0],time,2,100)
            if len(notes) > 1:
                MyMIDI.addNote(0,0,notes[1],time,2,100)
            time = time + 1

        binfile = open(file_dir, 'wb') 
        MyMIDI.writeFile(binfile) 
        binfile.close()

    def sequenceVector2wordsText(self, seqVector, output_uri):
        with open(output_uri, 'w') as content_file:
            for word in seqVector:
                if word == '+++***newline***+++':
                    word = '\n'
                try:
                    content_file.write(word + ' ')        
                except:
                    content_file.write(str(word) + ' ')        

#--------------------------------

# #testing
# # this segment reads midis and then export them, to check how well is the parsing done
# song = 'name.mid'
# loader = MidiLoader('/midiFolder', 1, 1, 'test')
# writer = MidiWriter()
# folder = 'midis/'
 

# import pickle
# # to read pickle.load(open("save.p", "rb"))

# # tensor = loader.read_dataset_as_melody()
# # pickle.dump(tensor, open('train.p','wb'))

# tensor = loader.midi_folder_2_list_of_sequences()
# pickle.dump(tensor, open('train_song_list.p','wb'))

# # individual file   
# midi_file = folder + song 
# seq = loader.midi2sequenceVector(midi_file)
# writer.sequenceVector2midiMelody(seq, song)

# # whole folder 
# for song in os.listdir(folder):
#     midi_file = folder + song 
#     seq = loader.midi2sequenceVector(midi_file)
#     writer.sequenceVector2midiMelody(seq, song)

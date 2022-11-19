#!/usr/bin/python
# This class handles the parsing of a midi file and builds a markov
# chain from it.

import hashlib
import mido
import argparse
from sklearn.cluster import KMeans
import numpy as np

from markov_chain import MarkovChain

class Parser:

    def __init__(self, filename, verbose=False):
        """
        This is the constructor for a Serializer, which will serialize
        a midi given the filename and generate a markov chain of the
        notes in the midi.
        """
        self.filename = filename
        # The tempo is number representing the number of microseconds
        # per beat.
        self.tempo = None
        # The delta time between each midi message is a number that
        # is a number of ticks, which we can convert to beats using
        # ticks_per_beat.
        self.ticks_per_beat = None
        self.Meters=[]
        self.markov_chain = MarkovChain()
        self.NoteRange = [127, 0]
        self.meternum=0
        self._parse(verbose=verbose)
        self.kmeans=None
        self.Dic=None
        self.Kmeans()
        #self.markov_chain.debug()

    def _parse(self, verbose=False):
        """
        This function handles the reading of the midi and chunks the
        notes into sequenced "chords", which are inserted into the
        markov chain.
        """
        midi = mido.MidiFile(self.filename)
        self.ticks_per_beat = midi.ticks_per_beat
        time_per_meter = midi.ticks_per_beat * 4
        for track in midi.tracks:
            Meters=[]
            current_chunk = []
            Meanfultrace=False
            Per_beat = 0
            for message in track:
                if verbose:
                    print(message)
                if message.type == "set_tempo":
                    self.tempo = message.tempo
                elif message.type == "note_on" or message.type =="note_off":
                    Meanfultrace=True
                    Velocity=message.velocity
                    if message.type=="note_off":
                        Velocity=0
                    Per_beat+=message.time
                    self.NoteRange[0] = min(message.note, self.NoteRange[0])
                    self.NoteRange[1] = max(message.note, self.NoteRange[1])
                    if Per_beat<time_per_meter or Velocity==0:
                        current_chunk.append((message.note,Velocity,message.time))
                    else:
                        Per_beat-=time_per_meter
                        Meters.append(current_chunk)
                        current_chunk = []
                        current_chunk.append((message.note,Velocity,message.time))
            if (not Meanfultrace):
                continue
            Meters.append(current_chunk)
            self.Meters.append(Meters)
            self.meternum=max(len(Meters),self.meternum)

    def Kmeans(self):
        K_meter=[]
        Krange=4
        for Chunk in range(self.meternum):
            t=[0] * (self.NoteRange[1] - self.NoteRange[0] + 1)
            for trace in range(len(self.Meters)):
                for message_tuple in self.Meters[trace][Chunk]:
                    t[message_tuple[0]-self.NoteRange[0]]+=1
            K_meter.append(t)
        K_meter=np.array(K_meter)
        self.kmeans = KMeans(n_clusters=int(len(K_meter)/Krange+1), random_state=0).fit(K_meter)
        Map=self.kmeans.labels_
        Dic=[[] for i in range(int(len(K_meter)/Krange+1))]
        for i in range(len(K_meter)):
            Dic[Map[i]].append(i)
        self.Dic=Dic
        for i in range(len(Map)-1):
            self.markov_chain.add(Map[i],Map[i+1])

    def get_chain(self):
        return self.markov_chain

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="The midi file input")
    args = parser.parse_args()
    print(Parser(args.input_file, verbose=False).get_chain())
    print('No issues parsing {}'.format(args.input_file))
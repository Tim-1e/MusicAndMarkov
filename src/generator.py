#!/usr/bin/python
# This class handles the generation of a new song given a markov chain
# containing the note transitions and their frequencies.

from myparser import Parser

import random
import mido

class Generator:

    def __init__(self, Parser):
        self.Parser = Parser

    @staticmethod
    def load(Parser):
        #assert isinstance(markov_chain, MarkovChain)
        return Generator(Parser)

    def _tuple_to_messages(self, tuple):
        return mido.Message("note_on", note = tuple[0],velocity = tuple[1],
                     time=tuple[2]),


    def generate(self, filename):
        with mido.midifiles.MidiFile() as midi:
            Chunk=self.Parser.Meters
            Dic=self.Parser.Dic
            Markev=[]
            last_meter = None
            for i in range(100):
                new_meter = self.Parser.markov_chain.get_next(last_meter)
                Markev.append(new_meter)
                last_meter = new_meter
            for trace in range(len(Chunk)):
                track = mido.MidiTrack()
                for meter in Markev:
                    MeterInKmean = Dic[meter]
                    SelectMeter=Chunk[trace][MeterInKmean[random.randint(0,len(MeterInKmean)-1)]]
                    for message_tuple in SelectMeter:
                        track.extend(self._tuple_to_messages(message_tuple))
                midi.tracks.append(track)
            midi.save(filename)

    def generate_test(self, filename):
        with mido.midifiles.MidiFile() as midi:
            Chunk=self.Parser.Meters
            for trace in range(len(Chunk)):
                track = mido.MidiTrack()
                for meter in range(self.Parser.meternum):
                    SelectMeter=Chunk[trace][meter]
                    for message_tuple in SelectMeter:
                        track.extend(self._tuple_to_messages(message_tuple))
                midi.tracks.append(track)
            midi.save(filename)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        loadParser = Parser(sys.argv[1])
        Generator.load(loadParser).generate(sys.argv[2])
        print('Generated markov chain')
    else:
        print('Invalid number of arguments:')
        print('Example usage: python generator.py <in.mid> <out.mid>')

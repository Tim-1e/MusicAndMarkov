#!/usr/bin/python
# This class handles the generation of a new song given a markov chain
# containing the note transitions and their frequencies.

from markov_chain import MarkovChain

import random
import mido

class Generator:

    def __init__(self, markov_chain):
        self.markov_chain = markov_chain

    @staticmethod
    def load(markov_chain):
        #assert isinstance(markov_chain, MarkovChain)
        return Generator(markov_chain)

    def _note_to_messages(self, notes):
        message = []
        for note in notes.note:
            message.append(
                mido.Message('note_on', note = note[0],velocity = note[1],
                         time=0),
                )
        for (i,note) in enumerate(notes.note):
            if i==0:
                message.append(
                    mido.Message('note_off', note = note[0],velocity = 0,
                            time=notes.duration)
                )
            else:
                message.append(
                    mido.Message('note_off', note = note[0],velocity = 0,
                            time=0)
                )
        return message
        # return [
        #     mido.Message('note_on', note = note,velocity = 127,
        #                  time=0),
        #     mido.Message('note_off', note = note,velocity = 0,
        #                  time=note.duration)
        #     # mido.Message('note_on', note = note.note[0],velocity = note.note[1],time = note.duration)
        # ]

    def generate(self, filename):
        with mido.midifiles.MidiFile() as midi:
            for one_chain in self.markov_chain:
                track = mido.MidiTrack()
                last_note = None
                # self.markov_chain.debug()
                # Generate a sequence of 100 notes
                for i in range(1000):
                    new_note = one_chain.get_next(last_note)
                    # print(last_note,"==>",new_note)
                    track.extend(self._note_to_messages(new_note))
                    last_note = new_note.note
                midi.tracks.append(track)
            midi.save(filename)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        # Example usage:
        # python generator.py <in.mid> <out.mid>
        from myparser import Parser
        chain = Parser(sys.argv[1]).get_chain()
        Generator.load(chain).generate(sys.argv[2])
        print('Generated markov chain')
    else:
        print('Invalid number of arguments:')
        print('Example usage: python generator.py <in.mid> <out.mid>')

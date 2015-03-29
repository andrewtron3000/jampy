"""
Csound.py - A set of Python classes for Csound instruments and scores
using the CSD Csound input file format.
"""

import string, types, os, sys, math
from random import uniform
from pitch_table import pitch_table

AMPLITUDE_MAXIMUM = math.pow(2, 15) - 1

def tabjoin(*args):
    return string.join(map(str, args), '\t')

def if_none(test_value, result_value):
    if test_value == None:
        return result_value
    else:
        return test_value

def parse_pitch(pitch):
    if type(pitch) == types.StringType:
        offset = 0
        if '+' in pitch:
            pitch, offset = pitch.split('+')
            offset = float(offset)
        hz = pitch_table.get(pitch)
        if not hz:
            print 'Error: Unknown pitch name: "%s"' % (pitch)
            sys.exit(1)
        return hz + offset
    else:
        return pitch

def convert_amplitude(amplitude):
    return min(amplitude * AMPLITUDE_MAXIMUM, AMPLITUDE_MAXIMUM)

# Parent instrument class:

class Instrument:
    serial_number = 1
    def __init__(self):#, number):
        #self.number = number
        self.number = Instrument.serial_number
        Instrument.serial_number += 1

    def orchestra(self):#, number):
        output, opcodes = self.opcodes()
        result = '\tinstr\t%d\n' % (self.number)
        result += opcodes + '\n'
        result += '\tout\t%s\n\tendin\n' % (output)
        return result

# Individual instruments:

class oscil(Instrument):
    def opcodes(self):
        return 'a1*k1', 'k1\tlinseg\t0, .012, 1, p3 - 0.036, 1, .024, 0\na1\toscil\tp4, p5, 1'

    def note(self, start, duration, frequency, amplitude=.5):
        return tabjoin('i', self.number, start, duration,
                       convert_amplitude(amplitude), parse_pitch(frequency))

class buzz(Instrument):
    def __init__(self, number_of_harmonics=10):
        Instrument.__init__(self)
        self.number_of_harmonics = number_of_harmonics

    def opcodes(self):
        return 'a1', 'a1\tbuzz\tp4, p5, p6, 1'
    
    def note(self, start, duration, frequency, amplitude=.5,
             number_of_harmonics=None):
        return tabjoin('i', self.number, start, duration,
                       convert_amplitude(amplitude), parse_pitch(frequency),
                       if_none(number_of_harmonics, self.number_of_harmonics))

# class pluck(Instrument):
#     def __init__(self):
#         # todo

#     def opcodes(self):
#           iplk = 0.75
#   kamp = 30000
#   icps = 220
#   kpick = 0.75
#   krefl = 0.5

#         return 'a1', 'a1 wgpluck2 iplk, kamp, icps, kpick, krefl'

class voice(Instrument):
    def __init__(self, vowel=1):
        Instrument.__init__(self)
        self.vowel = vowel

    def opcodes(self):
        #return 'a1', 'a1\tfmvoice\tp4, p5, p6, p7, p8, p9'
        #return 'a1', 'a1\tfmvoice\t.5, 110, 1, 0, 0.005, 6'
        #pgm = 'asrc\twgpluck2\t0.75, p4, p5, 0.75, 0.5\n'
        pgm = "asrc  voice p4, p5, p6, 0.488, 0, 1, 1, 2"
        #pgm += 'a1 reverb asrc, 1.5'
        return 'asrc', pgm
        #return 'a1', 'a1\twgpluck2\t0.75, 30000, 220, 0.75, 0.5'
        #return 'apluck', 'iplk = 0.75\nkamp = 30000\nicps = 220\nkpick = 0.75\nkrefl = 0.5\napluck wgpluck2 iplk, kamp, icps, kpick, krefl'

    def note(self, start, duration, frequency, amplitude = .5,
             vowel=None, spectral_tilt=None, vibrato_depth=None, vibrato_rate=None):
        return tabjoin('i', self.number, start, duration,
                       convert_amplitude(amplitude * 2.0), parse_pitch(frequency),
                       if_none(vowel, self.vowel))

class fmvoice(Instrument):
    def __init__(self, vowel=1, spectral_tilt=0, vibrato_depth=0.005, vibrato_rate=6):
        Instrument.__init__(self)
        self.vowel = vowel
        self.spectral_tilt = spectral_tilt
        self.vibrato_depth = vibrato_depth
        self.vibrato_rate = vibrato_rate

    def opcodes(self):
        #return 'a1', 'a1\tfmvoice\tp4, p5, p6, p7, p8, p9'
        #return 'a1', 'a1\tfmvoice\t.5, 110, 1, 0, 0.005, 6'
        pgm = 'asrc\twgpluck2\t0.75, p4, p5, 0.75, 0.5\n'
        pgm += 'a1 reverb asrc, 1.5'
        return 'a1', pgm
        #return 'a1', 'a1\twgpluck2\t0.75, 30000, 220, 0.75, 0.5'
        #return 'apluck', 'iplk = 0.75\nkamp = 30000\nicps = 220\nkpick = 0.75\nkrefl = 0.5\napluck wgpluck2 iplk, kamp, icps, kpick, krefl'

    def note(self, start, duration, frequency, amplitude = .5,
             vowel=None, spectral_tilt=None, vibrato_depth=None, vibrato_rate=None):
        return tabjoin('i', self.number, start, duration,
                       convert_amplitude(amplitude * 2.0), parse_pitch(frequency),
                       if_none(vowel, self.vowel),
                       if_none(spectral_tilt, self.spectral_tilt),
                       if_none(vibrato_depth, self.vibrato_depth),
                       if_none(vibrato_rate, self.vibrato_rate))


# CSD organization and output:

class CSD:
    def __init__(self, output_csd_filename='default.csd', render_sound=0):
        self.set_filenames(output_csd_filename)
        self.render_sound = render_sound
        self.options = '-W -o %s' % (self.output_sound_filename)
        self.instruments = []
        self.note_list = ''
        print 'Creating CSD file "%s"' % (self.output_csd_filename)
        if render_sound:
            print '; rendering to file "%s"' % (self.output_sound_filename)

    def set_filenames(self, output_csd_filename):
        self.output_csd_filename = output_csd_filename
        if output_csd_filename.endswith('.csd'):
            self.output_sound_filename = output_csd_filename[:-4] + '.wav'
        else:
            self.output_sound_filename = output_csd_filename + '.wav'

    def orchestra(self, *args):
        self.instruments += args

    def orchestra_definition(self):
        result = ''
        result += "sr = 44100\n"
        result += "kr = 4410\n"
        result += "ksmps = 10\n" 
        result += "nchnls = 1\n"

        for inst in self.instruments:
            result += inst.orchestra() + '\n'
        return string.rstrip(result)

    def tables(self):
        return tabjoin('f', 1, 0, 16384, 10, 1)

    def score(self, *args):
        self.note_list += string.join(args, '\n') + '\n'

    def score_definition(self):
        return string.rstrip(self.tables() + '\n' + self.note_list)

    def tagify(self, tag_name, s, newlines=1):
        return '\n<%s>\n%s\n</%s>\n' % (tag_name, s, tag_name)

    def output(self, output_csd_filename = None):
        if output_csd_filename:
            self.set_filenames(output_csd_filename)
        fp = open(self.output_csd_filename, 'w')
        fp.write(self.tagify('CsoundSynthesizer',
                             self.tagify('CsOptions', self.options) +
                             self.tagify('CsInstruments', self.orchestra_definition()) +
                             self.tagify('CsScore', self.score_definition()), 0))
        fp.close()
        if self.render_sound:
            os.system('/Users/ack/csound %s' % (self.output_csd_filename))

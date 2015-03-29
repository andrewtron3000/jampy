import random
import time
import sys
import Csound
import subprocess
import base64
import hashlib

csd = None
oscillator = None
buzzer = None
voice = None
song_publisher = None

def add_motif(instrument, req):
    global csd
    note_bank = req.note_bank.split()
    notes = random.sample(note_bank, len(note_bank))
    playit = [ random.choice([True, False]) for n in notes]
    chorus = zip(notes, playit)
    time = req.motif_start_time
    repeat = req.motif_repeat
    for (note, playit) in (chorus * repeat):
        if playit:
            csd.score(instrument.note(time, 
                                      req.note_duration, 
                                      note, 
                                      req.motif_amplitude))
        time += req.note_duration + req.internote_delay

def handle_create_song(req):
    global csd, oscillator, buzzer, voice
    global song_publisher
    s = 'temp'
    csd = Csound.CSD('%s.csd' % s) 
    csd.orchestra(oscillator, buzzer, voice) 
    for motif in req.motifs:
        if motif.instrument == 'oscil':
            add_motif(oscillator, motif)
        elif motif.instrument == 'buzzer':
            add_motif(buzzer, motif)
        elif motif.instrument == 'voice':
            add_motif(voice, motif)
    csd.output()
    args = ['csound', '-d', '%s.csd' % s] 
    subprocess.call(args)
    f = open('%s.csd' % s)
    csd_string = f.read()
    f.close()
    song_name = '%s.ogg' % req.song_name
    args = ['oggenc', '-o', song_name, '%s.aif' % s]
    subprocess.call(args)
    args = ['vorbiscomment', '-a', song_name,  
            '-t', "ARTIST=%s" % req.artist,
            '-t', "TITLE=%s" % req.song_name,
            '-t', "ALBUM=%s" % req.album,
            '-t', "GENRE=%s" % 'Electronica',
            '-t', "CSOUND=%s" % csd_string]
    subprocess.call(args)
    args = ['ogg123', song_name]
    subprocess.call(args)


class Motif(object):
    def __init__(self, motif_start_time, motif_repeat, motif_amplitude, note_bank, note_duration, internote_delay, instrument):
        self.motif_start_time = motif_start_time
        self.motif_repeat = motif_repeat
        self.motif_amplitude = motif_amplitude
        self.note_bank = note_bank
        self.note_duration = note_duration
        self.internote_delay = internote_delay
        self.instrument = instrument


class Request(object):
    def __init__(self, song_name, artist, album, motifs):
        self.song_name = song_name
        self.artist = artist
        self.album = album
        self.motifs = motifs    

def heads():
    return (random.random() < 0.5)

def biasedFlip(p):
    return (random.random() < p)

def selectInstrument():
    if heads():
        return 'oscil'
    else:
        return 'buzzer'

def selectInterval():
    return 0.15, 0.05

def triggerCreate(song_name, artist, album, motifs):
    handle_create_song(Request(song_name, artist, album, motifs))

def random_note():
	bases = ["A", "B", "C", "D", "E", "F", "G"]
	unsharpable = ["E", "B"]
	unflatable = ["C", "F"]
	octaves = map(str, range(2,6))
	mods = ["", "#"]

	base = random.choice(bases)
	mods = [""]
	if not base in unsharpable:
		mods.append("#")
	mod = random.choice(mods)
	octave = random.choice(octaves)
	return base + mod + octave

def random_motif(start_time):
	notes = " ".join([random_note() for i in range(10)])
	print("Random Notes: " + str(notes))
	return Motif(start_time, 12, 0.32, notes, 0.15, 0.05, random.choice(["oscil", "buzzer"]))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <artist> <album name>" % sys.argv[0]
        exit()
    else:
        artist = sys.argv[1]
        album = sys.argv[2]
    global song_publisher, oscillator, buzzer, voice
    oscillator = Csound.oscil() 
    buzzer = Csound.buzz() 
    voice = Csound.fmvoice() 
    for i in xrange(1, 16384):
        song_title = "song_%d" % i
        if heads():
            a = 0.05
            b = 0.15
        else:
            a = 0.15
            b = 0.05
        #motifs = [ Motif(0.0, 12, 0.32, "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6", 0.15, 0.05, selectInstrument()) ]
        motifs = [random_motif(i*2.0) for i in range(3)]
        # if biasedFlip(0.8):
        #     motifs.append(Motif(3.0, 10, 0.32, "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6",    a,    b, selectInstrument()))
        # if biasedFlip(0.9):
        #     motifs.append(Motif(6.0,  4, 0.10, "A2 B2 D3 D3 F#3 A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5",  0.3,  0.1, selectInstrument()))
        triggerCreate(song_title, artist, album, motifs)
        print "Created song %s" % song_title
        time.sleep(10)


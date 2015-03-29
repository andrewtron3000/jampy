import random
import time
import sys
import Csound
import subprocess
import base64
import hashlib
import matrixmusic

csd = None
oscillator = None
buzzer = None
voice = None
truevoice = None
song_publisher = None

def add_motif(instrument, req):
    global csd

    time = req.motif_start_time
    for note in req.score:
    	if note != "P":
	        csd.score(instrument.note(time, 
	                                  req.note_duration, 
	                                  note, 
	                                  req.motif_amplitude))
        time += req.internote_delay

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
    args = ['oggenc', '-o', song_name, '%s.wav' % s]
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
    def __init__(self, motif_start_time, motif_repeat, motif_amplitude, score, note_duration, internote_delay, instrument):
        self.motif_start_time = motif_start_time
        self.motif_repeat = motif_repeat
        self.motif_amplitude = motif_amplitude
        self.score = score
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
	#notes = " ".join([random_note() for i in range(10)])
	#notes = "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6 P".split(" ")
	notes = "C3 C#3 E3 F3 G3 G#3 B4 C4 C#4 E4 F4 G4 G#4".split(" ")
	score = matrixmusic.create_pair_score(notes, 15) * 5
	print("Random score: " + str(score))

	opts = [("voice", 1.0, 1.5), 
			#("oscil", 1.0, 1.5),
			("voice", 3.0, 1.5)] 
			#("oscil", 3.0, 1.5)]
	opt = random.choice(opts)

	return Motif(start_time, 12, 0.05, score, opt[1], opt[2], opt[0])


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
    #voice = Csound.voice()
    for i in xrange(1, 16384):
        song_title = "song_%d" % i

        #motifs = [ Motif(0.0, 12, 0.32, "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6", 0.15, 0.05, selectInstrument()) ]
        motifs = [random_motif(i*0.8) for i in range(3)]
        # if biasedFlip(0.8):
        #     motifs.append(Motif(3.0, 10, 0.32, "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6",    a,    b, selectInstrument()))
        # if biasedFlip(0.9):
        #     motifs.append(Motif(6.0,  4, 0.10, "A2 B2 D3 D3 F#3 A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5",  0.3,  0.1, selectInstrument()))
        triggerCreate(song_title, artist, album, motifs)
        print "Created song %s" % song_title
        time.sleep(10)


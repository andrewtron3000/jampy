import numpy as np
import random

def normalize_table(t):
	return t / np.sum(t, 0)

def make_random_transitions(nnotes):
	t = np.random.random((nnotes, nnotes))
	return normalize_table(t)

def weighted_arg_sample(probs):
	val = random.uniform(0.0, 1.0)
	for i in range(len(probs)):
		if val < probs[i]:
			return i
		else:
			val -= probs[i]
	# somehow got to the end?
	return len(probs) - 1

def random_table_walk(ttable, nnotes, startidx=-1):
	idx = startidx
	if idx < 0:
		idx = random.choice(list(range(ttable.shape[0])))
	ret = [idx]
	for i in range(nnotes - 1):
		curprobs = ttable[:, idx]
		idx = weighted_arg_sample(curprobs)
		ret.append(idx)
	return ret

def create_score(notes, length):
	ttable = make_random_transitions(len(notes))
	index_score = random_table_walk(ttable, length)
	newnotes = [notes[i] for i in index_score]
	return newnotes

if __name__ == '__main__':
	# test
	notes = "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6".split(" ")
	score = create_score(notes, 20)
	print("Score: %s" % " ".join(score))

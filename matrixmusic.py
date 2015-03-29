import numpy as np
import random
import math

def normalize_table(t):
	return t / np.sum(t, 0)

def make_random_transitions(nnotes):
	t = np.random.random((nnotes, nnotes))
	return normalize_table(t)

def make_local_transitions(nnotes, sigma = 3.0, baseweight = 0.01):
	base = np.random.random((nnotes, nnotes)) * baseweight
	for idx0 in range(nnotes):
		for idx1 in range(nnotes):
			dx = idx1 - idx0
			if dx != 0:
				w = math.exp(-(sigma * sigma * dx * dx))
			else:
				w = 0.0
			base[idx0, idx1] += w
	return normalize_table(base)

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
	ttable = make_local_transitions(len(notes))
	print(ttable)
	index_score = random_table_walk(ttable, length)
	newnotes = [notes[i] for i in index_score]
	return newnotes

if __name__ == '__main__':
	# test
	notes = "A3 B3 D4 E4 F#4 A4 B4 D5 E5 F#5 A5 B5 D6 E6 F#6".split(" ")
	score = create_score(notes, 20)
	print("Score: %s" % " ".join(score))

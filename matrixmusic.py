import numpy as np
import random
import math

def normalize_table(t):
	return t / np.sum(t, 0)

def make_random_transitions(nnotes):
	t = np.random.random((nnotes, nnotes))
	return normalize_table(t)

def make_random_pair_transitions(nnotes):
	t = np.random.random((nnotes, nnotes*nnotes))
	return normalize_table(t)

def make_sparse_pair_transitions(nnotes, noisefloor, ntrans):
	n2 = nnotes * nnotes
	t = np.random.random((nnotes, n2)) * noisefloor

	for i in range(n2):
		tgts = random.sample(list(range(nnotes)), ntrans)
		for tgt in tgts:
			t[tgt, i] = 1.0

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

def random_pair_table_walk(ttable, nnotes, startidx=(-1,-1)):
	idx = startidx
	if idx[0] < 0 or idx[1] < 0:
		idx0 = random.choice(list(range(ttable.shape[0])))
		idx1 = random.choice(list(range(ttable.shape[0])))
		idx = (idx0, idx1)
	ret = [idx[0]]
	for i in range(nnotes - 1):
		print(idx)
		flatidx = idx[0] + idx[1]*ttable.shape[0]
		curprobs = ttable[:, flatidx]
		newidx = weighted_arg_sample(curprobs)
		ret.append(idx[1])
		idx = (idx[1], newidx)
	return ret	

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

def create_pair_score(notes, length):
	ttable = make_sparse_pair_transitions(len(notes), 0.1, 2)
	#print(ttable)
	index_score = random_pair_table_walk(ttable, length)
	newnotes = [notes[i] for i in index_score]
	return newnotes

if __name__ == '__main__':
	# test
	notes = "A3 B3 D4 E4 F4 G4".split(" ")
	score = create_pair_score(notes, 20)
	print("Score: %s" % " ".join(score))

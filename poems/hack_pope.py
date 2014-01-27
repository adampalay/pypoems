import os
import re
import string
from poem import Poem
import nltk

print "cleaning poem"

volume_1_file = os.path.abspath("texts/pope_1.txt")
volume_2_file = os.path.abspath("texts/pope_2.txt")

v_1_start = "First in these fields I try the sylvan strains,"
v_1_end = "_F_. Alas! alas! pray end what you began,\nAnd write next winter more 'Essays on Man.'"

v_2_start = "Yes, you despise the man to books confined,"
v_2_end = "And universal darkness buries all."

with open(volume_2_file) as v2f:
	volume_2 = v2f.read()

with open(volume_1_file) as v1f:
	volume_1 = v1f.read()

def get_cropped_text(raw_text, start_text, end_text):
	start_index = raw_text.find(start_text)
	end_index = raw_text.find(end_text)
	return raw_text[start_index: end_index]

clean_volume_1 = get_cropped_text(volume_1, v_1_start, v_1_end)
clean_volume_2 = get_cropped_text(volume_2, v_2_start, v_2_end)

CROPPED_POEM = clean_volume_1 + "\n" + clean_volume_2


def get_clean_poem(cropped_poem):
	"""
	Clean poem of punctuation, line markers, and "PART"s
	"""
	lines = cropped_poem.split("\n")
	lines = [line for line in lines if len(line) < 100]
	for index, line in enumerate(lines):
		lines[index] = lines[index].strip()
		part_match = re.search(r"PART \w+", lines[index])
		line_marker = re.search(r"\d+$", lines[index])
		if part_match is not None:
			lines[index] = ""
		if line_marker is not None:
			# import pdb; pdb.set_trace()
			lines[index] = lines[index].strip(line_marker.group(0))
		lines[index] = lines[index].strip(string.punctuation + ' ')

	return "\n".join(lines)

def get_last_syllables(prons):
    if prons is None:
        return None
    last_syllables = set([])
    for pron in prons:
        # index of last vowel
        vowel_indices = [index for index, phen in enumerate(pron) if phen[-1].isdigit()]
        if vowel_indices:
            last_syllables.add(tuple(pron[vowel_indices[-1]:]))
    return last_syllables



PRON_DICT = nltk.corpus.cmudict.dict()
def rhymes(word, next_word):
	pron_1 = PRON_DICT.get(word.lower())
	pron_2 = PRON_DICT.get(next_word.lower())
	if pron_1 is not None and pron_2 is not None:
		if set(get_last_syllables(pron_1)) & set(get_last_syllables(pron_2)):
			return True
	return False


def get_rhymes_with(word, poem, deviation):
	rhyme_groups = []
	poem_length = len(poem)
	poem_split = poem.split("\n")
	for index, line in enumerate(poem_split):
		if line.split(" ")[-1].lower() == word.lower():
			# import ipdb; ipdb.set_trace()
			lower_bound = max(0, index - deviation)
			upper_bound = min(index + deviation + 1, poem_length)
			# import ipdb; ipdb.set_trace()
			context = poem_split[lower_bound: index] + poem_split[index + 1: upper_bound]
			for c_line in context:
				if rhymes(word, c_line.split(" ")[-1]):
					rhyme_groups.append((word, c_line.split(" ")[-1]))
	return rhyme_groups




CLEAN_POEM = get_clean_poem(CROPPED_POEM)
print "getting rhymes"

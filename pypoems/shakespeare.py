import re
import os
from pypoems.poetic_forms import ShakespeareSonnet
from pypoems.core import Collection

with open(os.path.abspath("texts/sonnets.txt")) as sonnet_file:
	RAW_TEXT = sonnet_file.read()

START = "\n\n\n\n\n  I\n\n"
END = "End of The Project Gutenberg Etext of Shakespeare's Sonnets"


def get_cropped_text(raw_text, start_text, end_text):
	start_index = raw_text.find(start_text)
	end_index = raw_text.find(end_text)
	return raw_text[start_index: end_index]


def generate_sonnets(clean_poems):
	sonnets = []
	for number, poem in enumerate(clean_poems):
		if len(poem.strip().split('\n')) == 14:
			sonnet = ShakespeareSonnet.create(
				poem.strip(),
				title="Sonnet {}".format(number + 1),
				author="William Shakespeare"
			)
			sonnets.append(sonnet)
	print "Sonnets generated"
	# for sonnet in sonnets:
	# 	sonnet.make_rhyming_groups()
	return sonnets


CROPPED_TEXT = get_cropped_text(RAW_TEXT, START, END)

RAW_POEMS = re.split(r'[IVXCML]+\n\n', CROPPED_TEXT)

CLEAN_POEMS = [poem for poem in RAW_POEMS if poem.strip()]
sonnets = Collection(generate_sonnets(CLEAN_POEMS))

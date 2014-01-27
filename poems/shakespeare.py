import re
from poem_tools_2 import Poem, Line, Word

with open("nlp/texts/sonnets.txt") as sonnet_file:
	RAW_TEXT = sonnet_file.read()

START = "\n\n\n\n\n  I\n\n"
END = "End of The Project Gutenberg Etext of Shakespeare's Sonnets"

CROPPED_TEXT = get_cropped_text(RAW_TEXT, START, END)

RAW_POEMS = re.split(r'[IVXCML]+\n\n', CROPPED_TEXT)

CLEAN_POEMS = [poem for poem in RAW_POEMS if poem.strip()]


def get_cropped_text(raw_text, start_text, end_text):
	start_index = raw_text.find(start_text)
	end_index = raw_text.find(end_text)
	return raw_text[start_index: end_index]


def generate_sonnets(clean_poems):
	sonnets = []
	for number, poem in enumerate(clean_poems):
		if len(poem.strip().split('\n')) == 14:
			sonnet = ShakespeareSonnet.make_poem(
				poem.strip(),
				title="Sonnet {}".format(number + 1),
				author="William Shakespeare"
			)
			sonnets.append(sonnet)
	print "Sonnets generated"
	for sonnet in sonnets:
		sonnet.make_rhyming_groups()
	return sonnets


class ShakespeareSonnet(Poem):

	def rhyme_setup(self):
		for i in range(3):
			base = i * 4
			self.lines[base].rhymes_to = self.lines[base + 2]
			self.lines[base + 1].rhymes_to = self.lines[base + 3]
		self.lines[12].rhymes_to = self.lines[13]

	def make_rhyming_groups(self):
		self.rhyming_groups = []
		for line in self.lines:
			if line.rhymes_to is not None:
				group = [line, line.rhymes_to]
				self.rhyming_groups.append(group)

class Collection(object):
	def __init__(self, poems):
		self.poems = poems

	def all_rhyme_pairs(self):
		rhyme_pairs = []
		for poem in self.poems:
			rhyme_pairs += poem.get_rhyme_pairs()
		return rhyme_pairs

class RhymePair(object):
	def __init__(self, words):
		# words is a tuple
		self.words = words

	def __eq__(self, pair):
		return len(self.words) == len(pair.words) and set(self.words) == set(pair.words)


sonnets = Collection(generate_sonnets(CLEAN_POEMS))

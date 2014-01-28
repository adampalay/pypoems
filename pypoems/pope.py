import os
import re
import string
from pypoems.poetic_forms import HeroicCouplets

# setup
file_name = os.path.abspath("texts/essay_on_criticism.txt")
raw_poem = open(file_name).read()

start = u"PART I."
end = u"Not free from faults, nor yet too vain to mend."

cropped_poem = raw_poem[raw_poem.find(start): raw_poem.find(end) + len(end)]

def get_clean_poem(cropped_poem):
	"""
	Clean poem of punctuation, line markers, and "PART"s
	"""
	lines = cropped_poem.split("\n")
	for index, line in enumerate(lines):
		lines[index] = lines[index].strip()
		part_match = re.search(r"PART \w+", lines[index])
		line_marker = re.search(r"\[\d+\]$", lines[index])
		if part_match is not None:
			lines[index] = ""
		if line_marker is not None:
			# import pdb; pdb.set_trace()
			lines[index] = lines[index].strip(line_marker.group(0))
		lines[index] = lines[index].strip(string.punctuation + ' ')

	return lines

clean_poem = "\n".join(get_clean_poem(cropped_poem))

essay_on_man = open(os.path.abspath("texts/essay_on_man.txt")).read()
EPISTLES = re.split(r"EPISTLE [IV]+\.", essay_on_man)
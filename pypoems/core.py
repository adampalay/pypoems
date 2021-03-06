import string
import nltk
import json
import itertools
import os

PRON_DICT = nltk.corpus.cmudict.dict()


class Poem(object):

    def __init__(self, text, author, title, rhyme_setup_needed):
        self.text = text
        self.author = author
        self.title = title
        self.rhyme_setup_needed = rhyme_setup_needed
        self.lines = [Line.create(number, line_text.strip()) for (number, line_text) in enumerate(text.strip().split('\n'))]
        self.rhyming_groups = None

    @property
    def lines_no_breaks(self):
        return [line for line in self.lines if line.text]

    @classmethod
    def create(cls, text, author=None, title=None, rhyme_setup_needed=True):
        # import ipdb; ipdb.set_trace()
        poem = cls(text, author, title, rhyme_setup_needed)

        # setup next_lines and prev_lines
        for line in poem.lines:
            line.next_line = poem.get_line(line.number + 1)
            line.prev_line = poem.get_line(line.number - 1)
        # setup rhymes, if necessary
        if rhyme_setup_needed:
            poem.rhyme_setup()

        return poem

    def lines_dict(self):
        return dict((line.number, line) for line in self.lines)

    def get_line(self, line_number):
        line = [line for line in self.lines if line.number == line_number]
        if len(line) == 1:
            return line[0]
        elif len(line) > 1:
            raise ValueError("More than one line with number {}".format(line_number))
        return None

    def rhyme_setup(self):
        pass

    def rhymes(self, line, next_line, context):
        pass

    def make_rhyming_groups(self):
        pass

    def get_context(self, line, lines_before, lines_after):
        context = {}
        for number in xrange(lines_before, lines_after):
            context[number] = self.get_line(line.number + number)
        return context

    def to_json(self):
        rt = dict((line.number, line.rhymes_to.number) for line in self.lines if line.rhymes_to is not None)
        json_dict = {
            "text": self.text,
            "author": self.author,
            "title": self.title,
            "rhymes_tos": rt
        }
        title_save = "untitled"
        if self.title is not None:
            title_save = self.title.replace(" ", "_").lower()
        author_save = "anonymous"
        if self.author is not None:
            author_save = self.author.replace(" ", "_").lower()
        with open(os.path.abspath("json/{}_{}.json".format(title_save, author_save)), 'wb') as jsonfile:
            json.dump(json_dict, jsonfile)

    @classmethod
    def from_json(cls, json_path):
        with open(json_path) as jsonfile:
            json_dict = json.load(jsonfile)
            text = json_dict["text"]
            author = json_dict["author"]
            title = json_dict["title"]
            rt = json_dict["rhymes_tos"]
            poem = cls.create(text, author, title, rhyme_setup_needed=False)
            for line in poem.lines:
                rhymes_to_number = rt.get(unicode(line.number))
                if rhymes_to_number is not None:
                    line.rhymes_to = poem.get_line(rhymes_to_number)
            poem.make_rhyming_groups()
            return poem

    def get_rhyme_pairs(self):
        rhyme_pairs = []
        for group in self.rhyming_groups:
            if len(group) == 2:
                rhyme_pairs.append(tuple(group))
            elif len(group) > 2:
                rhyme_pairs += itertools.combinations(group, 2)
        return [(t[0].words[-1].text.lower(), t[1].words[-1].text.lower()) for t in rhyme_pairs]


class Line(object):

    def __init__(self, number, text):
        self.number = number
        self.text = text
        self.rhymes_to = None
        self.is_break = False
        self.words = [Word.create(position, word_text) for position, word_text in enumerate(text.split(" "))]

    @classmethod
    def create(cls, number, text):
        line = cls(number, text)
        if len(line.text.strip()) == 0:
            line.is_break = True
        return line

    def rhymes_with(self, line):
        if self.is_break or line.is_break:
            return False
        return self.words[-1].rhymes_with(line.words[-1])

    def __repr__(self):
        return self.text


class Word(object):

    def __init__(self, position, text):
        self.position = position
        self.text = text.strip(string.punctuation + " ")
        self.last_consts = None
        self.prons = None

    @classmethod
    def create(cls, position, text):
        word = cls(position, text)
        word.prons = PRON_DICT.get(word.text.lower())
        if word.prons is not None:
            word.last_consts = set([pron[-1] for pron in word.prons if not pron[-1][-1].isdigit()])
        return word

    def get_last_syllables(self):
        if self.prons is None:
            return None
        last_syllables = set([])
        for pron in self.prons:
            # index of last vowel
            vowel_indices = [index for index, phen in enumerate(pron) if phen[-1].isdigit()]
            if vowel_indices:
                last_syllables.add(tuple(pron[vowel_indices[-1]:]))
        return last_syllables

    def rhymes_with(self, word):
        if self.prons is None or word.prons is None:
            return None
        return len(self.get_last_syllables() & word.get_last_syllables()) > 0

    def __repr__(self):
        return self.text


class PoemWithRhymeScheme(Poem):
    """
    Automatically generates a poem object from a rhyme_scheme,
    which looks something like 'abab'
    """
    def __init__(self, rhyme_scheme, *args, **kwargs):
        kwargs.update(rhyme_setup_needed=False)
        super(PoemWithRhymeScheme, self).__init__(*args, **kwargs)
        self.rhyme_scheme = rhyme_scheme

    def make_rhyming_groups(self):
        self.rhyming_groups = []
        for letter in set(self.rhyme_scheme):
            group = [scheme_line[1] for scheme_line in self.scheme_lines if scheme_line[0] == letter]
            for index, line in enumerate(group):
                if index < len(group) - 1:
                    line.rhymes_to = group[index + 1]
            self.rhyming_groups.append(group)

    @classmethod
    def create(cls, rhyme_scheme, *args, **kwargs):
        poem = cls(rhyme_scheme, *args, **kwargs)
        if len(poem.lines_no_breaks) % len(poem.rhyme_scheme) != 0:
            # sanity check
            raise ValueError("Rhyme scheme {} does not evenly fit into poem".format(poem.rhyme_scheme))
        poem.scheme_lines = zip(itertools.cycle(poem.rhyme_scheme), poem.lines_no_breaks)
        poem.make_rhyming_groups()
        return poem


class Collection(object):
    def __init__(self, poems):
        self.poems = poems

    def get_all_rhyme_pairs(self):
        rhyme_pairs = []
        for poem in self.poems:
            rhyme_pairs += poem.get_rhyme_pairs()
        return rhyme_pairs

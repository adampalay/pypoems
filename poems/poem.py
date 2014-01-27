import string
import nltk
import json
import itertools

PRON_DICT = nltk.corpus.cmudict.dict()


class Poem(object):

    def __init__(self, text, author, title, rhyme_setup_needed):
        self.text = text
        self.author = author
        self.title = title
        self.rhyme_setup_needed = rhyme_setup_needed
        self.lines = None
        self.lines_no_breaks = None
        self.rhyming_groups = None

    @classmethod
    def make_poem(cls, text, author=None, title=None, rhyme_setup_needed=True):
        # import ipdb; ipdb.set_trace()
        poem = cls(text, author, title, rhyme_setup_needed)
        poem.lines = [Line.make_line(number, line_text.strip()) for (number, line_text) in enumerate(text.strip().split('\n'))]
        poem.lines_no_breaks = [line for line in poem.lines if line.text]

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
        with open("../json/{}_{}.json".format(title_save, author_save)) as jsonfile:
            json.dump(json_dict, jsonfile)

    @classmethod
    def from_json(cls, json_path):
        with open(json_path) as jsonfile:
            json_dict = json.load(jsonfile)
            text = json_dict["text"]
            author = json_dict["author"]
            title = json_dict["title"]
            rt = json_dict["rhymes_tos"]
            poem = cls.make_poem(text, author, title, rhyme_setup_needed=False)
            for line in poem.lines:
                rhymes_to_number = rt.get(unicode(line.number))
                if rhymes_to_number is not None:
                    line.rhymes_to = poem.get_line(rhymes_to_number)
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
        self.words = [Word.make_word(position, word_text) for position, word_text in enumerate(text.split(" "))]


    @classmethod
    def make_line(cls, number, text):
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
    def make_word(cls, position, text):
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

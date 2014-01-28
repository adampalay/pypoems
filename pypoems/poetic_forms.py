from pypoems.core import Poem, PoemWithRhymeScheme


class ShakespeareSonnet(PoemWithRhymeScheme):
    def __init__(self, *args, **kwargs):
        super(ShakespeareSonnet, self).__init__(
            'ababcdcdefefgg', *args, **kwargs
        )


class HeroicCouplets(Poem):
    """
    A form mostly composed of couplets with the occassional
    Triplet thown in
    """
    def make_rhyming_groups(self):
        self.rhyming_groups = []
        group = []
        for line in self.lines_no_breaks:
            group.append(line)
            if line.rhymes_to is None:
                self.rhyming_groups.append(group)
                group = []
        print "Rhyming groups generated"

    def initial_rhyme_creation(self):
        for line in self.lines:
            context = self.get_context(line, -3, 4)

            if line.rhymes_to is not None:
                continue

            # assume first two lines rhyme:
            elif line.number == 0:
                line.rhymes_to = line.next_line

            # if line is last line: assume is rhymes with the line before
            elif line.next_line is None:
                self.get_line(line.number - 1).rhymes_to = line

            # if line comes after a break, assume it rhymes with the next line
            # and the lines before the break should rhyme too
            elif line.is_break:
                line.next_line.rhymes_to = line.next_line.next_line
                try:
                    line.prev_line.prev_line.rhymes_to = line.prev_line
                except AttributeError:
                    print line.number

            # finally, do the rhyming algorithm
            elif self.rhymes(line, line.next_line, context):
                line.rhymes_to = line.next_line
        print "Initial round of rhymes generated"

    def rhyme_setup(self):
        self.initial_rhyme_creation()
        self.make_rhyming_groups()
        # check for rhyming groups with only one member;
        # combine couplets
        solitary_rhymes = [group[0].number for group in self.rhyming_groups if len(group) == 1]
        for line_number in solitary_rhymes:
            line = self.get_line(line_number)
            if line.next_line.number in solitary_rhymes:
                line.rhymes_to = line.next_line
        print "lonely lines paired up"
        print 'regenerating rhyming_groups'
        self.make_rhyming_groups()

    def check_hard_rhymes(self, line, next_line):
        return line.rhymes_with(next_line) or line.rhymes_to == next_line

    def rhymes(self, line, next_line, context):
        ask_user = False
        if line.rhymes_with(next_line):
            return True

        if line.is_break or next_line.is_break:
            return False

        # if there's no way to pronounce the last word, ask user
        if line.words[-1].prons is None or next_line.words[-1].prons is None:
            ask_user = True

        # if words have the same final consonants:
        elif (line.words[-1].last_consts & next_line.words[-1].last_consts):

            # if it doesn't rhyme with the previous line,
            # we can assume it rhymes with the next one
            if not self.check_hard_rhymes(line.prev_line, line):
                return True

            # if it does rhyme with the previous line,
            # and if the next two lines rhyme, then
            # it doesn't rhyme with the next line
            if self.check_hard_rhymes(line.next_line, line.next_line.next_line):
                return False

            # otherwise, ask user
            ask_user = True

        if ask_user:
            decision = raw_input(
                "\nDo {word_1} and {word_2} rhyme?\n\n{context}\n".format(
                    word_1=line.words[-1].text,
                    word_2=next_line.words[-1].text,
                    context = "\n".join(
                        [str(line.number) + ": " + line.text for _, line in sorted(context.items())]
                    )
                )
            )
            return decision != "n"

        return False

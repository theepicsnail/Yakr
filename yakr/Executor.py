from StringIO import StringIO
import itertools
import os


def isplit(iterable, splitters):
    """
        Splits a list by a set of tokens
        isplit([1, 2, None, 3, 4], (None,)) => [[1,2],[3,4]]
    """
    #http://stackoverflow.com/questions/4322705/
    #   split-a-list-into-nested-lists-on-a-value
    return [list(g) for k, g in itertools.
            groupby(iterable, lambda x: x in splitters) if not k]


class Executor(object):
    def __init__(self, settings):
        self.paths = settings.get('paths', ['bin'])
        print "Executor settings:"
        print settings

    def tokenize(self, line):  # {{{
        """
            split line into a list of tokens
            replacing the pipe character with None

            e.g:
            "foo -bar | baz --qux=1"
            returns
            ["foo","-bar",None,"baz","--qux=1"]
        """
        escapeChar = '\\'
        quoteChars = '"\''
        delimiters = ' '
        pipe = '|'
        inEscape = False
        quoteStart = None

        curToken = ""
        for char in line:
            if inEscape:
                curToken += char
                inEscape = False
                continue

            if char == quoteStart:
                quoteStart = None
                continue

            if char == escapeChar:
                inEscape = True
                continue

            if quoteStart is None:
                if char in quoteChars:
                    quoteStart = char
                    continue

                if char in delimiters + pipe:
                    if curToken:
                        yield curToken
                    curToken = ""
                    if char in pipe:
                        yield None
                    continue

            curToken += char

        if curToken:
            yield curToken
    # }}}

    def search(self, prog):  # {{{
        for p in self.paths:
            for (cur, dirs, files) in os.walk(p):
                if prog in files:
                    return cur
                if prog + ".py" in files:
                    return cur
        return None
    # }}}

    def execute(self, command):  # {{{
        """
            Split apart a command and execute all the subcommands
            linking their stdout to the nexts stdin.

            "foo | bar | baz"
            will run foo, taking its stdout and putting it into bars stdin
            bars stdout will be put into bazs stdin
            bazs stdout will be returned as it's the last command

            Returns the last commands stdout.
        """
        parts = list(self.tokenize(command))
        # inputStream => prog1 => prog2 => prog3 => outputStream
        commands = isplit(parts, (None, ))
        error = ""

        for cmd in commands:
            prog, argv = cmd[0], cmd[1:]
            path = self.search(prog)
            if path is None:
                error = "Could not find '{}'".format(prog)
                break

        if error:
            return error

        return path
    # }}}

    def startProcess(self, argv, stdin):  # {{{
        # p = subprocess.Popen(argv,stdin=subprocess.PIPE,
        #                      stdout=subprocess.PIPE)
        # p.stdin.write(foo)
        # bar = p.stdout.read()
        # def connectProcess(p1, p2):
        #     outp = p1.stdout
        #     inp  = p2.stdin
        #     def streamReader(
        #     gevent.spawn(streamReader,p1,p2)
        # return process
        pass
    # }}}

if __name__ == "__main__":
    e = Executor({})
    running = True
    while running:
        line = raw_input(">")
        if not line:
            continue

        if line in ["quit", "exit"]:
            running = False
            continue

        result = e.execute(line)
        print result

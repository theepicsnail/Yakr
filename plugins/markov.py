from yakr.plugin_base import *
import redis
import re
import random
client = redis.StrictRedis(db=13)
def tokenize(line):
    for X in ["%", "!", "http", "<", ">", "[", " ", "Nicks", "Topic"]:
        if line.startswith(X):
            return []
    for X in ["has quit", "has joined", "C0 C1", "now known as", "has changed topic"]:
        if X in line:
            return []

    words = re.split("\s+", line.strip().lower())
    if len(words) < 4:
        return []

    for X in [
        "has quit",
        ]:
        if X in line:
            return []

    if "--" in words[2]:
        return []
    if "*" in words[2]:
        return []
    if "superbot" == words[2]:
        return []
    return words


def add_seed_data(line):
    chain = tokenize(line)
    WORDS_PER_LINK = 3
    if len(chain) < WORDS_PER_LINK+1:
        return

    line = " ".join(chain)
    idx = client.incr("last_idx")
    client.set(idx, line)

    for i in xrange(len(chain)-WORDS_PER_LINK+1):
        src = " ".join(chain[i:i+WORDS_PER_LINK])
        client.sadd(src, idx)
    

def reseed():
    client.flushdb()
    client.set("first_idx", 0)
    client.set("last_idx", 0)

    for N,line in enumerate(file("markov_seed_data.txt")):
        add_seed_data(line)
        if (N+1) % 1000000 == 0:
            print "Bundled 100,000"
    print "Done seeding data"

#Utility functions
def search_for_phrase(search):
    keys = client.keys(search)
    if len(keys) == 0:
        return None
    return random.choice(keys)

def phrase_to_lineno(phrase):
    return int(client.srandmember(phrase))

cached = {}
def lineno_to_line(lineno):
    if lineno in cached:
        return cached[lineno]
    
    cached_keys = cached.keys()
    if len(cached_keys) >= 100:
        del cached[random.choice(cached_keys)]

    line =client.get(lineno)
    cached[lineno] = line

    return line

def get_adjacent_words_in_line(phrase, line):
    print "adjacent:"
    print line
    print phrase
    print line.split(phrase)

    occurances = line.count(phrase)
    phrase_location = line.find(phrase)
    for _ in xrange(random.randint(0, occurances-1)):
        phrase_location = line.find(phrase, phrase_location + 1)

    before = line[:phrase_location]
    after = line[phrase_location + len(line):]
    if before:
        before = before.split(" ")[-2]
    else:
        before = None
    if after:
        after = after.split(" ")[1]
    else:
        after = None
    return before, after

def generate_sentence():
    low_key = int(client.get("first_idx"))
    high_key = int(client.get("last_idx"))
    chosen_key = random.randint(low_key, high_key)
    line = lineno_to_line(chosen_key)
    parts = line.split(" ")

    sentence = parts[:3] #sentence = [first, three, words]
    linenos = [chosen_key] * 3
    while True:
        parts = sentence[-3:]

        phrase = " ".join(parts)
        new_lineno = phrase_to_lineno(phrase)
        line = lineno_to_line(new_lineno)
        _, next_word = get_adjacent_words_in_line(phrase,line)

        if next_word:
            sentence.append(next_word)
            linenos.append(int(new_lineno))
        else:
            break

    return " ".join(sentence)

def generate_sentence_from(search):
    phrase = search_for_phrase(search)
    if phrase is None:
        return "I didn't find anything with '%s' in it. :(" % search
    lineno  = phrase_to_lineno(phrase)
    sentence = phrase.split(" ")
    linenos = [lineno] * 3

    #work backwards to a start
    while True:
        parts = sentence[:3]
        phrase = " ".join(parts)

        new_lineno = phrase_to_lineno(phrase)
        line = lineno_to_line(new_lineno)
        prev_word, _ = get_adjacent_words_in_line(phrase, line)

        if prev_word:
            sentence.insert(0, prev_word)
            linenos.insert(0, new_lineno)
        else:
            break

    #work forwards to an end
    while True:
        parts = sentence[-3:]
        phrase = " ".join(parts)

        new_lineno = phrase_to_lineno(phrase)
        line = lineno_to_line(new_lineno)
        _, next_word = get_adjacent_words_in_line(phrase, line)

        if next_word:
            sentence.append(next_word)
            linenos.append(new_lineno)
        else:
            break

    return " ".join(sentence)


@command("speak")
def speak(who, what, where):
    w = what.strip()
    if w:
        parts = w.split(" ")
        if len(parts) > 3:
            say(where, "!speak word [word [word]] - generate a phrase with the provided word(s)")
            return
        if len(parts) < 3: 
            w += " *"
        if len(parts) < 2:
            w = "* " + w

        say(where, generate_sentence_from(w.lower()))
    else:
        say(where, generate_sentence())

@privmsg
def add_privmsg(who, what, where):
    add_seed_data(what)


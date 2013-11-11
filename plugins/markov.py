from yakr.plugin_base import *
import redis
import random
import re
import time
client = redis.StrictRedis(host='localhost', port=6279, db=12)

def hincrby(src, dst, n):
    p.hincrby(src, dst, n)
    #assert(False)
    #t = mock_redis.get(src, {})
    #v = t.get(dst, "0")
    #v = str(int(v) + n)
    #t[dst] = v
    #t[dst] = v
    #mock_redis[src]=t

def hgetall(key):
    resp = client.hgetall(key)
    #return mock_redis.get(key, {})
    return resp
START_CACHE = hgetall("START")

def add_link(src, dst):
    hincrby(src, dst, 1)

def tokenize(line):
    words = re.split("\s+", line.strip().lower())
    if len(words) < 4:
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
    start = " ".join(chain[:WORDS_PER_LINK])
    add_link("START", start)
    end = " ".join(chain[-WORDS_PER_LINK:])
    add_link(end, "END")
    for i in xrange(len(chain)-WORDS_PER_LINK):
        src = " ".join(chain[i:i+WORDS_PER_LINK])
        add_link(src, chain[i+WORDS_PER_LINK])


def random_next(src):
    global START_CACHE
    start_time = time.time()
    if src == "START":
        m = START_CACHE
    else:
        m = hgetall(src)
    total = sum(map(int, m.values()))
    if total == 0:
        print "Random_next end", time.time()-start_time
        return "END"

    n = random.randint(0, total-1)
    for k,v in m.items():
        v = int(v)
        if n < v:
            print "Random_next end", time.time()-start_time
            return k
        n -= v
    return "ERROR"

def generate():
    #START -> A B
    #A B -> C
    #B C -> END
    word_pair = random_next("START")   #A B
    word_list = word_pair.split(" ")
    print "Start:",word_pair
    sentence = ""
    while word_list[-1] != "END":                       # B != END   C != END
        print word_list
        sentence += word_list[0] +" "
        word_list.append(random_next(" ".join(word_list)))
        word_list.pop(0)
    return sentence + " ".join(word_list[:-1])


#@privmsg
#def record(who, what, where):
#    add_seed_data(what)

@command("speak")
def speak(who, what, where):
    print "Speak triggered at", time.time()
    m = generate()
    print "Generation ended at", time.time()
    say(where, m)

@privmsg
def add_privmsg(who, what, where):
    add_seed_data(what)

def seed_data():
    #Do your data seeding here.
    for N,line in enumerate(file("markov_seed_data.txt")):
        add_seed_data(line)
        if (N+1) % 100000 == 0:
            print "Bundled 100,000"
            p.execute()
            print "Sent."
    print "Done seeding data"

if not START_CACHE:
    print "DB appears to be cleared. Reseeding..."
    p = client.pipeline()
    seed_data()
    p.execute()
    START_CACHE = hgetall("START")

p = client



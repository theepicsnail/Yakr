from yakr.plugin_base import *

@command("morse")
def toMorse(who, what, where):
    # do string stuff here
    # test
    # print(text2morseGeneral(what))
    say(where, text2morseGeneral(what))

def text2morseGeneral(text, useProsigns=False):
    morse = ""
    c = None
    text = tidyText(text)
    tokens = []
    #prosign = None
    i = 0
    token_length = None
    while len(text) > 0:
        token_length = 1
        #prosign = text.match(/^<...?>/)  # array of matches
        #if prosign and useProsigns:
        #    token_length = prosign[0].length
        
        tokens.append(text[0: token_length])
        text = text[token_length: len(text)]
    
    for i in range(0, len(tokens)):
        c = text2morseH[tokens[i]]
        if c == None:
            c = '?'
            if useProsigns:
                for j in range(0, len(prosign2morse)/2 ):
                    if prosign2morse[2*j] == tokens[i]:
                        c = prosign2morse[2*j + 1]
                        break

        morse += c + ' ';
    
    return morse.strip()

def tidyText(text):
    from re import sub
    text = text.upper()
    text = text.strip()
    text = sub(r"\s+", ' ', text)
    return text

text2morseH = {
    'A': ".-",
    'B': "-...",
    'C': "-.-.",
    'D': "-..",
    'E': ".",
    'F': "..-.",
    'G': "--.",
    'H': "....",
    'I': "..",
    'J': ".---",
    'K': "-.-",
    'L': ".-..",
    'M': "--",
    'N': "-.",
    'O': "---",
    'P': ".--.",
    'Q': "--.-",
    'R': ".-.",
    'S': "...",
    'T': "-",
    'U': "..-",
    'V': "...-",
    'W': ".--",
    'X': "-..-",
    'Y': "-.--",
    'Z': "--..",
    '1': ".----",
    '2': "..---",
    '3': "...--",
    '4': "....-",
    '5': ".....",
    '6': "-....",
    '7': "--...",
    '8': "---..",
    '9': "----.",
    '0': "-----",
    '.': ".-.-.-",
    ',': "--..--",
    ':': "---...",
    '?': "..--..",
    '\'': ".----.",
    '-': "-....-",
    '/': "-..-.",
    '(': "-.--.-",
    ')': "-.--.-",
    '"': ".-..-.",
    '@': ".--.-.",
    '=': "-...-",
    ' ': "/"
}

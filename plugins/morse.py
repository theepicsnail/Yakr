# The code was converted from JavaScript
# http://morsecode.scphillips.com/i/morse.js
# and is released availabe Gnu General Public License

#from yakr.plugin_base import *

#@command("morse")
def morse(who, what, where):
    # test
    print(convertPro(what))
    print(convertPro(convertPro(what)))
    #say(where, convert(what))

def convert(input):
    if isMorse(input):
        return morse2text(input)
    else:
        return text2morse(input)

def convertPro(input):
    if isMorse(input):
        return morse2textPro(input)
    else:
        return text2morsePro(input)

def isMorse(input):
    input = tidyMorse(input)
    from re import match
    if match(r"^[ /.-]*$", input):
        return True
    else:
        return False

def tidyText(text):
    from re import sub
    text = text.upper()
    text = text.strip()
    text = sub(r"\s+", ' ', text)
    return text

def text2morse(text):
    return text2morseGeneral(text, False)

def text2morsePro(text):
    return text2morseGeneral(text, True)

def text2morseGeneral(text, useProsigns=False):
    morse = ""
    c = None
    text = tidyText(text)
    tokens = []
    prosign = None
    i = 0
    token_length = None
    while len(text) > 0:
        token_length = 1
        from re import findall
        prosign = findall(r"^<...?>", text)  # array of matches
        if prosign and useProsigns:
            token_length = len(prosign[0])
        
        tokens.append(text[0: token_length])
        text = text[token_length: len(text)]
    
    for i in range(0, len(tokens)):
        if tokens[i] in text2morseH:
            c = text2morseH[tokens[i]]
        else:
            c = None
        if c == None:
            c = '?'
            if useProsigns:
                for j in range(0, int(len(prosign2morse)/2) ):
                    if prosign2morse[2*j] == tokens[i]:
                        c = prosign2morse[2*j + 1]
                        break

        morse += c + ' ';
    
    return morse.strip()

def tidyMorse(morse):
    morse = morse.strip();
    morse = morse.replace(r"\|", "/");  # unify the word seperator
    morse = morse.replace(r"\/", " / ");  # make sure word seperators are spaced out
    morse = morse.replace(r"\s+", " ");  # squash multiple spaces into single spaces
    morse = morse.replace(r"(\/ )+\/", "/");  # squash multiple word seperators
    morse = morse.replace(r"^ \/ ", "");  # remove initial word seperators
    morse = morse.replace(r" \/ $", "");  # remove trailing word seperators
    morse = morse.replace(r"_", "-");  # unify the dash character
    return morse

def morse2text(morse):
    return morse2textGeneral(morse, False)

def morse2textPro(morse):
    return morse2textGeneral(morse, True)

def morse2textGeneral(morse, useProsigns=False):
    text = ""
    c = None
    morse = tidyMorse(morse)
    tokens = morse.split(" ")
    for i in range(0, len(tokens)):
        if tokens[i] in morse2textH:
            c = morse2textH[tokens[i]]
        else:
            c = None
        if c == None:
            c = '?'
            if useProsigns:
                for j in range(0, int(len(prosign2morse)/2) ):
                    if prosign2morse[2*j + 1] == tokens[i]:
                        c = prosign2morse[2*j]
        text += c
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

morse2textH = {}
for text in text2morseH:
    morse2textH[text2morseH[text]] = text

prosign2morse = [
    '<AA>', '.-.-',
    '<AR>', '.-.-.',
    '<AS>', '.-...',
    '<BK>', '-...-.-',
    '<BT>', '-...-',  # also <TV>
    '<CL>', '-.-..-..',
    '<CT>', '-.-.-',
    '<DO>', '-..---',
    '<KN>', '-.--.',
    '<SK>', '...-.-',  # also <VA>
    '<VA>', '...-.-',
    '<SN>', '...-.',  # also <VE>
    '<VE>', '...-.',
    '<SOS>', '...---...'
]

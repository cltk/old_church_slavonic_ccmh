import re
import itertools
import kirillitsa as kr
from sys import argv


script, ascii_file, unicode_file = argv


def swap_mark(word):
    # not quite working for all bracket arrangements
    """ for all occurences of diacritics except if they're the last letter in the word:
    swap the diacritic with its successor to have correctly combining Unicode characters
    swap_mark("*(((wS$d&Sem&") returns "*w(S($(d&Sem&". Also swaps the upper case marking with slashes in words like
    "*/juZe"."""
    res = list(word)
    if re.search("/+", word):
        l = re.search("/+", word).span()[0]
        r = re.search("/+", word).span()[1]
        if word[0:2] == "*/":
            res[0], res[l:r] = res[l:r], res[0]
        elif word[:2] == "!*" or word[:2] == "*(" or word[:2] == "(*":
            if word[2] == "/":
                res[:1], res[l:r] = res[l:r], res[:1]
            else:
                res[:2], res[l:r] = res[l:r], res[:2]
        res = list(itertools.chain(*res))
    if re.search("\({2,}", word):
        brack_nr = len(re.search("\({2,}", word).group(0))
        if brack_nr > len(word[re.search("\({2,}", word).span()[1]:]):
            word = word[:re.search("\({2,}", word).span()[0]] + word[re.search("\({2,}", word).span()[1] - 1:]
            return swap_mark(word)
        if len(word) == 2 * brack_nr:
            # bracks = word[:brack_nr]
            letters = word[brack_nr:]
            res[0] = "("
            res[len(word) - 1] = word[len(word) - 1]
            for i in range(1, len(word) - 1):
                if i % 2 == 0:
                    res[i] = "("
                else:
                    res[i] = letters[i - 1]
        else:
            for i, letter in enumerate(word):
                # for words with multiple accents like *(((wS$d&Sem& we need to swap all the accents first
                if re.search("\({2,}", word[i:]):
                    print(res)
                    brack = len(re.search("\({2,}", word[i:]).group(0))
                    for j in range(brack):
                        # in case there's a ja, je, ju when swapping the bracket block
                        if word[i + j] == j:
                            res[i + j], res[i + j + brack], res[i + j + brack + 1] = res[i + j + brack], res[i + j + brack + 1], res[i + j]
                        else:
                            res[i + j], res[i + j + brack] = res[i + j + brack], res[i + j]
                            i += 1
            if i < len(word) - 1 and (
                                letter in kr.DIACRITICS and letter != "(" or (
                                    letter in ["*", "!"] and word[i + 1] == "j")):
                # for ja, je, ju etc we need (ja -> ja(, not (ja -> j(a
                if i < len(word) - 2 and word[i + 1] == "j":
                    res[i], res[i + 1], res[i + 2] = res[i + 1], res[i + 2], res[i]
                else:
                    res[i], res[i + 1] = res[i + 1], res[i]
        return "".join(res)
    else:
        skip_flag = False
        double_skip_flag = False
        for i, letter in enumerate(res):
            if double_skip_flag:
                double_skip_flag = False
                skip_flag = True
                continue
            if skip_flag:
                skip_flag = False
                continue
            if i < len(word) - 1 and (letter in kr.DIACRITICS or (letter in ["*", "!"] and res[i + 1] == "j")):
                # for ja, je, ju etc we need (ja -> ja(, not (ja -> j(a
                if i < len(word) - 2 and (res[i + 1] == "j" or res[i + 1] == "*"):
                    res[i], res[i + 1], res[i + 2] = res[i + 1], res[i + 2], res[i]
                    double_skip_flag = True
                else:
                    res[i], res[i + 1] = res[i + 1], res[i]
                    skip_flag = True
        return "".join(res)


def j_distinguisher(word):
    if word[1] == "u":
        return "ю"
    elif word[1] == "a":
        return "ꙗ"
    elif word[1] == "e":
        return "є"
    elif word[1] == "E":
        return "ꙝ"
    elif word[1] == "O":
        return "ѭ"


def titlo(tokens):
    if tokens[0] == "j":
        if tokens[1] == "u":
            return " ⷻ"
        elif tokens[1] == "a":
            return " ⷼ"
        elif tokens[1] == "O":
            return " ⷿ"
    elif tokens[0] == "'":
        return "꙽" + titlo(tokens[1:])
    elif tokens[0] == "^":
        return "҄" + titlo(tokens[1:])
    else:
        return kr.TITLOS[tokens[0]]


def unicode_encoder(word):
    if word == "":
        return ""
    for i, letter in enumerate(word):
        if i < len(word) - 1 and letter == "*":
            if word[i + 1] == "!":
                return "҃" + kr.KIRILLITSA[word[i + 2]].upper() + unicode_encoder(word[i + 3:])
            else:
                if word[i + 1] == "j":
                    return j_distinguisher(word[i + 1:]).upper() + unicode_encoder(word[i + 3:])
                else:
                    return kr.KIRILLITSA[word[i + 1]].upper() + unicode_encoder(word[i + 2:])
        elif i == 0 and letter == "!":
            return unicode_encoder(word[i + 1:]) + "҃"
        elif i < len(word) - 3 and letter == "!":
            return titlo(word[i + 1:]) + unicode_encoder(word[i + 2:])
        elif i < len(word) - 1 and word[i:i + 2] == "--":
            return "~" + unicode_encoder(word[i + 2:])
        elif letter == "j" and i < len(word) - 2:
            return j_distinguisher(word[i:]) + unicode_encoder(word[i + 2:])
        elif letter == "j":
            return j_distinguisher(word[i:])
        elif letter in kr.DIACRITICS:
            return unicode_encoder(word[i + 1:]) + kr.DIACRITICS[letter]
        elif letter not in kr.KIRILLITSA:
            return letter + unicode_encoder(word[i + 1:])
        else:
            return kr.KIRILLITSA[letter] + unicode_encoder(word[i + 1:])


#TODO: assemanianus, marianus, zogr, zogr-b
out = open(unicode_file, "w")
with open(ascii_file) as inp:
    for line in inp:
        list_in = line.split()
        for token in list_in:
            # print(token)
            # print(unicode_encoder(token))
            if token[0] not in list(kr.DIACRITICS.keys()) + list(kr.KIRILLITSA.keys()) + ["!", "*"] and token[len(token) - 1] not in list(kr.DIACRITICS.keys()) + list(kr.KIRILLITSA.keys()) + ["!", "*"]:
                token = token[0] + swap_mark(token[1:len(token) - 1]) + token[len(token) - 1]
            else:
                token = swap_mark(token)
            out.write(unicode_encoder(token))
            out.write(" ")
        out.write("\n")
inp.close()
out.close()

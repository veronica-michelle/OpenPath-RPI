

def idget(line, word):
    i = 0;
    for letter in line:
        if i == len(word):
                return "good";
        if letter == word[i] and i < len(word):
            i = i + 1
        else:
            i = 0;
    return "bad"


fp = open("dummydata.json")




for line in fp:
    ids = idget(line, "5.0")
    print(ids);



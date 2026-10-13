

def checker(line, word):
    i = 0;
    for letter in line:
        if i == len(word):
                return "good";
        if letter == word[i] and i < len(word):
            i = i + 1
        else:
            i = 0;
    return "bad"

def contents(line, word):
    i = 0;
    final = ""
    checker = 0
    for letter in line:

        if checker == 1:
            if letter == ',' or letter == '"':
                return final
            final = final + letter
        else:
            if i == len(word):
                checker = 1
            else:
                if letter == word[i]:
                    i = i + 1
    return ""



fp = open("dummydata.json")




finder = ("id","name","lat","long","type")
finderadds = ('": ','": ','":','":','": ') # remove the last most symbol in the seperateion:
# so if the line is "thing": "contents",
# it would be 'thing' and '":'
# dont ask why this is the case, i'm not sure myself, it just kind aworks like that
i = 0

for line in fp:
    status = checker(line, finder[i])
    if status == "good":
        result = contents(line, finder[i] + finderadds[i] )
        print(finder[i] + ": " + result)
        i = i + 1
        if i == len(finder):
            i = 0



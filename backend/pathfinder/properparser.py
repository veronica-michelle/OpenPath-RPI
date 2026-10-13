infilename = input("put the json file here:")

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


fd = open(infilename)
nodeinfo = dict()
finder = ("id","name","lat","long","type")
finderadds = ('": ','": ','":','":','": ') # remove the last most symbol in the seperateion:
# so if the line is "thing": "contents",
# it would be 'thing' and '":'
# dont ask why this is the case, i'm not sure myself, it just kind aworks like that '
i = 0

for line in fd:
    status = checker(line, finder[i])
    if status == "good":
        result = contents(line, finder[i] + finderadds[i] )
        nodeinfo[finder[i]] = result
        print(nodeinfo[finder[i]])
        i = i + 1
        if i == len(finder):

            # this is where you would pu the node information

            i = 0



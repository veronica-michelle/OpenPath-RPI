import networkx as nx

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
            if i+1 == len(word):
                checker = 1
            else:
                if letter == word[i]:
                    i = i + 1
                else:
                    i = 0;
    return "null"


# put stuff below here
G = nx.Graph()



fp = open("dummyloc.json")

finder = ("id","name","lat","long","type")
finderadds = ('":"', '":"', '":',  '":', '":"')
# if the line is "thing": "contents",
# it would be 'thing' and '": "'
i = 0

for line in fp:
    helper = ["null","null","null","null","null"]
    while i < len(finder):
        result = "null"
        status = checker(line, finder[i])
        if status == "good":

            result = contents(line, finder[i] + finderadds[i] )
            print(result)
            helper[i] = result

        if result == "null":
            break
        print(finder[i] + ": " + result)
        i = i + 1
    if(i == len(finder)):
        G.add_node(helper[0])
    i = 0


fp2 = open("dummypath.json")

finder = ("id","from","to","dist","type")
finderadds = ('":"', '":"', '":"',  '":', '":"')
# if the line is "thing": "contents",
# it would be 'thing' and '": "'
i = 0

for line in fp2:
    helper = ["null","null","null","null","null"]
    while i < len(finder):
        result = "null"
        status = checker(line, finder[i])
        if status == "good":
            result = contents(line, finder[i] + finderadds[i] )
            helper[i] = result
        if result == "null":
            break
        print(finder[i] + ": " + result)
        i = i + 1
    if(i == len(finder)):
        G.add_edge(helper[1],helper[2])
    i = 0

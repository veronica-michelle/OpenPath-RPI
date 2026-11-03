import networkx as nx

class Node:
    def __init__(self, ID: str, name: str, latitude: float, longitude: float, Type: str):
        self.ID = ID
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.Type = Type

class Connection:
    def __init__(self, ID: str, From: str, To: str, dist: float, Type: str):
        self.ID = ID
        self.From = From
        self.To = To
        self.dist = dist
        self.Type = Type




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

def corddif(lat1,long1,lat2,log2):
    final = 0
    flat = 0
    flong = 0
    if(lat1 > lat2):
        flat = lat1 - lat2
    else:
        flat = lat2 - lat1
    if(long1 > long2):
        flong = long1 - long2
    else:
        flong = long2 - long1

    final = sqrt(flat^2 + flong^2)

    return final


# put stuff below here
G = nx.Graph()

allnodes = {}

allconnections = {}

finalnodes = {}
finalconnections = ()



fp = open("dummyloc.json")

finder = ("id","name","lat","long","type")
finderadds = ('":"', '":"', '":',  '":', '":"')
# if the line is "thing": "contents",
# it would be 'thing' and '": "'
i = 0

for line in fp:

    # makes a list of all of the necesary information
    helper = ["null","null","0","0","null"]
    while i < len(finder):
        result = "null"
        status = checker(line, finder[i])
        if status == "good":

            result = contents(line, finder[i] + finderadds[i] )
            print(result)
            # gets a stores information in lit
            helper[i] = result

        if result == "null":
            break
        print(finder[i] + ": " + result)
        i = i + 1
    if(i == len(finder)):
        # uses information in list to make node
        final = Node(helper[0],helper[1],float(helper[2]),float(helper[3]),helper[4])
        allnodes[helper[1]] = final # stores it by name to allow for easy finding for inputing somthing
        G.add_node(helper[0])
    i = 0


fp2 = open("dummypath.json")

finder = ("id","from","to","dist","type")
finderadds = ('":"', '":"', '":"',  '":', '":"')
# if the line is "thing": "contents",
# it would be 'thing' and '": "'
i = 0

for line in fp2:
    helper = ["null","null","null","0","null"]
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
        final = Connection(helper[0],helper[1],helper[2],float(helper[3]),helper[4])
        allconnections[helper[0]] = final
        G.add_edge(helper[1],helper[2])
        list(G.adj[helper[1]])
    i = 0




# make an A* algorythm



# basically get a node; find all the nodes that are connected to it; then calculated the diffrence between each of those nodes, and the destination node.
# remove any nodes that are invalid, so if stairs are invalid, then dont include those types of nodes.




#start = input("starting point here: ")
#end = input("ending point here: ")
#restrictions = input("restrictions: ")

#done = False



#print(list(G.nodes))

#print(list(G.edges))
print(list(G.edges)[0]) # this works exactley how you think it does


























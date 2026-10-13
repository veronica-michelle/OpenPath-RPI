import networkx as nx











graph = nx.Graph()

nodes = map(str,int); # string is for location name; and int is for location number associated; int is ID

infilename = string(input("put the json file here:")) # replace with actual json file that has all the nodes

infile = open(infilename, "r")

helper = 0

for line in fp:
    print(line)

infile2name = string(input("put the json file here:"))

infile2 = open(infile2name, "r")

while line = infile2.readline()::

    graph.add_edges_from([(1, 2), (1, 3)])


# store all locations as a number
# maybe have a color atribute be the form of connection

# set up a loop that looks for the adjacent nodes for the current position and the final position; loop for each node thats adjaceent
# repeat until the list of adjacent nodes has at least one connection


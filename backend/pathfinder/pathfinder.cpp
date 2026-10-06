#include <vector>
#include <iostream>
#include <fstream>
#include <list>
#include <string>
#include <unordered_map>
#include "location.h"
#include <stack>


// fill this in later, this is where the proper code will go

// all locations will also be stored in a map for easy access
// the ID as the key, and the Location class as the value

// when adding a connection, it will just look through the map to find the 2 locations, and then just run addconnection() on one of them; wich will connect the two


// to find a path, it will keep a vector of already visited location, specifically there ID, so that it dosent go to the same place twice; and as such dosent go around in circles.

int main(int amount, char** inputs){

// write a loop of some form that goes through each of the locations, and the locations connected to it; and keeps track of the ids it has already been to; so that it dosent go in loops
// and once it finds a route that connects to the destination; it returns the path neaded

// could do a duel path system, where it runs all connections from the destination and the current position, and returns the first path that connects both.
// however this would result in possibly exponetial growth
// but i could use a child and parent process system

    std::string dataname = input[1];
    std::map<std::string,Location> locations;

    std::ifstream data(dataname);
    std::tring line;



    while(getline(data, line)){

    };






};

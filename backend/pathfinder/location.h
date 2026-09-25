#include <vector>
#include <iostream>
#include <fstream>
#include <list>
#include <string>

//****************** IMPORTANT
/*
 *
 *
if your getting data, i just need the location name, its ID, and its latitude and longitode;
if your getting a connection, i only need the names/IDs of the two locations that are connected and the type of the connection


*/
/*
 *
 e very part of campus can be stored as a location that then connects to other lo*cations
 with the connection in the code being represented by a pointer in an array of pointers that points to that location
 and the type of connection between two locations being stored as a string in a vector; the vector connection, and the array pointer being the same position in there vector and array respectfully

 if a location is under construstion, then all connections to it will also be labeled under construction
     if a connection itself is under construction, then that connection will be set to under construction

         */




class Location{
public:
    // identifiers  V
    // these are used to find where you are, and will be used as inputs to help people find where they are, and then find where they need to be
    std::string name; // the name of the location
    double latitude;
    double longitude;
    std::string id; // the unique id of this location


    // path id will not be needed, since it seems redundent
    std::vector<std::string> connectiontype; // says what the limitation of going to that location is
    std::vector<Location*>  connected; // connects to other locations

    Location(){
        name = "NULL";
        latitude = 0;
        longitude = 0;
        id = "NULL";
    };

    Location(std::string str, int la, int lo, std::string i){
        name = str;
        latitude = la;
        longitude = lo;
        id = i;
    };

    ~Location(){
        // i need to design a proper deleter

    };


    bool addconnection(Location &place, std::string limit){ // this adds a pointer to the vector of connected locations that points to another location
        // and does the same with the other location with this location.
        // make a loop to check if the connection already exists

        connectiontype.push_back(limit);
        connected.push_back(&place);

        place.connectiontype.push_back(limit);
        place.connected.push_back(this);

        return true;
    };

};




#include <vector>
#include <iostream>
#include <fstream>
#include <list>
#include <string>
#include <unordered_map>
#include "location.h"
#include <stack>



int main(){

    Location test1;

    Location test2("name2",0,0,"1");

    Location test3("name3",0,0,"1");

    test2.addconnection(test3,"none");

    std::cout << test1.name << "\n";
    std::cout << test2.name << "\n";
    std::cout << test3.name << "\n";
    std::cout << "tests below v\n";

    std::cout << test2.connected[0]->name << "\n";
    std::cout << test3.connected[0]->name << "\n";


};




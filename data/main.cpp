#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>

struct Point {
    Point() : x(0.0), y(0.0), z(0.0) {}
    Point(double x, double y, double z) : x(x), y(y), z(z) {}

    friend std::ostream& operator<<(std::ostream& ostr, const Point& p) {
        ostr << "(" << std::setprecision(7) << p.x << ", " << p.y << ", " << std::setprecision(2) << p.z << ")";
        return ostr;
    }

    double x;
    double y;
    double z;
};

double get_distance_2d(const Point& from, const Point& to) {
    const int x_scale_factor = 111093;
    const int y_scale_factor = 81541;
    
    double dx = (to.x - from.x) * x_scale_factor;
    double dy = (to.y - from.y) * y_scale_factor;

    return std::sqrt((dx * dx) + (dy * dy));
}

double get_distance(const Point& from, const Point& to) {
    double run = get_distance_2d(from, to);
    double rise = to.z - from.z;
    return std::sqrt((run * run) + (rise * rise));
}


double get_gradient(const Point& from, const Point& to) {
    double run = get_distance_2d(from, to);
    double rise = std::abs(to.z - from.z);
    return (rise / run);
}

int main() {
    std::cout << std::fixed;
    std::string input;

    while (true) {
        std::cout << "1. Create edge\n";
        std::cout << "2. Exit\n";
        std::cout << "\n> ";
        std::cin >> input;

        if (input == "2") {
            break;
        }

        if (input == "1") {
            std::cout << "\n";
            Point from;
            Point to;

            for (int i = 0; i < 2; ++i) {
                double x;
                double y;
                double z;

                std::cout << "Enter " << ((i == 0) ? "from" : "to") << " node: ";
                std::cin >> x >> y >> z;
                
                if (i == 0) {
                    from = Point(x, y, z);
                } else {
                    to = Point(x, y, z);
                }
                std::cout << "Point: " << ((i == 0) ? from : to) << "\n\n";
            }

            double distance = get_distance(from, to);
            double gradient = get_gradient(from, to) * 100;

            std::cout << "From Node: " << from;
            std::cout << "\nTo Node: " << to;
            std::cout << "\n";
            std::cout << "\nDistance: " << std::setprecision(3) << distance;
            std::cout << "\nGradient: " << std::setprecision(3) << gradient;
        }

        std::cout << "\n\n";
    }

    return 0;
}

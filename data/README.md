# JSON Data Structure

The purpose of this README is to explain the thought process and reasoning for the structure of the JSON file format detailing the necessary information on nodes (either location or pathpoints) and edges (the distance between nodes). Regarding edges, a distance formula has been proposed when calculating the distance. It also says what formula is to be used for the gradients.

Originally the layout for both files (`locations.json` and `paths.json`) were based off the given workflow (`workflow.jpg`). That structure was then revised and is continuously being revised due to remarks by team members regarding future use of this project and scaling.

## Node Data Layout (`locations.json`)

The intended organization of this file is for all nodes that specify a location (building) will be listed first, with nodes for pathpoints (sidewalks, intersections, start/end of stairs, ramps, etc.) following after.

Buildings will have an id that is to be used by the pathfinder, a name for displaying to users, an array of entrances, each with its own id and information, in order to find, not only the shortest path, but also the most accessible. The features list four variables: accessible, which refers to inside the building; the presence or absence of stairs and/or a ramp; and buttons, which contains a boolean array. The first element representing the outside push button and the second for the inside one.

Path nodes only have id, coordinations, and elevation fields (in meters). The entrances for the location nodes will also have coordinates and an elevation node (in meters). For the coordinates, they will be organized latitude first then longitude (latitude, longitude) The purpose for this is to calculate an approximate gradient between two points, that will be stored by a corresponding edge.

> [!NOTE]
> For the JSON files, any units that are not coordinates or gradients will be using the metric system.

```json
{
    "L##": {
        "id": "L##",
        "name": "building",
        "entrances": [{
            "id": "L##A",
            "coordinates": [0.0, 0.0],
            "elevation": 0.0,
            "features": {
                "accessible": false,
                "stairs": false,
                "ramp": false,
                "buttons": [false, false]
            }
        }, {
            "id": "L##B",
            "coordinates": [0.0, 0.0],
            "elevation": 0.0,
            "features": {
                "accessible": false,
                "stairs": false,
                "ramp": false,
                "buttons": [false, false]
            }
        }]
    },
    "N###": {
        "id": "N###",
        "coordinates": [0.0, 0.0],
        "elevation": 0.0
    }
}
```

Following a similar convention with the [RPI Atlas](https://github.com/rgtdthrd/RPI-Atlas) project, nodes specifically describing a building will be prefixed with a capital L followed by a two digit number, beginning at 01 up to 99. For nodes that designate a pathpoint, they will be prefixed with a capital N, with a three digit number after, starting potentially from 001 up to 999.

> [!NOTE]
> While not explicitly shown, entrance ids would be the location id followed by a letter (A, B, C, etc.).

The intent of this naming is to have the pathfinder to identify nodes by the length of the id. It will make more sense later when going over the edges, but essentially, a "location" node id will be three characters long, a "path" node id will be four characters long, and an edge id will be five characters long. This gives the potential for, hypothetically, 99 buildings, 999 paths, and 999 edges. The previous project has noted 71 locations, 377 nodes, and 584 connections.

> [!IMPORTANT]
> For this specific document, the path nodes should start after the last number for the location nodes; therefore, no two nodes should share the same number.

### Current Location IDs

With the current [ARN.txt](/docs/ARN.txt), here are the contents of the file with the appropriate id for each building. While the numbering is based off the ordering of the file, in reality, the numbering of buildings should not mattered as long as each has its own unique id.

```
ARN: area right now
we're doing the radius 0.1 miles around carnegie (photo in proposal)
buildings inside:
- Carnegie [L01]
- Walker Lab [L02]
- Sage Lab [L03]
- Pittsburg [L04]
- EMPAC [L05]
- West Hall [L06]
- Amos Eaton [L07]
- Lally [L08]
- Library [L09]
- VCC [L10]
```

## Edge Data Layout (`paths.json`)

The edges follow a similar layout to the workflow (`workflow.jpg`) with some changes. Following some previous comments by other team members, there is a features object, similar to the one in the location nodes, detailing attributes such as: ground quality, presence of stairs or ramps at any point, whether it is currently blocked off for any reason (construction happens a lot in a specific area), and the gradient or steepness overall. 

> [!IMPORTANT]
> The gradient will be calculated beforehand using the elevation of the `from` and `to` nodes before the pathfinder starts.

```json
{
    "E0###": {
        "from": "from",
        "to": "to",
        "distance": 0.0,
        "features": {
            "paved": false,
            "stairs": false,
            "ramp": false,
            "closed": false,
            "gradient": 0.0
        }
    }
}
```

In terms of naming, each edge will be prefixed with E0, followed by a three digit number, starting from 001 to 999. Since edges are entirely separate, or should be at least, from the nodes, there is no worry over the same number being used. Regarding location nodes, the main id will be listed in the edge, and it is up to the pathfinder to go through that location's array of entrances and find the most suitable one.

For time sake, I will personally fill out the locations.json for the buildings listed in the [ARN.txt](/docs/ARN.txt) file. Then I will record all path nodes that are reasonable and near each building and do the following calculations for the corresponding edges.

There is no viable way to automate the second part, unless there is something niche for that, and these properties should remain relatively static.

> [!NOTE]
> Like mentioned previously, distance will also be in metric units (meters). And regarding the gradient for both nodes and edges, they will be in degrees.

## Distance Formula

The previous project, [RPI Atlas](https://github.com/rgtdthrd/RPI-Atlas), used the Haversine distance. However, as the campus spans a variety of numbers (265, 275, and 295 acres) on various sites, if we capped it at 300 acres, it would be roughly 1.21405 km^2. Which, if we assumed a perfect square, would mean the length of the campus is around ~1.10184 km.

The point is, RPI is way to small to justify using the Haversine formula which is used for finding distance with the assumption that Earth is a perfect sphere. RPI is not big enough for curves to even impact distance calculations. Therefore, I suggest the Euclidean distance formula, specifically for 3D spaces to account for elevation.

For the coordinates to work, they need to be converted to meters from degrees. A scale factor for both latitude and longitude are required, based on a center. Considering potential scalability of this project, I have set the center to be the bridge connecting the main campus and freshman hill (42.7293334, -73.6776311)

Using length of one degree of latitude and longitude as shown on Table 7 in the [National Geospatial-Intelligence Agency American Practical Navigator (Vol. II, 2019)](https://www.dco.uscg.mil/Portals/9/NMC/pdfs/examinations/bowditch_Vol_2_2019.pdf) (pg. 130), the longitude scale factor is 111,093 m and the latitude scale factor is 81,541 m. This is going based off the 43th row on the table, which I got from rounding the latitude (42.7293334) to 43. Now, when calculating distances, the difference between the coordinates is multiplied by the scale factor, giving the actual distance in meters instead of degrees.

Following the Cartesian plane, where longitude is $x$ and latitude is $y$, the math to get to the standard Euclidean formula for 2D is:

$$
\Delta{x} = \left(x_1 - x_0 \right) \times 111,093
$$$$
\Delta{y} = \left(y_1 - y_0 \right) \times 81,541
$$$$
\text{Run} = \sqrt{\Delta{x^2} + \Delta{y^2}}
$$

Afterwards, find the difference in elevation between the two points where $z$ represents elevation: $Rise=z_1-z_0$

With both run and rise calculated (elevation will already be in meters, so no scale factor is required), both the distance and the gradient can be calculated with the 3D Euclidean and slope percentage formulas:

$$
\text{d} = \sqrt{Run^2 + Rise^2}= \sqrt{\Delta{x^2} + \Delta{y^2} + \Delta{z^2}}
$$$$
\text{Gradient (\\%)} = \left(\frac{\text{Rise}}{\text{Run}} \right) \times 100
$$

> [!IMPORTANT]
> While the JSON follows a latitude then longitude format, it's more common to have it as longitude first then latitude. Additionally, the distance formula described above follows that longitude, latitude format, associating longitude with x and latitude with y. Realistically, this should not cause too much of an issue as the only thing that differs is the scale factor. However, keep in mind of any potential reorderings to stick to the standard, either by me (Azrael Baram) or future maintainers.

## Thoughts and Future Planning

Obviously, these formats should be approved however, I will still collect data as the information taken from [RPI Atlas](https://github.com/rgtdthrd/RPI-Atlas) is not entirely accurate (specifically building entrances are not marked themselves).

My hope is that, after gathering the main data and calculating the necessary information for the rest of the team to work with, is to potentially create a program that would infact automate most of this process. It would be a program that takes in a TSV file, parse the data into a locations.json file, and then, given two nodes that the user specifies, it will create the corresponding edge and store it in paths.json.

Other advanced features would involve modifying existing nodes to reflect real life changes, adding or removing nodes which should then automatically update edges (only for node removal), and general listing and searching of nodes and edges. Separate files would be created to store the data for this program (not in JSON) files, so that the program can easily read and modify the attributes of existing data.

The target is for future use, in the case of either scope expansion or administrative adoption, whoever is in charge of the data itself would have a relatively straightforward way of changing it when needed.

### Additional Location Names

RPI is known for having a bunch of abbreviations or acronyms, to the point that there is a dedicated website just for explaining those abbreviations. In addition, some buildings are not known by what RPI lists as their official name. What would help in people trying navigate campus would be if several aliases guaranteed the same location.

While most of the locations' names could easily be checked to see if the user's search matches it works well, some are a bit more difficult. For example, both EMPAC and the VCC are currently listed by their abbreviations in `locations.json`. Despite those being what the buildings are referred to the most, someone entering "Voorhees Computing Center" would not get the intended building.

Of course, this could be done in many ways, and it is not an urgent issue, but might be useful to think about in the future, or if a user wished to know exactly what the abbreviation stood for.

## Links

Link to similar past project: [RPI Atlas](https://github.com/rgtdthrd/RPI-Atlas)

Link to the xlsx of the RPI Atlas data: [ATLAS_Graph_Data.xlsx](ATLAS_Graph_Data.xlsx)

Link to the National Geospatial-Intelligence Agency (NGA), "American Practical Navigator" (Bowditch), Pub. No. 9, Vol. II, 2019 Edition: https://www.dco.uscg.mil/Portals/9/NMC/pdfs/examinations/bowditch_Vol_2_2019.pdf

## Contributor Information

Contributor: Azrael Baram ([azzybar](https://github.com/azzybar/OpenPath-RPI))

Upstream Repo: [OpenPath-RPI](https://github.com/veronica-michelle/OpenPath-RPI)

Updated: 02 November 2026

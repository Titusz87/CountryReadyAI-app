from geopy.distance import geodesic

person = (-37.8069, 144.9611)
incident = (-37.8160, 144.9700)

distance_km = geodesic(person, incident).km

if distance_km <= 10:
    print("Incident is within 10 km")

#TODO write all current incidents into quadtree and test a search

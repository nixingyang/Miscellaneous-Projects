from itertools import combinations, permutations
import numpy as np
import pandas as pd
import re

EARTH_RADIUS = 6371


def get_coordinates(location):
    """Given (latitude, longitude, altitude), get the coordinates of the location.
    
    Reference: https://upload.wikimedia.org/wikipedia/commons/7/7b/ECEF.svg
    """
    latitude, longitude, altitude = location
    radius = altitude + EARTH_RADIUS
    x = radius * np.cos(np.radians(latitude)) * np.cos(np.radians(longitude))
    y = radius * np.cos(np.radians(latitude)) * np.sin(np.radians(longitude))
    z = radius * np.sin(np.radians(latitude))
    return np.array([x, y, z])


def is_valid_connection(coordinates_1, coordinates_2):
    """Given two coordinates, identify whether the tie line travel through Earth."""
    coordinates_anchor = np.zeros(3)
    distance_1 = np.linalg.norm(coordinates_1 - coordinates_anchor)
    distance_2 = np.linalg.norm(coordinates_2 - coordinates_anchor)
    distance_1_2 = np.linalg.norm(coordinates_1 - coordinates_2)
    s = (distance_1 + distance_2 + distance_1_2) / 2
    area = (s * (s - distance_1) * (s - distance_2) * (s - distance_1_2))**0.5
    height = 2 * area / distance_1_2

    # Any triangle
    if height >= EARTH_RADIUS:
        return True
    # Obtuse triangle
    if distance_1**2 - height**2 >= distance_1_2**2 or distance_2**2 - height**2 >= distance_1_2**2:
        return True
    return False


def run():
    # Read file content
    file_content = pd.read_csv("./input/track.csv", names=range(5)).as_matrix()

    # Read seed value
    print("Seed is {:s}".format(re.findall(r"\d+\.\d+", file_content[0, 0])[0]))

    # Read the coordinates of all satellites
    satellite_coordinates_dict = {}
    for row_index in range(1, file_content.shape[0] - 1):
        satellite_coordinates_dict[
            file_content[row_index, 0]] = get_coordinates(
                file_content[row_index, 1:-1])

    # Read the coordinates of the starting and ending points
    starting_point_coordinates = get_coordinates(
        file_content[-1, 1:3].tolist() + [0])
    ending_point_coordinates = get_coordinates(file_content[-1, 3:].tolist() +
                                               [0])

    # Find those satellites which are available for the starting and ending points
    valid_satellites_for_starting_point = []
    valid_satellites_for_ending_point = []
    for satellite_name, satellite_coordinates in satellite_coordinates_dict.items(
    ):
        if is_valid_connection(starting_point_coordinates,
                               satellite_coordinates):
            valid_satellites_for_starting_point.append(satellite_name)
        if is_valid_connection(ending_point_coordinates, satellite_coordinates):
            valid_satellites_for_ending_point.append(satellite_name)

    # Find valid satellite connections
    valid_next_satellites = {}
    for satellite_name in satellite_coordinates_dict.keys():
        valid_next_satellites[satellite_name] = []
    for satellite_combination in combinations(satellite_coordinates_dict.keys(),
                                              2):
        if is_valid_connection(
                satellite_coordinates_dict[satellite_combination[0]],
                satellite_coordinates_dict[satellite_combination[1]]):
            valid_next_satellites[satellite_combination[0]].append(
                satellite_combination[1])
            valid_next_satellites[satellite_combination[1]].append(
                satellite_combination[0])

    # Search in a depth-first fashion
    for search_depth in range(1, len(satellite_coordinates_dict.keys()) + 1):
        print("Working on search_depth {:d} ...".format(search_depth))

        # Generate all possible routes
        possible_routes = np.array(
            list(permutations(satellite_coordinates_dict.keys(), search_depth)))

        # Omit those routes which violate valid_satellites_for_starting_point
        valid_mask = np.zeros(possible_routes.shape[0], dtype=np.bool)
        for valid_satellite in valid_satellites_for_starting_point:
            valid_mask[possible_routes[:, 0] == valid_satellite] = True
        if np.sum(valid_mask) == 0:
            continue
        possible_routes = possible_routes[valid_mask]

        # Omit those routes which violate valid_satellites_for_ending_point
        valid_mask = np.zeros(possible_routes.shape[0], dtype=np.bool)
        for valid_satellite in valid_satellites_for_ending_point:
            valid_mask[possible_routes[:, -1] == valid_satellite] = True
        if np.sum(valid_mask) == 0:
            continue
        possible_routes = possible_routes[valid_mask]

        # Omit those routes which violate valid_next_satellites
        for index in range(0, search_depth - 1):
            valid_mask = np.zeros(possible_routes.shape[0], dtype=np.bool)
            for route_index, possible_route in enumerate(possible_routes):
                if possible_route[index + 1] in valid_next_satellites[
                        possible_route[index]]:
                    valid_mask[route_index] = True
            if np.sum(valid_mask) == 0:
                possible_routes = None
                break
            possible_routes = possible_routes[valid_mask]

        # Can not find valid routes
        if possible_routes is None:
            continue

        # Valid routes have been found
        for possible_route in possible_routes:
            for satellite_name in possible_route[:-1]:
                print(satellite_name, end=", ")
            print(possible_route[-1])
        break


if __name__ == "__main__":
    run()

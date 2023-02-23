import numpy
import cartHelpers
from CibicObjects import cibic_objects
import random

def Build_texture_position_all_rides(
    source_data:list, 
    aux_data: list,
    ride_size:int, 
    scriptOp:scriptTOP) -> callable:

    # create an empty ride array
    np_ride_array = numpy.zeros((len(source_data), ride_size, 4), dtype=numpy.float32)

    # loop through all rides
    for ride_index, each_ride in enumerate(source_data):
        current_ride:cibic_objects.Ride = each_ride
        single_ride = []

        if aux_data == None:
            blue_chan = 0
        else:
            blue_chan = aux_data[ride_index]

        # extract geometry and coords
        geometry = current_ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')
        if coords != None:
            # loop through all cords and append them to the single ride list
            for each_coord in coords:

                # print(each_coord)
                pos = [each_coord[1], each_coord[0], blue_chan, 1.0]
                single_ride.append(pos)

            # fill in extra elements with 0s
            while len(single_ride) < ride_size:
                single_ride.append([0.0, 0.0, 0.0, 0.0])
            
            # replace 0's in np array with ride data
            np_ride_array[ride_index] = single_ride

        else:
            pass

    return np_ride_array


def Build_texture_color_all_rides(
    source_data:list, 
    ride_size:int, 
    color_journal_lookup:OP, 
    scriptOp:scriptTOP) -> callable:

    # create an emptey ride array
    np_ride_array = numpy.zeros((len(source_data), ride_size, 4), dtype=numpy.float32)

    # loop through all rides
    for ride_index, each_ride in enumerate(source_data):
        current_ride:cibic_objects.Ride = each_ride
        ride_color = []
        
        reflection_data = current_ride.Reflection_data.answers if current_ride.Reflection_data != None else ''

        if reflection_data == '':
            journal_color_index = 6
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]
        else:
            journal_color_index = reflection_data[3]
            if journal_color_index == '' or journal_color_index == None:
                journal_color_index = 6
        
            else:
                journal_color_index = journal_color_index

            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]


        # extract geometry and coords
        geometry = current_ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')

        if coords == None:
            pass
        
        else:
            # loop through all cords and append them to the single ride list
            for each_coord in coords:
                if each_coord != None:
                    ride_color.append([journal_color[0], journal_color[1], journal_color[2], 1.0])
                else:
                    pass
            
            # fill in extra elements with 0s
            while len(ride_color) < ride_size:
                ride_color.append([0.0, 0.0, 0.0, 0.0])
            
            # replace 0's in np array with ride data
            np_ride_array[ride_index] = ride_color

    return np_ride_array


def Build_texture_satisfaction_data_by_rider(
    source_data:list, 
    ride_size:int, 
    color_journal_lookup:OP, 
    scriptOp:scriptTOP) -> callable:
    
    # create an emptey ride array
    np_ride_array = numpy.zeros((len(source_data), ride_size, 4), dtype=numpy.float32)

    # # loop through all rides
    for each_index, each_user in enumerate(source_data):
        output_color_list = []

        for each_ride in each_user.get('rides'):
            current_ride:cibic_objects.Ride = each_ride
            journal = current_ride.journaled_data
            output_col = 0
            user_color_list = []

            if journal == '' or journal == None:
                output_col = 2

            else:
                output_col = journal.answers[0]

            user_color_list = [
                output_col, 
                0, 
                0,
                1]

            output_color_list.append(user_color_list)

        # fill in extra elements with 0s
        while len(output_color_list) < ride_size:
            output_color_list.append([0.0, 0.0, 0.0, 0.0])
        
        # replace 0's in np array with ride data
        np_ride_array[each_index] = output_color_list

    return np_ride_array

def Build_texture_flows(
    source_data:dict, 
    scriptOp:scriptTOP) -> callable:

    all_flow_paths = []

    for each_flow, flow_vals in source_data.items():
        current_flow:cibic_objects.Flow = flow_vals        
        flow_paths = current_flow.all_paths

        for each_path in flow_paths:
            geometry = each_path.get('flowPath').get('geometry')
            if geometry != None:
                all_flow_paths.append(geometry.get('coordinates'))


    path_sizes = [len(each) for each in all_flow_paths]
    max_path_size = max(path_sizes)

    # create an emptey ride array
    np_ride_array = numpy.zeros((len(all_flow_paths), max_path_size, 4), dtype=numpy.float32)

    for coord_index, coords in enumerate(all_flow_paths):
        single_flow = []
        # loop through all cords and append them to the single ride list
        for each_coord in coords:
            single_flow.append([each_coord[1], each_coord[0], 0, 1.0])
        
        # fill in extra elements with 0s
        while len(single_flow) < max_path_size:
            single_flow.append([0.0, 0.0, 0.0, 0.0])
        
        # replace 0's in np array with ride data
        np_ride_array[coord_index] = single_flow

    return np_ride_array

def Build_texture_flows2(
    source_data:dict, 
    scriptOp:scriptTOP) -> callable:

    current_flows = set()
    all_flow_paths = []
    flow_use = []

    for each_ride in source_data:
        current_ride:cibic_objects.Ride = each_ride
        if current_ride != None:
            if current_ride.Flow != None:
                current_flows.add(current_ride.Flow)

    for each_flow in current_flows:
        this_flow:cibic_objects.Flow = each_flow
        geometry = this_flow.flow_path.get('geometry')
        if geometry != None:
            all_flow_paths.append(geometry.get('coordinates'))
            flow_use.append(len(this_flow.Rides))

    path_sizes = [len(each) for each in all_flow_paths]
    max_path_size = max(path_sizes)

    # create an empty ride array
    np_ride_array = numpy.zeros((len(all_flow_paths), max_path_size, 4), dtype=numpy.float32)

    for coord_index, coords in enumerate(all_flow_paths):
        single_flow = []
        flow_util = flow_use[coord_index]
        # loop through all cords and append them to the single ride list
        for each_coord in coords:
            single_flow.append([each_coord[1], each_coord[0], flow_util, 1.0])
        
        # fill in extra elements with 0s
        while len(single_flow) < max_path_size:
            single_flow.append([0.0, 0.0, 0.0, 0.0])
        
        # replace 0's in np array with ride data
        np_ride_array[coord_index] = single_flow

    return np_ride_array

def Point_per_ride_along_path(
    source_data:list, 
    scriptOp:scriptTOP) -> callable:

    role_map = {
        'rider' : 0,
        'steward' : 1, 
        'mentor' : 2
    }
    point_list = []

    for each_ride in source_data:
        current_ride:cibic_objects.Ride = each_ride
        role = current_ride.role
        satisfaction = 1
        if current_ride.journaled_data != None:
            satisfaction = current_ride.journaled_data.answers[0] + 1

        if current_ride != None:
            geometry = current_ride.Geo_JSON_Path_Only_Obj
            if geometry != None:
                coords = geometry.get('geometry').get('coordinates')
                if coords != None:
                    rand_index = random.randint(0, len(coords) - 1)
                    rand_coord = coords[rand_index]
                    point_data = [rand_coord[1], rand_coord[0], role_map.get(role), satisfaction]
                    point_list.append(point_data)

    # create an empty ride array
    np_ride_array = numpy.zeros((1, len(point_list), 4), dtype=numpy.float32)
    np_ride_array[0] = point_list

    return np_ride_array
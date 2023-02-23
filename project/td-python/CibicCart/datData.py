from datetime import datetime, timezone, timedelta
import cartHelpers
from CibicObjects import cibic_objects

# NOTE - DAT helpers
def Render_flow_map_to_table() -> list:
    ''' Returns flow_map to table DAT for render
    '''
    data = []
    header = ['id', 'has_paths', 'num_paths', 'has_join_points', 'join_point_list']
    data.append(header)
    flow_map = parent().Flow_Map

    for flow_id, flow_data in flow_map.items():
        if flow_id == None:
            pass
        else:
            paths = flow_data.Paths
            has_paths = None
            for each_path in paths:
                geometry = each_path.get('flowPath').get('geometry')
                if geometry != None:
                    has_paths = True
                    break
                else:
                    has_paths = False
            num_paths = len([path for path in flow_data.Paths if path.get('flowPath').get('geometry') != None])
            join_point_list = [path.get('flowPath').get('flowJoinPoints') for path in flow_data.Paths]
            has_join_points = any(elem is not None for elem in join_point_list)
            new_row = [flow_id, has_paths, num_paths, has_join_points, join_point_list]
            data.append(new_row)

    return data

def Render_rides_by_ride_data_to_table() -> list:
    source_data = parent().Rides
    data = []

    header = ['ride_id', 'user_id']
    data.append(header)
    
    for each in source_data:
        row_data = []
        row_data.extend([each.ride_id, each.user_id])
        data.append(row_data)

    return data

def Render_rides_by_user_data_to_table() -> list:
    data = []
    user_key = ipar.Settings.Targetuserid.eval()
    source_data = parent().Get_Rides_From_User_IDs([user_key])

    color_lookup = op('null_color_lookup')
    color_journal_lookup = op('null_color_journal_lookup')

    header = []
    coords_header = ['ride_id', 'flow_id', 'r', 'g', 'b', 'journal_r', 'journal_g', 'journal_b', 'index','raw_lat', 'raw_lon', 'satisfaction', 'words', 'face', 'color']
    journal_header = ['ride_id', 'flow_id', 'results']
    header.extend(coords_header)
    data.append(header)

    radius = 0.000

    for ride in source_data:
        row_data = []

        index = source_data.index(ride)
        features = ride.Geo_JSON_Obj.get('features')
        rgb = [color_lookup['r'][index], color_lookup['g'][index], color_lookup['b'][index]]
        reflection_data = ride.Reflection_data.answers if ride.Reflection_data != None else ''

        if reflection_data == '':
            journal_color_index = 6
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]
        else:
            journal_color_index = reflection_data[3]
            if journal_color_index == '':
                        journal_color_index = 6
        
            else: journal_color_index = journal_color_index
            
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]

        ids = [ride.ride_id, ride.Flow_id]

        geometry = ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')

        # # if geometry.get('type') == 'LineString':
        for each_coord in coords:
            lat_long = [each_coord[1], each_coord[0]]
            row_data = ids + rgb + journal_color + [index] + lat_long + list(reflection_data)
            data.append(row_data)


    return data


def Render_gps_coords_data_to_table() -> list:
    data = []

    rides = parent().Rides
    color_lookup = op('null_color_lookup')
    color_journal_lookup = op('null_color_journal_lookup')

    coords_header = ['x', 'y', 'z', 'r', 'g', 'b', 'journal_r', 'journal_g', 'journal_b', 'index', 'ride_id', 'flow_id', 'raw_lat', 'raw_lon']
    data.append(coords_header)

    # set start and end time as a datetime object with a utc timezone
    start = op.CARTOGRAPHY.Start_date
    end = op.CARTOGRAPHY.End_date

    # use the `Get_Rides_From_Time_Range` method
    rides = parent().Get_Rides_From_Time_Range(start, end)
    radius = 0.000
    sphere_radius = 10.0001


    for ride in rides[1:]:
        index = rides.index(ride)
        features = ride.Geo_JSON_Obj.get('features')
        rgb = [color_lookup['r'][index], color_lookup['g'][index], color_lookup['b'][index]]
        reflection_data = ride.Reflection_data.answers if ride.Reflection_data != None else ''

        if reflection_data == '':
            journal_color_index = 6
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]
        else:
            journal_color_index = reflection_data[3]
            if journal_color_index == '':
                        journal_color_index = 6
            
            else: journal_color_index = journal_color_index
            
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]

        journal_row = [ride.ride_id, ride.Flow_id]
        journal_row.extend(reflection_data)

        geometry = ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')

        for each_coord in coords:
            xyz = helpersMOD.convert_to_xy(each_coord[1], each_coord[0])
            xyz.extend([radius])
            xyz.extend(rgb)
            xyz.extend(journal_color)
            xyz.extend([index])
            xyz.extend([ride.ride_id, ride.Flow_id])
            xyz.extend([each_coord[1], each_coord[0]])
            xyz.extend(reflection_data)
            data.append(xyz)

        radius += 0.001
        sphere_radius += 0.001

    return data

def Render_sphere_coords_data_to_table() -> list:
    """
    """
    data = []

    rides = parent().Rides
    color_lookup = op('null_color_lookup')
    color_journal_lookup = op('null_color_journal_lookup')

    coords_header = ['x', 'y', 'z', 'r', 'g', 'b', 'journal_r', 'journal_g', 'journal_b', 'index', 'ride_id', 'flow_id', 'raw_lat', 'raw_lon']
    data.append(coords_header)

    # use the `Get_Rides_From_Time_Range` method

    radius = 0.000
    sphere_radius = 10.0001

    for ride in rides[1:]:
        index = rides.index(ride)
        features = ride.Geo_JSON_Obj.get('features')
        rgb = [color_lookup['r'][index], color_lookup['g'][index], color_lookup['b'][index]]
        reflection_data = ride.Reflection_data.answers if ride.Reflection_data != None else ''

        if reflection_data == '':
            journal_color_index = 6
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]
        else:
            journal_color_index = reflection_data[3]
            if journal_color_index == '':
                        journal_color_index = 6
            
            else: journal_color_index = journal_color_index
            
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]

        journal_row = [ride.ride_id, ride.Flow_id]
        journal_row.extend(reflection_data)

        geometry = ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')

        for each_coord in coords:
            sphere_xyz = helpersMOD.convert_to_xyz(each_coord[1], each_coord[0], sphere_radius)
            sphere_xyz.extend(rgb)
            sphere_xyz.extend(journal_color)
            sphere_xyz.extend([index])
            sphere_xyz.extend([ride.ride_id, ride.Flow_id])
            sphere_xyz.extend([each_coord[1], each_coord[0]])
            sphere_xyz.extend(reflection_data)
            data.append(sphere_xyz)

        radius += 0.001
        sphere_radius += 0.001

    return data

def Render_word_frequency_to_table(ride_list:list) -> list:
    """
    """
    data = []
    header = ['word', 'count']
    word_bank = {}

    data.append(header)

    for each_ride in ride_list:

        current_ride:cibic_objects.Ride = each_ride
        reflection = current_ride.Reflection_data

        if reflection != None:
            selected_words = reflection.answers[1]

            if selected_words != None:
                for each_word in selected_words:
                    
                    # check for submissions prior to complete language selection
                    if type(each_word) == dict:
                        word_count_word = each_word.get('en')
                    else:
                        word_count_word = each_word

                    # add word to word count dict
                    if word_count_word not in list(word_bank.keys()):
                        word_bank[word_count_word] = 1

                    else:
                        word_bank[word_count_word] = word_bank[word_count_word] + 1

    for each_key, each_val in word_bank.items():
        data.append([each_key, each_val])

    return data

def Render_user_frequency_to_table(
    scriptOp:scriptDAT, 
    DATA_op:OP,
    user_map:dict,
    region_str:str) -> list:
    '''
    '''
    data = []
    data.append(['user_id', 'num_rides'])
    
    for each_user, each_val in user_map.items():
        if each_user != None:
            user_rides = DATA_op.Get_Rides_From_User_IDs([each_user])
            num_rides = len([ride for ride in user_rides if ride.region == region_str])
            if num_rides > 0:
                data.append([each_user, num_rides])
            else:
                pass
    return data

def Render_all_user_ride_frequency_to_table(
    scriptOp:scriptDAT, 
    DATA_op:OP, 
    user_map:dict) -> list:
    
    data = []
    data.append(['user_id', 'num_rides'])

    for each_user, each_val in user_map.items():
        if each_user != None:
            user_rides = DATA_op.Get_Rides_From_User_IDs([each_user])
            num_rides = len(user_rides)
            data.append([each_user, num_rides])
    return data

def Render_free_text_response_to_table(scriptOp:scriptDAT, rides:list) -> list:
    data = []
    data.append(['user_id', 'num_rides'])

    for each_ride in rides:
        current_ride: cibic_objects.Ride = each_ride
        journal = current_ride.journaled_data
        if current_ride.user_id != None and journal != None:
            free_text = journal.answers[2]
            if free_text != '' :
                data.append([current_ride.user_id, free_text])
    return data

def Render_pod_data_to_table(scriptOp:scriptDAT, rides:list, user_map:dict) -> list:
    data = []
    data.append(['pod_id', 'flow_name', 'num_users', 'num_journals'])
    rides_with_pods = [ride for ride in rides if ride.pod_id != None]

    # based on custom par
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(30)

    pods = set()
    pod_map = {}

    for each_ride in rides:
        current_ride:cibic_objects.Ride = each_ride
        if current_ride.pod_id != None:
            pods.add(current_ride.pod_id)
            if current_ride.pod_id not in pod_map.keys():
                pod_map[current_ride.pod_id] = {
                    'users' : [],
                    'flow_names' : set(),
                    'journals' : []
                }
    for each_ride in rides:
        current_ride: cibic_objects.Ride = each_ride
        if current_ride.pod_id != None:
            rider = current_ride.user_id
            flow_name = current_ride.flow_name
            journal = current_ride.journaled_data
            pod_user_list = pod_map.get(current_ride.pod_id).get('users')
            flow_set = pod_map.get(current_ride.pod_id).get('flow_names')

            if rider not in pod_user_list:
                pod_user_list.append(rider)
            else:
                pass

            flow_set.add(flow_name)

            if journal != None:
                journal_list = pod_map.get(current_ride.pod_id).get('journals')
                journal_list.append(journal)
        
    for each_pod, pod_vals in pod_map.items():
        user_list = pod_vals.get('users')
        flow_name = pod_vals.get('flow_names')
        journals = pod_vals.get('journals')
        num_rides = 0

        data.append([each_pod, flow_name, len(user_list), len(journals)])

    return data

def Render_all_rides_to_table(scriptOp:scriptDAT, rides:list) -> list:
    data = []
    data.append([
        'date', 
        'ride_id', 
        'user', 
        'region',
        'flow_name', 
        'pod_name', 
        'pod_id',
        'has_journal', 
        'satisfaction',
        'free_response'])
    for each_ride in rides:
        current_ride:cibic_objects.Ride = each_ride
        ride_data = [
            current_ride.end_time, 
            current_ride.ride_id, 
            current_ride.user_id,
            current_ride.region, 
            current_ride.Flow.name, 
            current_ride.pod_name, 
            current_ride.pod_id, 
            True if current_ride.journaled_data != None else False, 
            current_ride.journaled_data.answers[0] if current_ride.journaled_data != None else '-',
            current_ride.journaled_data.answers[2] if current_ride.journaled_data != None else '-']
        # add each ride to data block
        data.append(ride_data)

    return data
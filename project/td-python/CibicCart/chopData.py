from datetime import datetime, timezone
import cartHelpers
import CibicObjects

# NOTE - CHOP Channel Processing 
def Build_chans_all_rides(scriptOp:scriptCHOP) -> dict:

    color_lookup = op('null_color_lookup')
    color_journal_lookup = op('null_color_journal_lookup')

    source_data = parent().Rides
    coord_index = 0
    r_chan = []
    g_chan = []
    b_chan = []
    journal_r_chan = []
    journal_b_chan = []
    journal_g_chan = []
    index_chan = []
    raw_lat_chan = [] 
    raw_lon_chan = []
    satisfaction_chan = []
    
    for each_ride in source_data:
        ride_index = source_data.index(each_ride)
        rgb = [color_lookup['r'][ride_index], color_lookup['g'][ride_index], color_lookup['b'][ride_index]]
        reflection_data = each_ride.Reflection_data.answers if each_ride.Reflection_data != None else ''

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
        
            else:
                journal_color_index = journal_color_index
            
            journal_color = [
                color_journal_lookup['r'][journal_color_index], 
                color_journal_lookup['g'][journal_color_index], 
                color_journal_lookup['b'][journal_color_index]]

        geometry = each_ride.Geo_JSON_Path_Only_Obj
        coords = geometry.get('geometry').get('coordinates')

        # # if geometry.get('type') == 'LineString':
        for each_coord in coords:
            lat, long = each_coord[1], each_coord[0]
            r_chan.append(rgb[0])
            g_chan.append(rgb[1])
            b_chan.append(rgb[2])
            journal_r_chan.append(journal_color[0])
            journal_g_chan.append(journal_color[1])
            journal_b_chan.append(journal_color[2])
            index_chan.append(ride_index)
            raw_lat_chan.append(lat)
            raw_lon_chan.append(long)
            satisfaction_chan.append(reflection_data[0] if reflection_data != '' else 0)

    data = {
        'samples' : len(r_chan),
        'channels' : {
            'r' : r_chan,
            'g' : g_chan,
            'b' : b_chan,
            'journal_r' : journal_r_chan,
            'journal_g' : journal_g_chan,
            'journal_b' : journal_b_chan,
            'index' : index_chan,
            'raw_lat' : raw_lat_chan,
            'raw_lon' : raw_lon_chan,
            'satisfaction' : satisfaction_chan
        }
    }
    return data


def Build_chans_all_flows(scriptOp:scriptCHOP) -> dict:

    flow_map = parent().Flow_Map
    index = 0

    index_chan = []
    raw_lat_chan = [] 
    raw_lon_chan = []

    for flow_key, flow_vals in flow_map.items():		
        flow_paths = flow_vals.Paths
        for each_path in flow_paths:
            flow_path = each_path.get('flowPath')

            if flow_path != None:
                geometry = each_path.get('flowPath').get('geometry')
                if geometry != None:
                    coords = geometry.get('coordinates')
                    for each_coord in coords:
                        lat, long = each_coord[1], each_coord[0]
                        raw_lat_chan.append(lat)
                        raw_lon_chan.append(long)
                        index_chan.append(index)

    data = {
        'samples' : len(raw_lon_chan),
        'channels' : {
            'index_chan' : index_chan,
            'raw_lat_chan' : raw_lat_chan,
            'raw_lon_chan' : raw_lon_chan
        }
    }
    return data

def Build_chans_all_flow_join_points(scriptOp:scriptCHOP) -> dict:

    flow_map = parent().Flow_Map
    index = 0

    index_chan = []
    raw_lat_chan = [] 
    raw_lon_chan = []

    for flow_key, flow_vals in flow_map.items():		
        flow_paths = flow_vals.Paths
        for each_path in flow_paths:
            flow_path = each_path.get('flowPath')

            if flow_path != None:
                geometry = each_path.get('flowPath').get('geometry')
                if geometry != None:
                    coords = geometry.get('coordinates')
                    for each_coord in coords:
                        lat, long = each_coord[1], each_coord[0]
                        raw_lat_chan.append(lat)
                        raw_lon_chan.append(long)
                        index_chan.append(index)
    
                    index += 1

    data = {
        'samples' : len(index_chan),
        'channels' : {
            'index_chan' : index_chan,
            'raw_lat_chan' : raw_lat_chan,
            'raw_lon_chan' : raw_lon_chan
        }
    }

    return data

def Build_chans_rider_satisfaction(scriptOp:scriptCHOP) -> dict:
    channels = {}
    max_rides = []

    user_index = 0
    user_ids = parent().User_IDs
    for each_user in user_ids:
        satisfaction = []
        user_ride_data = parent().Get_Rides_From_User_IDs([each_user])
        max_rides.append(len(user_ride_data))

        for each_ride in user_ride_data:
            if each_ride.Reflection_data == None:
                satisfaction.append(0)
            else:
                satisfaction.append(each_ride.Reflection_data.answers[0])

        channels[f"user{user_index}"] = satisfaction
        user_index += 1
        print(each_user)

    data = {
        'samples' : max(max_rides),
        'channels' : channels
    }

    return data
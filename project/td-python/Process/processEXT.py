"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import logging
import Lookup
import CibicCart
from datetime import datetime, timezone, timedelta
import SudoMagic as smTools
import os

# i surrender
from CibicObjects import cibic_objects

class Process:
    """Process

    The Process class is responsible for handling this project's rendering 
    and image processing. This includes:
    
        -> mapbox rendering
        -> mapbox and ride data composite
        -> abstract visualization
        -> additional composites of abstract data viz and map views
        -> Rendering images to file for AWS cloud rendering
    """

    COLOR_LOOKUP = Lookup.PROCESS.op('base_assets/null_color_lookup')
    COLOR_JOURNAL_LOOKUP = Lookup.PROCESS.op('base_assets/null_color_journal_lookup')
    RIDE_SIZE = 0

    AWS_OUTPUT_TOP = Lookup.PROCESS.op('base_compositor/moviefileout_viz')
    MAPBOX_COMP = Lookup.PROCESS.op('base_mapbox/MapboxTD')

    region_map = {
        'LA' : 'Los Angeles',
        'BA': 'Buenos Aires'
    }

    def __init__(self, myOp):
        self.My_op = myOp
        self._set_rides_coordinate_width(Lookup.DATA.Rides)
        logging.info(f"PROCESS 🏭 | Process Init")

    def Touch_start(self):
        """
        """
        logging.info(f"PROCESS 🏭 | Process Touch_start")

        # download remote media and cache locally
        self.Download_remote_media()

    def Set_output_map_target(self, city:str) -> None:
        """Sets Mapbox pars to defaults specified in the Project Class
        """

        mapbox_pars = Lookup.PROJECT.MAPBOX_PAR_MAP.get(city)

        if mapbox_pars != None:
            for each_key, each_val in mapbox_pars.items():
                Process.MAPBOX_COMP.par[each_key] = each_val
        
        pass

    def Download_remote_media(self) -> None:
        '''Builds a list of all remote media and downaloads to the local project
        '''
        downlaoder = self.My_op.op('base_assets/base_threaded_downloader')
        downlaoder.Fetch_files(self._get_remote_media_paths())
    
    def Load_rider_media(self) -> None:
        rider_media_mov_buffer = self.My_op.op('base_assets/moviefilein_rider_media')
        rider_media_cache = self.My_op.op('base_assets/tex3d_rider_media')
        media_cache = f"{project.folder}/_exports/img_cache"
        media_files = os.listdir(media_cache)

        rider_media_cache.par.cachesize = len(media_files) - 1
        rider_media_cache.par.resetpulse.pulse()

        for each_index, each_file in enumerate(media_files):
            rider_media_cache.par.replaceindex = each_index
            rider_media_mov_buffer.par.file = f"{media_cache}/{each_file}"
            rider_media_cache.par.replacesinglepulse.pulse()

    def _get_remote_media_paths(self) -> list:
        '''Loops through all rides to find paths to remote media
        '''
        rides = Lookup.DATA.Rides
        remote_paths = []
        video_ext = ['mov', 'MOV']

        for each_ride in rides:
            journal = each_ride.journaled_data
            if journal != None:
                media = journal.media
                if media != None:
                    for each_media_item in media:
                        file_ext = each_media_item[-3:]
                        if file_ext in video_ext:
                            pass
                        else:
                            remote_paths.append(each_media_item)
        return remote_paths

    # NOTE - Image Output
    def Run_cloud_render_process(self) -> None:
        """
        """
        delay_seconds = 5
        Lookup.PROCESS.op("base_mapbox").cook(force=True, recurse=True)

        delay_args = [
            [0, 1, True],
            [0, 1, False],
            [1, 1, True],
            [1, 1, False]
        ]

        delay_script = 'args[0]._render_view(args[1], args[2], args[3])'

        ipar.Settings.Active = True

        for index, each in enumerate(delay_args):
            delay_frames = (delay_seconds * 60) * (index + 1)
            run(delay_script, self, each[0], each[1], each[2], delayFrames=delay_frames)

        delay_active_complete = "args[0]._cloud_render_complete()"
        run(delay_active_complete, self, delayFrames = (delay_seconds * 60) * (len(delay_args)+1))

    def _rides_by_region(self:callable) -> list:
        '''Rides filtered by currently selected region
        '''
        region = ipar.Settings.Location.eval()
        region_str = Process.region_map.get(region)

        # based on custom par
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(ipar.Settings.Previousdaysofdata.eval())
        all_rides = Lookup.DATA.Get_Rides_From_Time_Range(start, end)

        region_rides = [ride for ride in all_rides if ride.region == region_str]        
        rides_with_flows = [ride for ride in region_rides if ride.Flow.name != None]
        rides_with_journals = [ride for ride in rides_with_flows if ride.Reflection_data != None]
        
        # which list of rides do we output
        output_rides = rides_with_flows

        self._set_rides_coordinate_width(output_rides)

        return output_rides

    def _cloud_render_complete(self:callable) -> None:
        logging.info('Cloud Rendering Complete')
        ipar.Settings.Active = False

    def _get_mapbox_loaded(self:callable):
            return Lookup.PROCESS.op("base_mapbox/MapboxTD").par.Loaded
    
    def _render_view(self, location:int=0, view:int=0, recent:bool=False) -> None:
        ipar.Settings.Location = location
        ipar.Settings.Selectedview = view
        self._render_current_view_to_file(recent)
    
    def _render_la_view(self) -> None:
        ipar.Settings.Location = 0
        ipar.Settings.Selectedview = 1
        run('args[0]._render_current_view_to_file(args[1])', self, True, delayFrames=60)
        run('args[0]._render_current_view_to_file(args[1])', self, False, delayFrames=70)

    def _render_ba_view(self) -> None:
        ipar.Settings.Location = 1
        ipar.Settings.Selectedview = 1
        run('args[0]._render_current_view_to_file(args[1])', self, True, delayFrames=60)
        run('args[0]._render_current_view_to_file(args[1])', self, False, delayFrames=70)

    def _render_current_view_to_file(self, recent:bool=False) -> str:
        """
        """
        current_region = ipar.Settings.Location.eval()
        sequence_index = 0
        file_name = self._build_file_name(recent, current_region, sequence_index)
        file_path = f'{ipar.Settings.Outputdirectory}/{file_name}.jpg'

        Process.AWS_OUTPUT_TOP.par.file = file_path
        Process.AWS_OUTPUT_TOP.par.record.pulse()
        logging.info(f"PROCESS 🏭 | rendering to file")
        return file_path

    def _build_file_name(self, recent:bool=False, region:str='LA', sequence_index:int=0) -> str:
        """
        """
        current_date = smTools.datetime.datetime.now()

        if recent:
            file_name = f"{region}-recent"
        else:
            file_name = f"{region}-{current_date.month}-{current_date.day}-{current_date.year}-TD-{sequence_index}"
        print(file_name)
        return file_name

    def _set_rides_coordinate_width(self, ride_list:list) -> None:
        coords_list = []
        for each_ride in ride_list:
            current_ride = each_ride
            geometry = current_ride.Geo_JSON_Path_Only_Obj
            coords = geometry.get('geometry').get('coordinates')

            if coords != None:
                coords_list.append(coords)

        coord_len = [len(each) for each in coords_list]
        Process.RIDE_SIZE = max(coord_len)
        return None

    # NOTE - DAT Processing 
    def Render_word_frequency_to_table(self, scriptOp:scriptDAT) -> list:
        rides = self._rides_by_region()
        data = CibicCart.datData.Render_word_frequency_to_table(rides)
        return data 

    def Render_user_frequency_to_table(self, scriptOp:scriptDAT) -> list:
        '''
        '''
        user_map = Lookup.DATA.User_Map
        region = ipar.Settings.Location.eval()
        region_str = Process.region_map.get(region)
        data = CibicCart.datData.Render_user_frequency_to_table(scriptOp, Lookup.DATA, user_map, region_str)

        return data

    def Render_all_user_ride_frequency_to_table(self, scriptOp:scriptDAT) -> list:
        user_map = Lookup.DATA.User_Map
        data = CibicCart.datData.Render_all_user_ride_frequency_to_table(
            scriptOp,
            Lookup.DATA,
            user_map)

        return data

    def Render_all_rides_to_table(self, scriptOp:scriptDAT) -> list:
        rides = Lookup.DATA.Rides
        data = CibicCart.datData.Render_all_rides_to_table(
            scriptOp,
            rides)
        return data

    def Render_current_rides_to_table(self, scriptOp:scriptDAT) -> list:
        rides = self._rides_by_region()
        data = CibicCart.datData.Render_all_rides_to_table(
            scriptOp,
            rides)
        return data

    def Render_free_text_response_to_table(self, scriptOp:scriptDAT) -> list:
        rides = self._rides_by_region()
        data = CibicCart.datData.Render_free_text_response_to_table(scriptOp, rides)
        return data

    def Render_pod_data_to_table(self, scriptOp:scriptDAT) -> list:
        rides = self._rides_by_region()
        user_map = Lookup.DATA.User_Map
        data = CibicCart.datData.Render_pod_data_to_table(scriptOp, rides, user_map)
        return data

    def Render_flow_table(self, scriptOp:scriptDAT) -> list:
        data = []
        header = ['flow_name', 'rides']

        data.append(header)

        rides = self._rides_by_region()
        flow_dict = {}
        
        for each_ride in rides:
            current_ride:cibic_objects.Ride = each_ride
            flow = current_ride.Flow
            flow_use = len(flow.Rides)

            if current_ride == None:
                pass

            else:
                if flow.name in flow_dict.keys():
                    pass
                else:
                    flow_dict[flow.name] = {
                        'num_rides' : flow_use
                    }

        for each_flow, flow_vals in flow_dict.items():
            row_data = [each_flow, flow_vals.get('num_rides')]
            data.append(row_data)

        return data

    # NOTE - TOP Processing 
    def Build_texture_position_all_rides(self, scriptOp:scriptTOP) -> callable:
        rides = self._rides_by_region()
        numpy_array = CibicCart.topData.Build_texture_position_all_rides(
            rides, 
            None,
            Process.RIDE_SIZE, 
            scriptOp)
        return numpy_array

    def Build_texture_position_pods(self, scriptOp:scriptTOP) -> callable:
        rides = self._rides_by_region()
        pod_map = Lookup.DATA.Pod_Map
        matched_rides = []
        pod_popularity = []

        # find pods in current rides
        pods_in_current_rides = set()
        for each_ride in rides:
            
            if each_ride.pod_id == None:
                pass
            else:
                pods_in_current_rides.add(each_ride.pod_id)

        for each_pod in pods_in_current_rides:
            current_pod = pod_map.get(each_pod)
            for each_user in current_pod.users:
                for each_ride in each_user.Rides:
                    if each_ride.pod_id == each_pod:
                        matched_rides.append(each_ride)
                        pod_popularity.append(len(current_pod.users))
                        break
        
        pod_len = [len(each_ride.Geo_JSON_Path_Only_Obj.get('geometry').get('coordinates')) for each_ride in matched_rides]
        numpy_array = CibicCart.topData.Build_texture_position_all_rides(
            matched_rides, 
            pod_popularity,
            max(pod_len),
            scriptOp)
        return numpy_array

    def Build_texture_color_all_rides(self, scriptOp:scriptTOP) -> callable:
        rides = self._rides_by_region()
        numpy_array = CibicCart.topData.Build_texture_color_all_rides(
            rides,
            Process.RIDE_SIZE,
            Process.COLOR_JOURNAL_LOOKUP,
            scriptOp)
        return numpy_array

    def Build_texture_flows(self, scriptOp:scriptTOP) -> callable:
        rides = self._rides_by_region()
        numpy_array = CibicCart.topData.Build_texture_flows2(
            rides,
            scriptOp)
        return numpy_array

    def Build_texture_satisfaction_data_by_rider(self, scriptOp:scriptTOP) -> callable:
        region = ipar.Settings.Location.eval()
        region_str = Process.region_map.get(region)

        user_map = Lookup.DATA.User_Map
        rides_by_user = []
        user_count = 0

        for each_user, each_val in user_map.items():
            if each_user != None:
                user_count += 1
                user_dict = {}
                raw_rides = Lookup.DATA.Get_Rides_From_User_IDs([each_user])
                rides = [ride for ride in raw_rides if ride.region == region_str]
                num_rides = len(rides)
                if num_rides <= 0:
                    pass
                else:
                    user_dict['user_id'] = each_user
                    user_dict['rides'] = rides
                    user_dict['num_rides'] = num_rides
                    rides_by_user.append(user_dict)

        num_rides_list = [each_ride.get('num_rides') for each_ride in rides_by_user]
        max_rides = max(num_rides_list)

        numpy_array = CibicCart.topData.Build_texture_satisfaction_data_by_rider(
            rides_by_user,
            max_rides,
            Process.COLOR_JOURNAL_LOOKUP,
            scriptOp)
        return numpy_array
    
    def Build_texture_point_per_ride_along_path(self, scriptOp:scriptTOP) -> callable:
        rides = self._rides_by_region()
        numpy_array = CibicCart.topData.Point_per_ride_along_path(
            rides,
            scriptOp)

        return numpy_array
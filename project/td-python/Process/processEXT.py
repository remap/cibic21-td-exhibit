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
import random
import cloudRenderMOD

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

    CAMERA_TIMER = Lookup.PROCESS.op('base_map_abstract_view/timer1')
    AWS_OUTPUT_TOP = Lookup.PROCESS.op('base_compositor/moviefileout_viz')
    MAPBOX_COMP = Lookup.PROCESS.op('base_mapbox/MapboxTD')

    region_map = {
        'LA' : 'Los Angeles',
        'BA': 'Buenos Aires'
    }

    def __init__(self, myOp):
        self.My_op = myOp
        self._set_rides_coordinate_width(Lookup.DATA.Rides)
        self.CloudRenderManager = None
        logging.info(f"PROCESS 🏭 | Process Init")

    def Touch_start(self):
        """
        """
        logging.info(f"PROCESS 🏭 | Process Touch_start")

        # download remote media and cache locally
        # self.Download_remote_media()

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
        media_cache = f"{project.folder}/_outputs/photos"
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

    def Media_random_loc(self):
        rides = Lookup.DATA.Rides
        remote_paths = []
        img_coords = []
        video_ext = ['mov', 'MOV']

        for each_ride in rides:
            each_ride:cibic_objects.Ride
            journal = each_ride.journaled_data
            if journal != None:
                media = journal.media
                
                if media != None:
                    ride_path = each_ride.Geo_JSON_Path_Coords
                    rand_index = random.randint(0, len(ride_path)-1)

                    for each_media_item in media:
                        file_ext = each_media_item[-3:]
                        if file_ext in video_ext:
                            pass
                        else:
                            rand_coord = ride_path[rand_index]
                            img_coords.append(rand_coord)

        return img_coords

    # NOTE - Image Output
    def Run_cloud_render_process(self) -> None:
        '''
        '''
        # turn off realtime
        project.realTime = False

        # toggle active flag
        ipar.Settings.Active = True

        # force cook mapbox
        Lookup.PROCESS.op("base_mapbox").cook(force=True, recurse=True)

        # generate render jobs and start render stack
        render_jobs = Lookup.DATA.Get_render_jobs()
        self.CloudRenderManager = cloudRenderMOD.renderManager(job_list=render_jobs)
        self.CloudRenderManager.advance()
    
    def Video_render_timer_cycle(self, timerOp:OP) -> None:
        if ipar.Settings.Active:
            # we're currently running a render job
            current_worker:cloudRenderMOD.renderWorker = self.CloudRenderManager.Get_current_worker()
            if current_worker != None:
                # render cycle has completed and we can mark video as done
                current_worker.set_video_complete(True)
            else:
                # Nonetype - there is no current worker
                pass

    # NOTE Mapbox and Ride Info
    def _get_mapbox_loaded(self:callable):
            return Lookup.PROCESS.op("base_mapbox/MapboxTD").par.Loaded

    def _rides_by_region(self:callable, region:str) -> list:
        '''Rides filtered by currently selected region
        '''
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
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
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
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        data = CibicCart.datData.Render_all_rides_to_table(
            scriptOp,
            rides)
        return data

    def Render_free_text_response_to_table(self, scriptOp:scriptDAT) -> list:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        data = CibicCart.datData.Render_free_text_response_to_table(scriptOp, rides)
        return data

    def Render_pod_data_to_table(self, scriptOp:scriptDAT) -> list:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        user_map = Lookup.DATA.User_Map
        data = CibicCart.datData.Render_pod_data_to_table(scriptOp, rides, user_map)
        return data

    def Render_flow_table(self, scriptOp:scriptDAT) -> list:
        data = []
        header = ['flow_name', 'rides', 'flow_satisfaction', 'journal_to_ride_ratio']

        data.append(header)

        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        
        flow_dict = {}
        
        for each_ride in rides:
            current_ride:cibic_objects.Ride = each_ride
            flow = current_ride.Flow
            flow_use = len(flow.Rides)
            flow_satisfaction = []

            for each_flow_ride in flow.Rides:
                each_flow_ride:cibic_objects.Ride
                if each_flow_ride.Reflection_data != None:
                    satisfaction = each_flow_ride.Reflection_data.answers[0]
                    flow_satisfaction.append(satisfaction)

            if current_ride == None:
                pass

            else:
                if flow.name in flow_dict.keys():
                    pass
                else:
                    flow_dict[flow.name] = {
                        'num_rides' : flow_use,
                        'flow_satisfaction' : flow_satisfaction,
                        'journal_to_ride_ratio' : round(len(flow_satisfaction) / flow_use, 3)
                    }

        for each_flow, flow_vals in flow_dict.items():
            row_data = [
                each_flow, 
                flow_vals.get('num_rides'), 
                flow_vals.get('flow_satisfaction'),
                flow_vals.get('journal_to_ride_ratio')]
            data.append(row_data)

        return data

    # NOTE - TOP Processing 
    def Build_texture_position_all_rides(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        numpy_array = CibicCart.topData.Build_texture_position_all_rides(
            rides, 
            None,
            Process.RIDE_SIZE, 
            scriptOp)
        return numpy_array

    def Build_texture_position_pods(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
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
        region = scriptOp.parent().par.Location.eval()
        
        rides = self._rides_by_region(region)
        numpy_array = CibicCart.topData.Build_texture_color_all_rides(
            rides,
            Process.RIDE_SIZE,
            Process.COLOR_JOURNAL_LOOKUP,
            scriptOp)
        return numpy_array

    def Build_texture_flows(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        numpy_array = CibicCart.topData.Build_texture_flows2(
            rides,
            scriptOp)
        return numpy_array
    
    def Build_colormap_flows(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        numpy_array = CibicCart.topData.Colormap_by_common_user_selection(
            rides,
            Process.COLOR_JOURNAL_LOOKUP,
            scriptOp)
        return numpy_array

    def Build_texture_satisfaction_data_by_rider(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
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
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)
        numpy_array = CibicCart.topData.Point_per_ride_along_path(
            rides,
            scriptOp)

        return numpy_array

    def Build_texture_point_per_ride_along_path_color(self, scriptOp:scriptTOP) -> callable:
        region = scriptOp.parent().par.Location.eval()
        rides = self._rides_by_region(region)

        numpy_array = CibicCart.topData.Point_per_ride_along_path_color(
            rides,
            Process.COLOR_JOURNAL_LOOKUP,
            scriptOp)

        return numpy_array
"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import Lookup
import SudoMagic
import logging

class renderManager:
    '''
    '''
    def __init__(self, job_list:list=[]):
        self.Name = 'HAL'
        self.worker_stack = []
        self.Current_worker = None
        self.generate_stack(job_list)

    def generate_stack(self, job_list:list=[]) -> None:
        '''
        '''        
        for each_index, each_job in enumerate(job_list):
            
            new_job = renderWorker(
                workerName=f'render job {each_index}',
                renderManager=self,
                jobName=each_job.get('renderJobName'),
                isImg=each_job.get('isImg'),
                isVideo=each_job.get('isVideo'),
                delayCall=each_job.get('delay'), 
                sequenceIndex=each_job.get('sequenceIndex'),
                gallery=each_job.get('gallery'),
                recent=each_job.get('recent'),
                renderFrame=each_job.get('renderFrame'),
                iparSettings=each_job.get('iparSettings'))
            self.worker_stack.append(new_job)
        
        for each_index, each_stack_job in enumerate(self.worker_stack[:-1]):
            next_worker = self.worker_stack[each_index+1]
            each_stack_job.next_item = next_worker

    def Get_current_worker(self) -> callable:
        return self.Current_worker

    def advance(self) -> None:
        '''
        '''
        # advance to the next item in the stack
        if len(self.worker_stack) > 0:
            next_item:renderWorker = self.worker_stack.pop(0)
            self.Current_worker = next_item
            next_item.RunAction()

        # we've completed all render tasks, reset network
        else:
            project.realTime = True            
            ipar.Settings.Outputsizew = 3840
            ipar.Settings.Outputsizeh = 2160
            Lookup.PROCESS.CAMERA_TIMER.par.cue = False
            Lookup.PROCESS.CAMERA_TIMER.par.play = True
    
            # toggle active flag
            ipar.Settings.Active = False

            logging.info('CLOUD RENDER ☁️ | All items in stack complete ✅')

class renderWorker:
    '''
    '''
    def __init__(
            self,
            workerName:str=None,
            renderManager:callable= None,
            jobName:str=None,
            isImg:bool=False,
            isVideo:bool=False,
            delayCall:int=0,
            sequenceIndex:int=0,
            gallery:bool=False,
            recent:bool=False,
            renderFrame:int=0,
            iparSettings:dict={},
            nextItem:callable=None):
        
        self.Worker_name = workerName
        self._renderManager = renderManager
        self._job_name = jobName
        self._isImg = isImg
        self._isVideo = isVideo
        self._delay_call = delayCall
        self._sequenceIndex = sequenceIndex
        self._gallery = gallery
        self._recent = recent
        self._render_frame = renderFrame
        self._iparSettings = iparSettings
        self._next_item = nextItem
        self._state = False
        self._render_ready = False
        self._video_complete = False

    # NOTE - state managers for DoWhen
    def get_state(self):
        '''
        '''
        return self._state
    
    def set_state(self, val):
        '''
        '''
        self._state = val

    def get_render_ready(self):
        '''
        '''
        return self._render_ready
    
    def set_render_ready(self, val):
        self._render_ready = val

    def get_video_complete(self):
        return self._video_complete

    def set_video_complete(self, val):
        self._video_complete = val

    # NOTE Utilities
    def RunAction(self) -> None:
        '''
        '''
        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} running action")
        delay_update = "args[0].set_state(True)"
        run(delay_update, self, delayFrames=self._delay_call)

        SudoMagic.DoWhen(self.render, self.get_state)
        pass

    def render(self) -> None:
        '''
        '''
        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} starting render")
        
        if self._isImg:
            self._render_img()
        
        elif self._isVideo:
            self._render_video()
        
        else:
            pass
            
    def _advance_stack(self):
        '''
        '''
        logging.info('CLOUD RENDER ☁️ | worker advance')
        try:
            mgmt = self._renderManager
            mgmt.advance()
        except Exception as e:
            debug(e)

    def _build_file_name(self, recent:bool=False, gallery:bool=False, region:str='LA', sequence_index:int=0) -> str:
        '''
        '''
        current_date = SudoMagic.datetime.datetime.now()

        if recent:
            if gallery: 
                file_name = f"{region}-{sequence_index:02d}"
            else:
                file_name = f"{region}-recent"
        else:
            file_name = f"{region}-{current_date.month}-{current_date.day}-{current_date.year}-TD-{sequence_index}"
        logging.info(f'CLOUD RENDER ☁️ | generating file name {file_name}')
        return file_name

    # NOTE Rendering Video
    def _render_video(self) -> None:
        '''
        '''
        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} rendering video")

        # set appropriate pars
        ipar.Settings.Location = self._iparSettings.get('Location')
        ipar.Settings.Selectedview = self._iparSettings.get('Selectedview')
        # set resolution
        ipar.Settings.Outputsizew = self._iparSettings.get('Outputsizew')
        ipar.Settings.Outputsizeh = self._iparSettings.get('Outputsizeh')

        # turn off play on camera and cue to beginning of timer
        Lookup.PROCESS.CAMERA_TIMER.par.play = False
        Lookup.PROCESS.CAMERA_TIMER.par.cuepoint = 0
        Lookup.PROCESS.CAMERA_TIMER.par.cue = True

        # render image after setting and waiting
        delay_render_state = "args[0].set_render_ready(args[1])"
        run(delay_render_state, self, True, delayFrames=self._delay_call)

        SudoMagic.DoWhen(self._render_video_to_file_start, self.get_render_ready)

    def _render_video_to_file_start(self) -> None:
        '''
        '''
        
        # generate file name
        current_region = ipar.Settings.Location.eval()
        sequence_index = self._sequenceIndex
        recent = self._recent
        gallery = self._gallery
        file_name = self._build_file_name(
            recent=recent, 
            gallery=gallery, 
            region=current_region, 
            sequence_index=sequence_index)
        file_path = f'{ipar.Settings.Outputdirectory}/{file_name}.mp4'

        Lookup.PROCESS.AWS_OUTPUT_TOP.par.type = 0
        Lookup.PROCESS.AWS_OUTPUT_TOP.par.videocodec = 3

        Lookup.PROCESS.AWS_OUTPUT_TOP.par.file = file_path
        
        # start timer
        Lookup.PROCESS.CAMERA_TIMER.par.play = True
        Lookup.PROCESS.CAMERA_TIMER.par.cue = False

        #start recording
        Lookup.PROCESS.AWS_OUTPUT_TOP.par.record = True

        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} starting video render - {file_name}")

        SudoMagic.DoWhen(self._render_video_to_file_end, self.get_video_complete)
        
    def _render_video_to_file_end(self):
        Lookup.PROCESS.AWS_OUTPUT_TOP.par.record = False
        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} completing video render")
        self._advance_stack()

    # NOTE Rendering Images
    def _render_img(self) -> None:
        '''
        '''
        logging.info(f"CLOUD RENDER ☁️ | {self.Worker_name} rendering image")
        
        # NOTE start the render_view

        ipar.Settings.Location = self._iparSettings.get('Location')
        ipar.Settings.Selectedview = self._iparSettings.get('Selectedview')
        ipar.Settings.Outputsizew = self._iparSettings.get('Outputsizew')
        ipar.Settings.Outputsizeh = self._iparSettings.get('Outputsizeh')

        Lookup.PROCESS.CAMERA_TIMER.par.play = False
        Lookup.PROCESS.CAMERA_TIMER.par.cue = True
        Lookup.PROCESS.CAMERA_TIMER.par.cuepoint = self._render_frame

        self.set_render_ready(False)

        # render image after setting and waiting
        delay_render_state = "args[0].set_render_ready(args[1])"
        run(delay_render_state, self, True, delayFrames=self._delay_call)

        SudoMagic.DoWhen(self._render_img_to_file, self.get_render_ready)

    
    def _render_img_to_file(self) -> str:
        '''
        '''
        current_region = ipar.Settings.Location.eval()

        file_name = self._build_file_name(
            recent=self._recent, 
            gallery=self._gallery,
            region=current_region, 
            sequence_index=self._sequenceIndex)
        
        file_path = f'{ipar.Settings.Outputdirectory}/{file_name}.jpg'

        Lookup.PROCESS.AWS_OUTPUT_TOP.par.type = 1
        Lookup.PROCESS.AWS_OUTPUT_TOP.par.imagefiletype = 1

        Lookup.PROCESS.AWS_OUTPUT_TOP.par.file = file_path
        Lookup.PROCESS.AWS_OUTPUT_TOP.par.record.pulse()

        logging.info(f'CLOUD RENDER ☁️ | {self.Worker_name} rendering to file {file_path}')
        # advance when complete
        self._advance_stack()

        return file_path

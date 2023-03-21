"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

# td python mods
import SudoMagic as smTools
import Lookup

# pure python
import json
import socket
import logging

class Project:
    """ Project Class

    The project class is responsible for the construction and distribution
    of all extensions. _setup() constructs extensions in order, allowing
    for a reliable and consistent start-up sequence for all python extensions

    Additionally the Project class is responsible for start-up functions
    that include loading settings from file.
    """

    #NOTE - other class variables
    _config_default_overrides = "data/default_overrides.json"
    New_default_profile = "default_profile.json"
    CLOUD_RENDER_DELAY_FRAMES = 60

    LA_MAPBOX = {
        "Targetzoom" : 12.5,
        "Targetlatlng1" : 34.0739,
        "Targetlatlng2" : -118.222
    }
    BA_MAPBOX = {
        "Targetzoom" : 14.5,
        "Targetlatlng1" : -34.61805,
        "Targetlatlng2" : -58.41304
    }

    MAPBOX_PAR_MAP = {
        'LA' : LA_MAPBOX,
        'BA' : BA_MAPBOX
    }

    def __init__(self, myOp:callable) -> None:
        self.My_op = myOp
        logging.info(f"PROJECT 🏛️ | Project Init from {myOp}")
        self._setup()

    def _setup(self) -> None:
        """Private Setup Function

        Currently a placeholder for additional extension setup routines

        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        None      
        """
        
        logging.info("PROJECT 🏛️ | Running _setup()")

    def Touch_start_dev(self) -> None:
        """Starts process as developer
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        None      
        """

        ####### FOR DEVELOPMENT ONLY #######
        self.Touch_start()

    def Touch_start(self) -> None:
        """Touch_start for project - runs ordered start-up sequence for project
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        None     
        """

        logging.info(f"PROJECT 🏛️ | Starting Touch_start() call - {self.My_op} ")

        ipar.Settings.Rootpath = var("PUBLIC")
        project.paths['log'] = f'{var("PUBLIC")}\\log'
        project.paths['assets'] = f'{var("PUBLIC")}\\assets'
        project.paths['media'] = f'{var("PUBLIC")}\\assets\\media'
        project.paths['thumbnails'] = f'{var("PUBLIC")}\\assets\\imgs\\thumbnails'
        project.paths['data'] = f'{var("PUBLIC")}\\data'
        project.paths['profile'] = f'{var("PUBLIC")}\\data\profile'

        # set project profile json file
        ipar.Settings.Projectprofile = f'{var("PUBLIC")}\\data\profile\\cibic-exhibit-profile.json'

        # load project profile
        self.Load_project_profile()

        # set addresses and machine name		
        ipar.Settings.Ipaddress = self._get_machine_ip()
        ipar.Settings.Machinename = self._get_machine_name()

        # set media assets path
        logging.info(f'media assets path: {var("PUBLIC")}\\assets\\media')
        ipar.Settings.Mediaassets = f'{var("PUBLIC")}\\assets\\media'
        ipar.Settings.Mediaassets.readOnly = True

        # calls touch-start extensions
        Lookup.COM.Touch_start()
        Lookup.DATA.Touch_start()        
        Lookup.PROCESS.Touch_start()
        Lookup.OUTPUT.Touch_start()
        Lookup.VIEWS.Touch_start()
        
        # Locks all operators that were saved unlocked. 
        # TODO: remove debug statements
        logging.debug("PROJECT | Touch_start locking all lockable operators")
        for child in self.My_op.findChildren(tags=["unlockOnSave"]):
            child.lock = True

        logging.info(f"PROJECT 🏛️ | Completing Touch_start() call - {self.My_op}")

        # delays running cloud rendering call
        delay_cloud_rendering = "args[0].Cloud_rendering()"
        run(delay_cloud_rendering, self, delayFrames = Project.CLOUD_RENDER_DELAY_FRAMES)

    def Cloud_rendering(self) -> bool:
        """Runs cloud rendering operation

        Checks to see if cloud rendering env var is true
        runs process if the env var is true, otherwise does nothing
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        success_state(`bool`)
        > true if cloud rendering process has been called      
        """

        if ipar.Settings.Cloudrendering:
            # calls op.PROCESS to run cloud rendering method
            Lookup.PROCESS.Run_cloud_render_process()
            logging.info(f"PROJECT 🏛️ | Running Cloud Render")
            success_state = True
        else:
            success_state = False

        return success_state

    def Load_project_data(self, info_dict:dict) -> None:
        """
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        info_dict(`dict`)
        > dictionary of all pars loaded      
        """

        logging.info("PROJECT 🏛️ | loading info dict")

    def Load_project_profile(self) -> None:
        """
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        None      
        """

        project_pars = smTools.Json_to_dict(ipar.Settings.Projectprofile.eval())
        smTools.Update_custom_internal_pars(op.PROJECT, project_pars)
        logging.info(f"PROJECT 🏛️ | profile loaded from {ipar.Settings.Projectprofile.eval()}")

        pass

    def Save_project_profile(self) -> None:
        """
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        None      
        """
        pars_dict = smTools.Custom_pars_to_dict(op.PROJECT.par.iop1.eval(), [])
        smTools.Save_dict_to_json(pars_dict, ipar.Settings.Projectprofile.eval())
        pass

    def Quit_project(self) -> None:
        """Quits project and runs any appropriate shut-down procedures
        """

        project.quit(force=True)

    def _get_machine_ip(self) -> str:
        """Private method to return machine ip as string
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        ip_address (`str`):
        > ip address as string
        """
        machine_ip = socket.gethostbyname(socket.gethostname())
        logging.info(f"PROJECT 🏛️ | Getting Machine IP -> {machine_ip}")
        return machine_ip


    def _get_machine_name(self) -> str:
        """Private method to return machine hostname
        
        Args
        ---------------
        self (`callable`)
        > Class instance

        Returns
        ---------------
        hostname (`str`):
        > hostname as string      
        """
        hostname = socket.gethostname()
        logging.info(f"PROJECT 🏛️ | Getting Machine Hostname -> {hostname}")
        return hostname
    
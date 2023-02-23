import SudoMagic as smTools
from subprocess import Popen
import logging

def Location(par:callable) -> None:
    op.PROCESS.Set_output_map_target(par.eval())

def Active(par:callable) -> None:
    logging.info(f'ipar.Settings | {par.name} - {par.eval()}')
    if par.eval() == False:
        if ipar.Settings.Cloudrendering.eval() == True:
            # close project
            ipar.Settings.Quitproject.pulse()

# NOTE - pulse pars
def Render() -> None:
    logging.info('ipar.Settings | Render pulse')
    op.PROCESS.Run_cloud_render_process()

def Loadprojectprofile() -> None:
    ...

def Saveprojectprofile() -> None:
    ...

def Quitproject() -> None:
    op.PROJECT.Quit_project()
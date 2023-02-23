from datetime import date
import os

def build_toe():

    if build_warning():
        print("Building")
        # remove external tox paths
        remove_ext_tox_paths()

        # remove external script paths
        remove_ext_dat_paths()

        # save project file
        project.save(get_toe_path())

        # quit project
        project.quit(force=True)
    
    else:
        print("no building")
        pass

def remove_ext_tox_paths() -> None:
    """Removes all TOX paths
    """
    all_comps = root.findChildren(type=COMP)

    for each_comp in all_comps:
        if each_comp.par.externaltox != '':
            each_comp.par.externaltox = ''
            log_msg = f"removing external TOX path for {each_comp.name} | {each_comp.path}"
            print(log_msg)
        else:
            pass

def remove_ext_dat_paths() -> None:
    """Removes all DAT paths
    """
    all_dats = root.findChildren(type=DAT)

    for each_dat in all_dats:

        if each_dat.par["file"] != '':
            try:
                each_dat.par["file"] = ''
                log_msg = f"removing external DAT path for {each_dat.name} | {each_dat.path}"
                print(log_msg)
            except Exception as e:
                pass
        else:
            pass

def get_toe_path() -> str:
    """ Return a path for a toe file based on build date
    """
    
    # construct path from build date
    file_dir = f"{project.folder}/_toe-builds/{date.today()}"
    
    # check to see if path exists - if it exists pass, else build dirs
    if os.path.exists(file_dir):
        pass
    else:
        print("making dirs")
        os.makedirs(file_dir)

    # construct and return file path
    file_path = f"{file_dir}/aws.toe"
    return file_path

def build_warning():
    header = "BUILDING TOE FOR AWS"
    body = """You are about to build a TOE for AWS
remote rendering. This is a destrcutive process
and will terminate this TouchDesigner session
upon completion. 

Are you sure you want to Continue?
"""
    buttons = ["No", "Yes"]
    warning = ui.messageBox(header, body, buttons=buttons)
    return warning


import SudoMagic as smTools
import TDJSON
import logging

def Commit_par_changes(**kwargs):
    target = kwargs.get('target_op')
    manifest = kwargs.get('manifest')
    pars_as_json = TDJSON.opToJSONOp(target)
    smTools.Save_dict_to_json(pars_as_json, manifest, sort=False)

    #TODO: remove debug statements
    logging.debug("Commiting ipar changes to file")

def Load_par_changes(**kwargs):
    target = kwargs.get('target_op')
    manifest = kwargs.get('manifest')
    pars_dict = smTools.Json_to_dict(manifest)
    TDJSON.addParametersFromJSONOp(target, pars_dict)
    #TODO: remove debug statements
    logging.debug("Loading ipar changes from file")


    
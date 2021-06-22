import os
import sys

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

@err_catcher(name=__name__)
def maya_get_shots():
    import maya.cmds as cmds
    import maya
    shots = cmds.ls(type="shot")
    result = {}
    for shot in shots:
        shot_path = os.path.join(os.getenv("TMP"), shot + ".mov")
        # if not os.path.exists(shot_path):
        maya.mel.eval("performPlayblastShot(0, \"" + shot + "\")")
        result[shot] = {
            "name": cmds.shot(shot, shotName=True, q=True),
            "outputpath": shot_path}
    return result

@err_catcher(name=__name__)
def app_get_shots():
    try:
        return maya_get_shots()
    except:
        return {}
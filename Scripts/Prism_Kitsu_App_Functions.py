import os
import sys

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


def parse_format(fformat):
    format_dict = {"qt": ".mov"}
    return format_dict.get(fformat, "." + fformat)


@err_catcher(name=__name__)
def maya_get_shots():
    import maya.cmds as cmds
    import maya

    shots = cmds.ls(type="shot")
    result = {}
    for shot in shots:
        shot_path = os.path.join(
            cmds.workspace(expandName=maya.mel.eval("getDefaultPlayblastDirectory()")),
            shot + parse_format(cmds.optionVar(q="playblastFormat")),
        )
        if not os.path.exists(shot_path):
            cmds.optionVar(iv=("playblastSequenceShowOrnaments", origin.chb_useOrnament.isChecked()))
            maya.mel.eval('performPlayblastShot(0, "' + shot + '")')
        result[shot] = {
            "name": cmds.shot(shot, shotName=True, q=True),
            "outputpath": shot_path
        }
    return result


@err_catcher(name=__name__)
def app_get_shots():
    try:
        return maya_get_shots()
    except:
        return {}

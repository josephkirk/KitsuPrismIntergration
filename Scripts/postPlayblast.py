# This script will be executed after the execution of a playblast state in the Prism State Manager.
# You can use this file to define project specific actions, like modifying the created images.

# Example:
# print "Prism has created a playblast."

# If the main function exists in this script, it will be called.
# The "kwargs" argument is a dictionary with usefull information about Prism and the current export.
import os, shutil
IMAGENAMINGRULE = r"{PROJECT_DIR_CENTRAL}\data\review\{publishtype}\{step}\{episode}\{sequence}\{shot}\{version}\{filetype}\{episode}.{sequence}.{shot}.{frame}.{filetype}"
MAYANAMINGRULE = r"{PROJECT_DIR_CENTRAL}\data\review\{publishtype}\{episode}\{sequence}\{shot}\{step}\{episode}.{sequence}.{shot}.{step}.{version}.ma"
STEPTRANSLATE = {
    "anm": "anim",
    "lay": "layout"
}
KITSUSTEPTRANSLATE = {
    "anim": "animation",
    "layout": "layout",
    "anm": "animation",
    "lay": "layout"
}
"""
Copy to data review
"""
import datetime

def getCurrentFocalLength():
    import maya.cmds as cmds
    import maya.OpenMaya as OpenMaya
    import maya.OpenMayaUI as OpenMayaUI

    view = OpenMayaUI.M3dView.active3dView()
    cam = OpenMaya.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    return cmds.getAttr(camPath+".focalLength")

def createTatoo(sourcePathInput, destinationPathInput, titleInput, focalInput, firstFrameInput, lastFrameInput, logoInput):
    import sys
    mod = "C:/vsTools2/SBS/tools/tattooMaker"
    if mod not in sys.path:
        sys.path.append(mod)
    if mod + "/lib" not in sys.path:
        sys.path.append(mod + "/lib")
    import TatooLib
    # print(">"*50)
    # print(sourcePathInput)
    # print(destinationPathInput)
    # print(titleInput)
    # print(focalInput)
    # print(firstFrameInput)
    # print(lastFrameInput)
    # print(logoInput)
    # print("<"*50)
    TatooLib.add_tatoo(sourcePathInput, destinationPathInput, titleInput, focalInput, firstFrameInput, lastFrameInput, logoInput)

def publishToKitsu(projectname, sequencename, shotname, step, movpath, comment = "Publish Playblast"):
    import gazulite
    gazulite.set_host("http://kitsu.virtuos-sparx.com/api")
    gazulite.try_log_in_master()
    project = gazulite.project.get_project_by_name(projectname)
    seq = gazulite.shot.get_sequence_by_name(project, sequencename)
    shot = gazulite.shot.get_shot_by_name(seq, shotname)

    animation = gazulite.task.get_task_type_by_name(step)
    wip = gazulite.task.get_task_status_by_short_name("wip")

    filename, ext = os.path.splitext(movpath)
    tempfile = "D:/Working/Temp/temppreview{}{}".format(datetime.datetime.now().strftime("%d%m%Y-%H%M%S"),ext)
    try:
        task = gazulite.task.get_task_by_name(shot, animation)

        if not os.path.exists("D:/Working/Temp"):
            os.makedirs("D:/Working/Temp")
        shutil.copyfile(movpath, tempfile)
        try:
            comment = gazulite.task.add_comment(task, wip, comment, attachments=[])
        except Exception as why:
            print(why)
        try:
            preview_file = gazulite.task.add_preview(
                task,
                gazulite.task.get_last_comment_for_task(task),
                tempfile
            )
        except Exception as why:
            print(why)
    finally:
        try:
            os.remove(tempfile)
        except:
            pass
    print("Publish to kitsu finished!")

def main(*args, **kwargs):
    print(args)
    print(kwargs)
    core = kwargs["core"]
    projectName = core.projectName
    sceneBasePath = kwargs["core"].scenePath
    shotBasePath = kwargs["core"].shotPath
    task_name = kwargs["state"].l_taskName.text()
    scenePath = kwargs["scenefile"]
    infoPath = core.getVersioninfoPath(scenePath)
    if not os.path.exists(infoPath):
        print("Fail to find version info")
        return
    config = core.getConfig(configPath = infoPath)
    entityName = config.get("entityName")
    version = "{:04d}".format(int(config.get("version").replace("v","")))
    step = STEPTRANSLATE.get(config.get("step")) or config.get("step")
    try:
        seqname, shotname = entityName.split("-")
    except:
        print("Fail to split entity name {}".format(entityName))
        return
    startframe = kwargs["startframe"]
    endframe = kwargs["endframe"]
    outputpath = kwargs["outputpath"]
    episode = core.getConfig(seqname,"episode",config="sequenceinfo")
    # if not episode:
    #     sequenceinfo = os.path.join(shotBasePath, seqname+"-", "sequenceinfo.yml")
    if not episode:
        shotinfoPath = os.path.join(shotBasePath, entityName, "shotinfo.yml")
        if not os.path.exists(shotinfoPath):
            print("Fail to find shot info")
            return
        shotconfig = core.getConfig(configPath = shotinfoPath)
        episode = shotconfig.get("episode") or "MainPack"
    
    # fix dump prism output
    print("Raw Input: {}".format(outputpath))
    outputpath = outputpath.replace(".qt (with audio)", ".qt (with a.mov").replace(".avi (with audio)", ".avi (with a.avi").replace("..",".")

    ouputname, ext = os.path.splitext(outputpath)
    filetype = ext.replace(".","")

    if filetype != "jpg":
        output_target = IMAGENAMINGRULE.format(
            PROJECT_DIR_CENTRAL=os.getenv("PROJECT_DIR_CENTRAL"),
            step = step,
            episode = episode,
            sequence = seqname,
            shot = shotname,
            version = version,
            filetype=filetype,
            publishtype="image",
            frame = "{:04d}-{:04d}".format(startframe, endframe)
        )
    else:
        output_target = IMAGENAMINGRULE.format(
            PROJECT_DIR_CENTRAL=os.getenv("PROJECT_DIR_CENTRAL"),
            step = step,
            episode = episode,
            sequence = seqname,
            shot = shotname,
            version = version,
            filetype=filetype,
            publishtype="image",
            frame = r"{:04d}"
        )

    output_maya_target = MAYANAMINGRULE.format(
        PROJECT_DIR_CENTRAL=os.getenv("PROJECT_DIR_CENTRAL"),
        step = step,
        episode = episode,
        sequence = seqname,
        shot = shotname,
        version = version,
        publishtype="shot",
        frame = "{:04d}-{:04d}".format(startframe, endframe)
    )

    try:
        os.makedirs(os.path.dirname(output_target))
    except:
        pass
    try:
        os.makedirs(os.path.dirname(output_maya_target))
    except:
        pass
    try:
        if filetype != "jpg":
            try:
                print(filetype, outputpath, output_target, episode, seqname, shotname, version, startframe, endframe)
                createTatoo(outputpath, output_target, "{}-{}-{}-{}".format(episode, seqname, shotname, version), "{} mm".format(round(getCurrentFocalLength())), startframe, endframe, "VIRTUOS-SPARX")
            except Exception as why:
                shutil.copyfile(outputpath, output_target)
                print(why, "Attempt Normal copy")
            kitsustep = KITSUSTEPTRANSLATE.get(step)
            if kitsustep: 
                try:
                    publishToKitsu(projectName, seqname, shotname, kitsustep, output_target, comment="Publish Playblast from {} by {}".format(os.path.basename(scenePath), os.getenv("USERNAME")))
                except:
                    print("Failed to pulish to kitsu")
            print("Publish Movie {} to {}".format(outputpath, output_target))
        else:
            files = os.listdir(os.path.dirname(outputpath))
            files.sort()
            for frameid, f in enumerate(files):
                filepath = os.path.join(os.path.dirname(outputpath), f)
                if os.path.isfile(filepath):
                    shutil.copyfile(filepath, output_target.format(frameid))
            print("Publish Sequence:\n {}\n to {}\n Success!".format(outputpath, output_target))
        
    except (IOError, shutil.Error) as why:
        print("Failed to copy playblast {} {} \n{}".format(outputpath, output_target, why))
    try:
        shutil.copyfile(scenePath, output_maya_target)
        print("Publish Maya Scene {} to {}".format(scenePath, output_maya_target))
    except (IOError, shutil.Error) as why:
        print("Failed to copy maya {} {} \n{}".format(scenePath, output_maya_target, why))
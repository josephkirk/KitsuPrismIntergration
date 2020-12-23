#####################################
# https://github.com/EmberLightVFX
#####################################

import os
import gazu

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

@err_catcher(name=__name__)
def removeLastSlash(adress):
    if adress[-1:] == "/":
        adress = adress[:-1]

    return adress

@err_catcher(name=__name__)
def GetEpisodes(project_dict, user=False):
    if user:
        episodes = gazu.user.all_episodes_for_project(project_dict)
    else:
        episodes = gazu.shot.all_episodes_for_project(project_dict)

    return episodes

@err_catcher(name=__name__)
def RemoveEpisode(episode_dict):
    return gazu.shot.remove_episode(episode_dict)

@err_catcher(name=__name__)
def GetSequences(dict, where="from_project", user=False):
    sequences = None
    if user:
        if where == "from_project":
            sequences = gazu.user.all_sequences_for_project(dict)
        else:
            sequences = gazu.user.all_sequences_for_episode(dict)
    else:
        if where == "from_project":
            sequences = gazu.shot.all_sequences_for_project(dict)
        else:
            sequences = gazu.shot.all_sequences_for_episode(dict)

    return sequences

@err_catcher(name=__name__)
def RemoveSequence(sequence_dict):
    return gazu.shot.remove_sequence(sequence_dict)

@err_catcher(name=__name__)
def GetShots(dict, where="from_sequence", user=False, getCanceled=False):
    shots = None

    if user:
        if where == "from_sequence":
            shots = gazu.user.all_shots_for_sequence(dict)
            # Add sequence name as it isn't given from user-catch
            for shot in shots:
                shot.update({'sequence_name': dict["name"]})
        else:
            shots = gazu.user.all_shots_for_project(dict)
    else:
        if where == "from_sequence":
            shots = gazu.shot.all_shots_for_sequence(dict)
        else:
            shots = gazu.shot.all_shots_for_project(dict)

    return shots

@err_catcher(name=__name__)
def RemoveShot(shot_dict):
    return gazu.shot.remove_shot(shot_dict)

@err_catcher(name=__name__)
def GetAssets(proj_dict, asset_type, user=False, getCanceled=False):
    if user:
        assets = gazu.user.all_assets_for_asset_type_and_project(
            proj_dict,
            asset_type)
    else:
        assets = gazu.asset.all_assets_for_project_and_type(
            proj_dict,
            asset_type)

    return assets

@err_catcher(name=__name__)
def RemoveAsset(asset_dict):
    return gazu.asset.remove_asset(asset_dict)

@err_catcher(name=__name__)
def GetAssetType(asset_type_id, user=False):
    assetType = gazu.asset.get_asset_type(asset_type_id)
    return assetType

@err_catcher(name=__name__)
def RemoveAssetType(asset_type_dict):
    return gazu.asset.remove_asset_type(asset_type_dict)

@err_catcher(name=__name__)
def GetAssetTypes():
    return gazu.asset.all_asset_types()

@err_catcher(name=__name__)
def GetEntity(id):
    entity = gazu.entity.get_entity(id)
    return entity

@err_catcher(name=__name__)
def GetEpisodeName(ep_id):
    epDict = gazu.entity.get_entity(ep_id)["name"]
    return epDict


# returns created, updated
@err_catcher(name=__name__)
def DownloadThumbnail(self, name, preview_file_id, folder_name):
    local_preview_id = self.core.getConfig(
        name, "thumbnailID", config=folder_name.lower()
    )

    if preview_file_id != local_preview_id:
        previewImgPath = os.path.join(
            os.path.dirname(self.core.prismIni),
            folder_name,
            "%s_preview" % name,
        )
        if preview_file_id is None:  # Thumbnail removed
            if os.path.isfile(previewImgPath + ".jpg"):
                os.remove(previewImgPath + ".jpg")
            return "", False, True  # File updated

        else:  # Thumbnail added or changed
            file_exists = os.path.exists(previewImgPath + ".jpg")
            if file_exists is False or preview_file_id != local_preview_id:
                # Download the file
                extension = (gazu.files.get_preview_file(preview_file_id)
                            ["extension"])
                thumbnailPath = previewImgPath + "." + extension
                # Make path if it doesn't exist yet
                mkdir_p(
                    os.path.join(
                        os.path.dirname(self.core.prismIni),
                        folder_name
                    )
                )
                gazu.files.download_preview_file_thumbnail(
                    preview_file_id, thumbnailPath)
                # If not jpg, convert it
                if os.path.splitext(thumbnailPath)[1] != ".jpg":
                    # Get image data
                    pixmap = self.core.media.getPixmapFromPath(thumbnailPath)
                    # Save the image as a jpg
                    self.core.media.savePixmap(pixmap, previewImgPath + ".jpg")
                    # Delete old file
                    os.remove(thumbnailPath)

            if file_exists:  # If file got updated
                return preview_file_id, False, True
            else:  # If file didn't exist
                return preview_file_id, True, False

    return False, False, False

@err_catcher(name=__name__)
def createKitsuEpisode(project_dict, episode_name):
    """
    returns
        Episode dict
        If created new episode
    """
    if episode_name is None:
        return None, False

    episode_dict = gazu.shot.get_episode_by_name(project_dict, episode_name)
    if episode_dict is None:
        episode_dict = gazu.shot.new_episode(project_dict, episode_name)
        return episode_dict, True
    else:
        return episode_dict, False

@err_catcher(name=__name__)
def createKitsuSequence(project_dict, sequence_name, episode_dict):
    """
    returns
        Project dict
        If created new sequence
    """

    if episode_dict is None:
        sequence_dict = gazu.shot.get_sequence_by_name(project_dict,
                                                    sequence_name)
    else:
        sequence_dict = gazu.shot.get_sequence_by_name(project_dict,
                                                    sequence_name,
                                                    episode_dict)

    if sequence_dict is None:
        if episode_dict is None:
            sequence_dict = gazu.shot.new_sequence(project_dict,
                                                sequence_name)
        else:
            sequence_dict = gazu.shot.new_sequence(project_dict,
                                                sequence_name,
                                                episode_dicts)
        return sequence_dict, True

    else:
        return sequence_dict, False

@err_catcher(name=__name__)
def createKitsuShot(project_dict, sequence_dict, shot_name, ranges):
    """
    returns
        Shot dict
        If created new shot
    """
    shot_dict = gazu.shot.get_shot_by_name(sequence_dict, shot_name)

    if shot_dict is None:
        if ranges is not None:
            shot_dict = gazu.shot.new_shot(project=project_dict,
                                        sequence=sequence_dict,
                                        name=shot_name,
                                        nb_frames=ranges[1] - ranges[0],
                                        frame_in=ranges[0],
                                        frame_out=ranges[1],
                                        data={})
        else:
            shot_dict = gazu.shot.new_shot(project=project_dict,
                                        sequence=sequence_dict,
                                        name=shot_name,
                                        data={})
        return shot_dict, True
    else:
        return shot_dict, False

@err_catcher(name=__name__)
def createKitsuAssetType(name):
    asset_type_dict = gazu.asset.get_asset_type_by_name(name)
    if asset_type_dict is None:
        asset_type_dict = gazu.asset.new_asset_type(name)
        return asset_type_dict, True
    else:
        return asset_type_dict, False

@err_catcher(name=__name__)
def createKitsuAsset(project_dict,
                    asset_type_dict,
                    asset_name,
                    asset_description,
                    extra_data={},
                    episode=None):
    """
    returns
        asset dict
        If created new asset
    """
    asset_dict = gazu.asset.get_asset_by_name(project_dict, asset_name)

    if asset_dict is None:
        asset_dict = gazu.asset.new_asset(
            project_dict,
            asset_type_dict,
            asset_name,
            asset_description,
            extra_data,
            episode
        )
        return asset_dict, True
    else:
        return asset_dict, False

@err_catcher(name=__name__)
def uploadThumbnail(entity_id, thumbnail_URL, task_type_dict, user_Email):
    uploadRevision(entity_id,
                thumbnail_URL,
                task_type_dict,
                user_Email,
                True)
    entity_dict = gazu.entity.get_entity(entity_id)
    return entity_dict["preview_file_id"]

@err_catcher(name=__name__)
def uploadRevision(entity_id,
                thumbnail_URL,
                task_type_dict,
                type_status_dict,
                user_Email,
                set_preview,
                comment=""):

    entity_dict = gazu.entity.get_entity(entity_id)
    person_dict = gazu.person.get_person_by_email(user_Email)
    task_dict = gazu.task.get_task_by_name(entity_dict, task_type_dict)
    if task_dict is None:
        task_dict = gazu.task.new_task(entity_dict, task_type_dict)

    if type_status_dict is None:
        type_status_dict = gazu.task.get_task_status(task_dict)

    comment_dict = addComment(task_dict,
                            type_status_dict,
                            comment=comment,
                            person=person_dict)

    preview_dict = gazu.task.add_preview(task_dict,
                                        comment_dict,
                                        thumbnail_URL)

    if set_preview is True:
        gazu.task.set_main_preview(preview_dict)

    return preview_dict

@err_catcher(name=__name__)
def addComment(task, task_status="todo", comment="", person=None):
    if not isinstance(task_status, dict):
        if task_status is None:
            task_status = "todo"
        task_status = gazu.task.get_task_status_by_short_name(task_status)
    if person is not None:
        person = gazu.person.get_person_by_email(person)

    comment_dict = gazu.task.add_comment(task, task_status, comment, person)

    return comment_dict

@err_catcher(name=__name__)
def getTaskTypes(dict=None):
    tasks = None
    if dict is None:
        tasks = gazu.task.all_task_types()
    elif dict["type"] == "Episode":
        tasks = gazu.task.all_task_types_for_episode(dict)
    elif dict["type"] == "Sequence":
        tasks = gazu.task.all_task_types_for_sequence(dict)
    elif dict["type"] == "Scene":
        tasks = gazu.task.all_task_types_for_scene(dict)
    elif dict["type"] == "Shot":
        tasks = gazu.task.all_task_types_for_shot(dict)
    elif dict["type"] == "Asset":
        tasks = gazu.task.all_task_types_for_asset(dict)
    else:
        tasks = gazu.task.all_task_types()

    return tasks


@err_catcher(name=__name__)
def ReportUpdateInfo(self, created, updated, type):
    # Check and report what got added or updated ##
    if len(created) > 0 or len(updated) > 0:
        msgString = ""
        created.sort()
        updated.sort()

        if len(created) > 0:
            msgString += "The following " + type + " were created:\n\n"

            for i in created:
                msgString += str(i) + "\n"

        if len(created) > 0 and len(updated) > 0:
            msgString += "\n\n"

        if len(updated) > 0:
            msgString += "The following " + type + " were updated:\n\n"

            for i in updated:
                msgString += str(i) + "\n"
    else:
        msgString = "No " + type + " were created or updated."

    QMessageBox.information(self.core.messageParent, "Kitsu Sync", msgString)

@err_catcher(name=__name__)
def DownloadDescription(self, name, description, configName):
    local_description = self.core.getConfig(
        name,
        "description",
        config=configName
    )

    if description != local_description:
        if local_description is None:  # Description got created
            return description, True, False
        else:  # Description got edited
            return description, False, True

    return False, False, False

@err_catcher(name=__name__)
def saveID(self, name, id, info_location):
    oldID = getID(self, name, info_location)
    if oldID != id:
        self.core.setConfig(
            cat=name,
            param="objID",
            val=id,
            config=info_location.lower()
        )

@err_catcher(name=__name__)
def removeID(self, name, info_location):
    self.core.setConfig(
        cat=name,
        param="objID",
        delete=True,
        config=info_location.lower()
    )
    self.core.setConfig(
        cat=name,
        param="thumbnailID",
        delete=True,
        config=info_location.lower()
    )

@err_catcher(name=__name__)
def getID(self, name, info_location):
    obj_id = self.core.getConfig(cat=name,
                                 param="objID",
                                 config=info_location.lower())

    return obj_id

@err_catcher(name=__name__)
def saveThumbnailID(self, name, id, info_location):
    oldID = getID(self, name, info_location)
    if oldID != id:
        self.core.setConfig(
            name,
            "thumbnailID",
            id,
            config=info_location.lower()
        )

@err_catcher(name=__name__)
def RemoveCanceled(entities):
    nonCanceled = []
    for entity in entities:
        if not entity["canceled"]:
            nonCanceled.append(entity)
    return nonCanceled


# Get Kitsu shots
@err_catcher(name=__name__)
def GetKitsuShots(self):
    connected = self.connectToKitsu()
    if connected is False:
        return False

    ksuShots = []

    # Check if only should get user assigned objects
    user_sync = self.core.getConfig("kitsu",
                                    "usersync",
                                    configPath=self.core.prismIni)


    # Check if tv show, meaning we're also dealing with episodes
    if self.project_dict["production_type"] == "tvshow":
        episodes = GetEpisodes(self.project_dict, user=user_sync)
        for episode in episodes:
            sequences = GetSequences(
                episode, "from_episode", user=user_sync)

            for sequence in sequences:
                shots = GetShots(sequence, "from_sequence", user=user_sync)

                for shot in shots:
                    shot["episode_name"] = episode["name"]
                    ksuShots.append(shot)

    else:  # meaning feature or short film
        sequences = GetSequences(
            self.project_dict, "from_project", user=user_sync)

        for sequence in sequences:
            shots = GetShots(sequence, "from_sequence", user=user_sync)

            for shot in shots:
                ksuShots.append(shot)

    if len(ksuShots) == 0:
        return False

    ksuShots = RemoveCanceled(ksuShots)

    return ksuShots


# Get Kitsu shots
@err_catcher(name=__name__)
def GetKitsuAssets(self):
    connected = self.connectToKitsu()
    if connected is False:
        return False

    assetTypes = GetAssetTypes()
    ksuAssets = []

    # Check if only should get user assigned objects
    user_sync = self.core.getConfig("kitsu",
                                    "usersync",
                                    configPath=self.core.prismIni)
    for assetType in assetTypes:
        assets = GetAssets(self.project_dict, assetType, user=user_sync)
        for asset in assets:
            ksuAssets.append(asset)
    if len(ksuAssets) == 0:
        return False
    ksuAssets = RemoveCanceled(ksuAssets)

    return ksuAssets

@err_catcher(name=__name__)
def getPublishTypeDict(self, pType, doStatus=False):
    """
    Get task types
    Get task statses
    """
    taskTypes_dict = getTaskTypes()

    taskTypes = []
    for taskType in taskTypes_dict:
        if taskType["for_shots"] == (pType == "Shot"):
            taskTypes.append(taskType)

    taskStatuses = gazu.task.all_task_statuses()

    tp = TaskPicker.TaskPicker(core=self.core,
                               doStatus=doStatus,
                               taskTypes_dicts=taskTypes,
                               taskStatuses_dicts=taskStatuses)
    tp.exec_()

    if tp.picked_data is None:
        QMessageBox.warning(
            self.core.messageParent,
            "Kitsu Publish",
            "Publishing canceled"
        )

    return tp.picked_data

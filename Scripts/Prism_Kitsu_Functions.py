# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2020 Richard Frangenberg
#
# Licensed under GNU GPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.

####################################################
#
# KITSUPLUGIN
#
# Nguyen Phi Hung
#
# contact: nguyenphihung.tech@outlook.com
#
####################################################

from genericpath import isfile
import os
from posixpath import split
import sys
import tempfile
import shutil
import ruamel.yaml as yaml

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

if sys.version[0] == "3":
    pVersion = 3
else:
    pVersion = 2

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Kitsu Plugin")

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

modulePath = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "external_modules")
if not modulePath in sys.path:
    sys.path.append(modulePath)

import add_external_folders
import gazu
# import box
from Prism_Kitsu_Utils_Functions import *
from Prism_Kitsu_App_Functions import *
import TaskPicker


IMAGETYPE = ["jpg", "png", "bmp", "exr"]
MOVIETYPE = ["mov", "mp4", "mkv", "avi"]

STEP2TASKTRANSLATE = {
    "anm": "Animation",
    "lay": "Layout",
    "cmp": "Compositing",
    "lgt": "Lighting",
    "fx": "FX",
    "prv": "Previz"
}


def is_image_type(filetype):
    return any(filetype.endswith(f) for f in IMAGETYPE)

def is_movie_type(filetype):
    return any(filetype.endswith(f) for f in MOVIETYPE)

class Prism_Kitsu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.callbacks = []
        project_tokens = None
        self.tokens = None
        self.publish_type_dict = None
        self.registerCallbacks()

    @err_catcher(name=__name__)
    def isActive(self):
        return True

    @property
    def isPublishOnPlayblast(self):
        return self._isPublishOnPlayblast

    @property
    def publishStatus(self):
        return self._publishStatus

    @err_catcher(name=__name__)
    def setIsPublishOnPlayblast(self, value):
        self._isPublishOnPlayblast = value

    @err_catcher(name=__name__)
    def setPublishStatus(self, value):
        self._publishStatus = value

    @err_catcher(name=__name__)
    def registerCallbacks(self):
        self.callbacks.append(self.core.registerCallback("projectBrowser_getAssetMenu", self.projectBrowser_getAssetMenu))
        self.callbacks.append(self.core.registerCallback("projectBrowser_getShotMenu", self.projectBrowser_getShotMenu))
        self.callbacks.append(self.core.registerCallback("onStateCreated", self.onStateCreated))
        self.callbacks.append(self.core.registerCallback("postPlayblast", self.onPostPlayblast))
        self.callbacks.append(self.core.registerCallback("postRender", self.onPostRender))

    @err_catcher(name=__name__)
    def unregister(self):
        self.unregisterCallbacks()

    @err_catcher(name=__name__)
    def unregisterCallbacks(self):
        for cb in self.callbacks:
            self.core.unregisterCallback(cb["id"])


    @err_catcher(name=__name__)
    def onProjectChanged(self, origin):
        if hasattr(self, "kitsu"):
            del self.kitsu

    @err_catcher(name=__name__)
    def prismSettings_loadUI(self, origin):
        origin.gb_prjmanPrjIntegration = QGroupBox("Kitsu integration")
        origin.w_Kitsu = QWidget()
        lo_prjmanI = QHBoxLayout()
        lo_prjmanI.addWidget(origin.w_Kitsu)
        origin.gb_prjmanPrjIntegration.setLayout(lo_prjmanI)
        origin.gb_prjmanPrjIntegration.setCheckable(True)
        origin.gb_prjmanPrjIntegration.setChecked(False)

        lo_prjman = QGridLayout()
        origin.w_Kitsu.setLayout(lo_prjman)

        origin.l_prjmanSite = QLabel("Kitsu site:")
        origin.l_prjmanPrjName = QLabel("Project Name:")
        origin.l_prjmanUserName = QLabel("Username:       ")
        origin.l_prjmanUserPassword = QLabel("Password:")
        origin.e_prjmanSite = QLineEdit()
        origin.e_prjmanPrjName = QLineEdit()
        origin.e_prjmanUserName = QLineEdit()
        origin.e_prjmanUserPassword = QLineEdit()
        origin.chb_syncUserTasks = QCheckBox("Only sync user assigned tasks")
        origin.chb_syncUserTasks.setChecked(True)

        lo_prjman.addWidget(origin.l_prjmanSite)
        lo_prjman.addWidget(origin.l_prjmanPrjName)
        lo_prjman.addWidget(origin.l_prjmanUserName)
        lo_prjman.addWidget(origin.l_prjmanUserPassword)
        lo_prjman.addWidget(origin.e_prjmanSite, 0, 1)
        lo_prjman.addWidget(origin.e_prjmanPrjName, 1, 1)
        lo_prjman.addWidget(origin.e_prjmanUserName, 2, 1)
        lo_prjman.addWidget(origin.e_prjmanUserPassword, 3, 1)
        lo_prjman.addWidget(origin.chb_syncUserTasks, 4, 1)

        origin.w_prjSettings.layout().insertWidget(5, origin.gb_prjmanPrjIntegration)
        origin.groupboxes.append(origin.gb_prjmanPrjIntegration)
        origin.e_prjmanUserPassword.setEchoMode(QLineEdit.Password)

        origin.gb_prjmanPrjIntegration.toggled.connect(
            lambda x: self.prismSettings_prjmanToggled(origin, x)
        )

    @err_catcher(name=__name__)
    def prismSettings_prjmanToggled(self, origin, checked):
        origin.w_Kitsu.setVisible(checked)

    @err_catcher(name=__name__)
    def prismSettings_loadSettings(self, origin, settings):
        if "kitsu" in settings:
            if "username" in settings["kitsu"]:
                origin.e_prjmanUserName.setText(settings["kitsu"]["username"])

            if "userpassword" in settings["kitsu"]:
                origin.e_prjmanUserPassword.setText(settings["kitsu"]["userpassword"])

    @err_catcher(name=__name__)
    def prismSettings_loadPrjSettings(self, origin, settings):
        if "kitsu" in settings:
            if "active" in settings["kitsu"]:
                origin.gb_prjmanPrjIntegration.setChecked(settings["kitsu"]["active"])

            if "site" in settings["kitsu"]:
                origin.e_prjmanSite.setText(settings["kitsu"]["site"])

            if "projectname" in settings["kitsu"]:
                origin.e_prjmanPrjName.setText(settings["kitsu"]["projectname"])

            if "usersync" in settings["kitsu"]:
                origin.chb_syncUserTasks.setChecked(
                    settings["kitsu"]["usersync"])

        self.prismSettings_prjmanToggled(origin, origin.gb_prjmanPrjIntegration.isChecked())

    @err_catcher(name=__name__)
    def prismSettings_saveSettings(self, origin, settings):
        if "kitsu" not in settings:
            settings["kitsu"] = {}

        settings["kitsu"]["username"] = origin.e_prjmanUserName.text()
        settings["kitsu"]["userpassword"] = origin.e_prjmanUserPassword.text()

    @err_catcher(name=__name__)
    def prismSettings_savePrjSettings(self, origin, settings):
        if "kitsu" not in settings:
            settings["kitsu"] = {}

        settings["kitsu"]["active"] = origin.gb_prjmanPrjIntegration.isChecked()
        settings["kitsu"]["site"] = origin.e_prjmanSite.text()
        settings["kitsu"]["projectname"] = origin.e_prjmanPrjName.text()
        settings["kitsu"]["usersync"] = origin.chb_syncUserTasks.isChecked()


    @err_catcher(name=__name__)
    def pbBrowser_getMenu(self, origin):
        prjman = self.core.getConfig(
            "kitsu", "active", configPath=self.core.prismIni
        )
        if prjman:
            prjmanMenu = QMenu("kitsu", origin)

            actprjman = QAction("Open Kitsu", origin)
            actprjman.triggered.connect(self.openprjman)
            prjmanMenu.addAction(actprjman)

            prjmanMenu.addSeparator()

            actA2Local = QAction("Kitsu assets to local", origin)
            actA2Local.triggered.connect(lambda: self.prjmanAssetsToLocal(origin))
            prjmanMenu.addAction(actA2Local)

            actLocal2projman = QAction("Local assets to Kitsu", origin)
            actLocal2projman.triggered.connect(lambda: self.prjmanAssetsToprjman(origin))
            prjmanMenu.addAction(actLocal2projman)

            prjmanMenu.addSeparator()

            actprojmanS2Local = QAction("Kitsu shots to local", origin)
            actprojmanS2Local.triggered.connect(lambda: self.prjmanShotsToLocal(origin))
            prjmanMenu.addAction(actprojmanS2Local)

            actLocalS2projman = QAction("Local shots to Kitsu", origin)
            actLocalS2projman.triggered.connect(lambda: self.prjmanShotsToprjman(origin))
            prjmanMenu.addAction(actLocalS2projman)

            return prjmanMenu

    @err_catcher(name=__name__)
    def projectBrowser_getAssetMenu(self, origin, assetname, assetPath, entityType):
        if entityType != "asset":
            return

        kitsu = self.core.getConfig("kitsu", "active", configPath=self.core.prismIni)
        if kitsu:
            kitsuAction = QAction("Open in Kitsu", origin)
            kitsuAction.triggered.connect(
                lambda: self.openprjman(assetname, eType="Asset", assetPath=assetPath)
            )
            return kitsuAction

    @err_catcher(name=__name__)
    def projectBrowser_getShotMenu(self, origin, shotname):
        kitsu = self.core.getConfig("kitsu", "active", configPath=self.core.prismIni)
        if kitsu:
            kitsuAction = QAction("Open in Kitsu", origin)
            kitsuAction.triggered.connect(lambda: self.openprjman(shotname))
            return kitsuAction


    @err_catcher(name=__name__)
    def pbBrowser_getPublishMenu(self, origin):
        prjman = self.core.getConfig(
            "kitsu", "active", configPath=self.core.prismIni
        )
        if (
            prjman
            and origin.mediaPlaybacks["shots"]["seq"]
        ):
            prjmanAct = QAction("Publish to Kitsu", origin)
            prjmanAct.triggered.connect(lambda: self.prjmanPublish(origin))
            return prjmanAct

    @err_catcher(name=__name__)
    def createAsset_open(self, origin):
        prjman = self.core.getConfig(
            "kitsu", "active", configPath=self.core.prismIni
        )
        if not prjman:
            return

        lt, pt = self.connectToKitsu()
        if all([lt,pt]):
            origin.chb_createInKitsu = QGroupBox("Create asset in Kitsu")
            origin.chb_createInKitsu.setCheckable(True)
            origin.chb_createInKitsu.setLayout(QVBoxLayout())

            origin.lb_KitsuAssetTypes = QLabel("Asset Type:")
            origin.lb_KitsuAssetDescription = QLabel("Description:")
            origin.cb_KitsuAssetTypes = QComboBox()
            asset_types = gazu.asset.all_asset_types()
            origin.cb_KitsuAssetTypes.addItems([t.get("name") for t in asset_types])
            origin.tb_assetDescription = QTextEdit()
            
            origin.chb_createInKitsu.layout().addWidget(origin.lb_KitsuAssetTypes)
            origin.chb_createInKitsu.layout().addWidget(origin.cb_KitsuAssetTypes)
            origin.chb_createInKitsu.layout().addWidget(origin.lb_KitsuAssetDescription)
            origin.chb_createInKitsu.layout().addWidget(origin.tb_assetDescription)

            origin.w_options.layout().insertWidget(0, origin.chb_createInKitsu)
            origin.chb_createInKitsu.setChecked(True)


    @err_catcher(name=__name__)
    def createAsset_typeChanged(self, origin, state):
        if hasattr(origin, "chb_createInKitsu"):
            origin.chb_createInKitsu.setEnabled(state)

    @err_catcher(name=__name__)
    def assetCreated(self, origin, itemDlg, assetPath):
        if (
            hasattr(itemDlg, "chb_createInKitsu")
            and itemDlg.chb_createInKitsu.isChecked()
        ) and (
            hasattr(itemDlg, "cb_KitsuAssetTypes")
        ) and (
            hasattr(itemDlg, "tb_assetDescription")
        ):
            self.createprjmanAssets([(
                assetPath,
                itemDlg.cb_KitsuAssetTypes.currentText(),
                itemDlg.tb_assetDescription.toPlainText())])

    @err_catcher(name=__name__)
    def editShot_open(self, origin, shotName):
        shotName, seqName = self.core.entities.splitShotname(shotName)
        if not shotName:
            prjman = self.core.getConfig(
                "kitsu", "active", configPath=self.core.prismIni
            )
            if not prjman:
                return

            origin.chb_createInKitsu = QCheckBox("Create shot in Kitsu")
            origin.widget.layout().insertWidget(0, origin.chb_createInKitsu)
            origin.chb_createInKitsu.setChecked(True)

    @err_catcher(name=__name__)
    def editShot_closed(self, origin, shotName):
        if (
            hasattr(origin, "chb_createInKitsu")
            and origin.chb_createInKitsu.isChecked()
        ):
            self.createprjmanShots([shotName])

    @err_catcher(name=__name__)
    def connectToKitsu(self, user=True, raise_login_error=True):
        try:
            prjmanSite = self.core.getConfig("kitsu", "site", configPath=self.core.prismIni)
            prjmanUser = self.core.getConfig("kitsu", "username")
            prjmanUserPassword = self.core.getConfig("kitsu", "userpassword")
            prjmanName = self.core.getConfig("kitsu", "projectname", configPath=self.core.prismIni)
            api_host= prjmanSite+"/api"
            gazu.set_host(api_host)
            from qtazulite import utils
            try:
                login_tokens = gazu.log_in(prjmanUser, prjmanUserPassword)
            except:
                from qtazulite.widgets.login import Login
                login_window = Login(host = api_host, user=prjmanUser, password=prjmanUserPassword)
                login_window.logged_in.connect(self.prismSettings_saveLoginSettings)
                login_window.exec_()
                login_tokens = login_window.login_tokens
            project_tokens = gazu.project.get_project_by_name(prjmanName)

            return login_tokens, project_tokens
        except:
            if raise_login_error:
                raise
            return None, None

    @err_catcher(name=__name__)
    def prismSettings_saveLoginSettings(self, user, password):
        self.core.setConfig("kitsu", "username", val=user)
        self.core.setConfig("kitsu", "userpassword", val=password)


    @err_catcher(name=__name__)
    def createprjmanAssets(self, assets=[]):
        from pathlib import Path
        login_tokens, project_dict = self.connectToKitsu()
        new_assets = []
        for asset, asset_type, asset_description in assets:
            if gazu.asset.get_asset_by_name(project_dict, asset):
                continue
            asset_type_dict = gazu.asset.get_asset_type_by_name(asset_type)
            asset_path = Path(asset)
            if asset_path.parent.name.lower() != asset_type.lower():
                asset_type_root = Path(self.core.assetPath) / asset_type
                asset_type_root.mkdir(parents=True, exist_ok=True)
                asset_path = asset_path.rename(asset_type_root / asset_path.name)

            new_assets.append(gazu.asset.new_asset(
                project_dict, 
                asset_type_dict, 
                self.core.entities.getAssetNameFromPath(asset),
                asset_description
            ))
        return new_assets


    @err_catcher(name=__name__)
    def createprjmanShots(self, shots=[]):
        login_tokens, project_tokens = self.connectToKitsu()
        new_shots=[]
        for shot in shots:
            shotName, seqName = self.core.entities.splitShotname(shot)
            sequence = gazu.shot.get_sequence_by_name(project_tokens, seqName)
            if not sequence:
                sequence = gazu.shot.new_sequence(project_tokens, seqName) 
            if gazu.shot.get_shot_by_name(sequence, shotName):
                continue
            shotRange = self.core.getConfig("shotRanges", shot, config="shotinfo")
            new_shots.append(
                gazu.shot.new_shot(
                project_tokens, 
                sequence, 
                shotName, 
                frame_in=shotRange[0], 
                frame_out=shotRange[1], 
                data={"metadata": self.core.getConfig("metadata", shot, config="shotinfo")}
                ))
        return new_shots
            

    @err_catcher(name=__name__)
    def prjmanPublish(self, origin):
        try:
            del sys.modules["KitsuPublish"]
        except:
            pass

        import KitsuPublish

        if origin.tbw_browser.currentWidget().property("tabType") == "Assets":
            pType = "Asset"
        else:
            pType = "Shot"

        shotName = os.path.basename(origin.renderBasePath)

        taskName = (
            origin.curRTask.replace(" (playblast)", "")
            .replace(" (2d)", "")
            .replace(" (external)", "")
        )
        versionName = origin.curRVersion.replace(" (local)", "")
        mpb = origin.mediaPlaybacks["shots"]

        imgPaths = []
        if mpb["prvIsSequence"] or len(mpb["seq"]) == 1:
            if os.path.splitext(mpb["seq"][0])[1] in [".mp4", ".mov"]:
                imgPaths.append(
                    [os.path.join(mpb["basePath"], mpb["seq"][0]), mpb["curImg"]]
                )
            else:
                imgPaths.append(
                    [os.path.join(mpb["basePath"], mpb["seq"][mpb["curImg"]]), 0]
                )
        else:
            for i in mpb["seq"]:
                imgPaths.append([os.path.join(mpb["basePath"], i), 0])

        if "pstart" in mpb:
            sf = mpb["pstart"]
        else:
            sf = 0
        # do publish here
        kitsup = KitsuPublish.Publish(
            core=self.core,
            origin=self,
            ptype=pType,
            shotName=shotName,
            task=taskName,
            preview=mpb,
            version=versionName,
            sources=imgPaths,
            startFrame=sf,
        )
        kitsup.exec_()

    def openprjman(self, shotName=None, eType="Shot", assetPath=""):
        login_tokens, project_tokens = self.connectToKitsu()
        if shotName:
            if eType == "Shot":
                shotName, seqName = self.core.entities.splitShotname(shotName)
                sequence = gazu.shot.get_sequence_by_name(project_tokens, seqName)
                shot = gazu.shot.get_shot_by_name(sequence, shotName)
                base_url = gazu.shot.get_shot_url(shot)
            else:
                asset = gazu.asset.get_asset_by_name(project_tokens, shotName)
                base_url = gazu.asset.get_asset_url(asset)
        else:
            base_url = gazu.project.get_project_url(project_tokens)
        launch_url = base_url.replace("http://", "http://" + login_tokens.get("access_token") + "@")
        import subprocess
        if os.path.exists("C:/Temp/Chromium/chrome.exe"):
            subprocess.Popen("C:/Temp/Chromium/chrome.exe {}".format(launch_url))
        else:
            # pass
            import webbrowser
            try:
                webbrowser.get("chromium").open(launch_url)
            except:
                webbrowser.open(launch_url)

    @err_catcher(name=__name__)
    def prjmanAssetsToLocal(self, origin):
        # add code here

        createdAssets = []
        login_tokens, project_tokens = self.connectToKitsu()
        if not all([project_tokens,login_tokens]):
            msgString = "Project is not valid"
            QMessageBox.information(self.core.messageParent, "Kitsu Sync Assets", msgString)
            return
        from pathlib import Path
        assets = gazu.asset.all_assets_for_project(project_tokens)
        for asset in assets:
            assetInfo = {}
            asset_name = asset.get("name")
            # Process thumbnail
            tmbID, created, updated = self.downloadThumbnail(
                                                        asset_name,
                                                        asset.get("preview_file_id"),
                                                        "Assetinfo")
            if tmbID == "":
                removeID(self, asset["name"], "assetinfo")
            elif tmbID is not False:
                assetInfo["thumbnailID"] = tmbID
            asset_type = gazu.asset.get_asset_type(asset.get("entity_type_id")).get("name")
            asset_path = Path(self.core.assetPath) / asset_type / asset_name
            if not asset_path.exists():
                self.core.entities.createEntity("asset", str(asset_path))
                createdAssets.append(asset_name)


        if len(createdAssets) > 0:
            msgString = "The following assets were created:\n\n"

            createdAssets.sort()

            for i in createdAssets:
                msgString += i + "\n"
        else:
            msgString = "No assets were created."

        QMessageBox.information(self.core.messageParent, "Kitsu Sync", msgString)

        origin.refreshAHierarchy()

    @err_catcher(name=__name__)
    def prjmanAssetsToprjman(self, origin):
        # add code here
        assets_path = self.core.entities.getAssetPaths()
        assets_path = [
            a for a in assets_path if os.path.basename(a) not in self.core.entities.omittedEntities["asset"]
        ]
        createdAssets = []
        updatedAssets = []


        from box import Box
        from pathlib import Path
        login, project = self.connectToKitsu()
        for asset_path in assets_path:
            asset_path = Path(asset_path)
            asset_name = asset_path.name
            asset = gazu.asset.get_asset_by_name(project, asset_name)
            if asset:
                asset = Box(asset)
                if not asset.data:
                    asset.data = Box()
                asset.data.prism = Box()
                asset.data.prism.path = str(asset_path)
                info = self.core.getConfig(config="assetinfo", location=str(asset_path))
                print(info)
                asset.data.prism.assetInfo = self.core.getConfig(configPath=info)
                gazu.asset.update_asset(asset)
                updatedAssets.append(asset_name)
            else:
                if asset_path.parent == self.core.assetPath:
                    continue
                rel_path = asset_path.relative_to(self.core.assetPath)
                asset_type_name = list(rel_path.parents)[::-1][1]
                asset_type = gazu.asset.get_asset_type_by_name(asset_type_name)
                if not asset_type:
                    asset_type = gazu.asset.new_asset_type(asset_type_name)
                info = self.core.getConfig(config="assetinfo", location=str(asset_path))
                prism_info = dict(prism=dict(
                    path = str(asset_path),
                    assetinfo = info
                ))
                gazu.asset.new_asset(
                    project,
                    asset_type,
                    asset_name,
                    extra_data=prism_info
                )
                createdAssets.append(asset_name)

        if len(createdAssets) > 0 or len(updatedAssets) > 0:
            msgString = ""


            createdAssets.sort()
            updatedAssets.sort()

            if len(createdAssets) > 0:
                msgString += "The following assets were created:\n\n"

                for i in createdAssets:
                    msgString += i + "\n"

            if len(createdAssets) > 0 and len(updatedAssets) > 0:
                msgString += "\n\n"

            if len(updatedAssets) > 0:
                msgString += "The following assets were updated:\n\n"

                for i in updatedAssets:
                    msgString += i + "\n"
        else:
            msgString = "No assets were created or updated."

        QMessageBox.information(self.core.messageParent, "Kitsu Sync", msgString)

    @err_catcher(name=__name__)
    def prjmanShotsToLocal(self, origin):
        login_tokens, project_tokens = self.connectToKitsu()
        ksuShots = self.getKitsuShots()

        if not ksuShots:
            QMessageBox.warning(
                self.core.messageParent,
                "Kitsu Sync",
                "No shots on Kitsu were found",
            )
            return

        createdShots = []
        updatedShots = []
        configInfo = {}
        # Process all shots ##
        for shotData in ksuShots:
            shotInfo = {}
            
            # Create shot folders ##
            shotName = shotData["sequence_name"] + "-" + shotData["name"]

            # Add episode name if exists
            if "episode_name" in shotData:
                shotName = shotData["episode_name"] + "." + shotName

            # Create folder if it doesn't exist
            if not os.path.exists(os.path.join(origin.sBasePath, shotName)):
                self.core.entities.createEntity("shot", shotName)

                createdShots.append(shotName)

                shotInfo["objID"] = shotData["id"]

            # As Kitsu allows you to write only one of the start frame and
            # end frame we need to check them induvidually
            frame_nudge = int(self.core.getConfig("kitsu",
                                                  "setFirstFrameOne",
                                                  configPath=self.core.prismIni) is True)
            nb_frames = None
            if shotData["nb_frames"] is not None:
                nb_frames = int(shotData["nb_frames"])
            frame_in = None
            frame_out = None
            if shotData["data"] is not None:
                if "frame_in" in shotData["data"]:
                    try:
                        frame_in = int(shotData["data"]["frame_in"])
                    except ValueError:
                        frame_in = None
                if "frame_out" in shotData["data"]:
                    try:
                        frame_out = int(shotData["data"]["frame_out"])
                    except ValueError:
                        frame_out = None

            if frame_in is not None:
                if frame_out is None:
                    frame_out = frame_in + nb_frames
            elif nb_frames is not None:
                frame_in = frame_nudge
                frame_out = nb_frames - 1 + frame_nudge

            if frame_in is not None and frame_out is not None:
                shotRange = self.core.getConfig("shotRanges",
                                                shotName,
                                                config="shotinfo")

                prv_frame_in = None
                prv_frame_out = None

                if (isinstance(shotRange, (list, yaml.comments.CommentedSeq))
                        and len(shotRange) == 2):
                    prv_frame_in = int(shotRange[0])
                    prv_frame_out = int(shotRange[1])

                if (frame_in != prv_frame_in or frame_out != prv_frame_out):
                    # Update to be connected to shot-name instead of shotRange
                    self.core.setConfig(
                        "shotRanges",
                        shotName,
                        [frame_in, frame_out],
                        config="shotinfo"
                    )

                if (
                    shotName not in createdShots
                    and shotName not in updatedShots
                    and (frame_in != prv_frame_in
                         or frame_out != prv_frame_out)
                ):
                    updatedShots.append(shotName)

            # Process thumbnail ##
            tmbID, created, updated = self.downloadThumbnail(
                                                        shotName,
                                                        shotData["preview_file_id"],
                                                        "Shotinfo")
            if tmbID == "":
                removeID(self, shotName, "assetinfo")
            elif tmbID is not None:
                shotInfo["thumbnailID"] = tmbID

            if (
                shotName not in createdShots
                and shotName not in updatedShots
            ):
                if created:
                    createdShots.append(shotName)
                elif updated:
                    updatedShots.append(shotName)

            # Add info to config array
            configInfo[shotName] = shotInfo

        if len(configInfo) > 0:
            # Write information
            self.core.setConfig(data=configInfo, config="shotinfo")

        # Report what shots got added or updated
        ReportUpdateInfo(self, createdShots, updatedShots, "shots")

        # Check if we should do reverse sync
        ignore_post_checks = self.core.getConfig("kitsu",
                                                 "ignorepostchecks",
                                                 configPath=self.core.prismIni)

        if ignore_post_checks is False:

            # Check for shots that does not exist on Kitsu ##
            for i in os.walk(origin.sBasePath):
                foldercont = i
                break

            shotnames = []
            for shot_name in foldercont[1]:
                if (not shot_name.startswith(
                        "_") and shot_name not in self.core.entities.omittedEntities["shot"]):
                    shotnames.append(shot_name)

            localShots = []
            for localName in shotnames:
                localID = getID(self, localName, "shotinfo")
                if localID is None:
                    localShots.append(localName)

            if len(localShots) > 0:
                msg = QMessageBox(
                    QMessageBox.Question,
                    "Kitsu Sync",
                    "Some local shots don't exist on Kitsu:\n"
                    + "\n".join(localShots),
                    parent=self.core.messageParent,
                )
                msg.addButton("Hide local shots", QMessageBox.YesRole)
                msg.addButton("Add shots to Kitsu", QMessageBox.YesRole)
                msg.addButton("Do nothing", QMessageBox.YesRole)
                msg.addButton("Don't ask again", QMessageBox.YesRole)
                action = msg.exec_()

                if action == 0:
                    noAccess = []
                    for i in localShots:
                        dstname = os.path.join(origin.sBasePath, "_" + i)
                        if not os.path.exists(dstname):
                            try:
                                os.rename(
                                    os.path.join(
                                        origin.sBasePath,
                                        i
                                    ),
                                    dstname
                                )
                            except Exception:
                                noAccess.append(i)

                    if len(noAccess) > 0:
                        msgString = "Acces denied for:\n\n"

                        for i in noAccess:
                            msgString += i + "\n"

                        QMessageBox.warning(
                            self.core.messageParent, "Hide Shots", msgString
                        )
                elif action == 1:
                    created_shots, updated_shots = self.createShots(localShots)
                    # Report what shots got added or updated
                    ReportUpdateInfo(self, created_shots,
                                     updated_shots, "shots")
                elif action == 3:
                    QMessageBox.information(
                        self.core.messageParent,
                        "Kitsu",
                        "You can undo this by unchecking \"Ignore post checks\" in the settings.",
                    )
                    self.core.setConfig("kitsu",
                                        "ignorepostchecks",
                                        True,
                                        configPath=self.core.prismIni)

        origin.refreshShots()

    @err_catcher(name=__name__)
    def prjmanShotsToprjman(self, origin):
        login_tokens, project_tokens = self.connectToKitsu()
        # add code here
        for i in os.walk(origin.sBasePath):
            foldercont = i
            break
        self.core.entities.refreshOmittedEntities()

        shot_names = []
        for shot_name in foldercont[1]:
            if (not shot_name.startswith(
                    "_") and shot_name not in self.core.entities.omittedEntities["shot"]):
                shot_names.append(shot_name)

        created_shots, updated_shots = self.createShots(shot_names)

        # Report what shots got added or updated
        ReportUpdateInfo(self, created_shots, updated_shots, "shots")

        # Check if we should do reverse sync
        ignore_post_checks = self.core.getConfig("kitsu",
                                                 "ignorepostchecks",
                                                 configPath=self.core.prismIni)

        if ignore_post_checks is False:

            # Time to check if Kitsu has some shots we don't have
            # Get kitsu shots
            ksuShots = self.getKitsuShots()

            if ksuShots is not False:
                externalShots = []
                # Process all shots ##
                for shotData in ksuShots:
                    # Create shot folders ##
                    shotName = shotData["sequence_name"] + \
                        "-" + shotData["name"]

                    localID = getID(self, shotName, "Shotinfo")
                    if localID is None:
                        externalShots.append(shotName)

                if len(externalShots) > 0:
                    msg = QMessageBox(
                        QMessageBox.Question,
                        "Kitsu Sync",
                        "Some Kitsu shots don't exist locally:\n"
                        + "\n".join(externalShots),
                        parent=self.core.messageParent,
                    )
                    msg.addButton("Sync Kitsu shots", QMessageBox.YesRole)
                    msg.addButton("Do nothing", QMessageBox.YesRole)
                    action = msg.exec_()

                    if action == 0:
                        self.ksuShotsToLocal(origin)

    @err_catcher(name=__name__)
    def onProjectBrowserClose(self, origin):
        pass

    @err_catcher(name=__name__)
    def onSetProjectStartup(self, origin):
        pass

    @err_catcher(name=__name__)
    def updateStatus(self):
        self.cb_status.clear()
        for status in gazu.task.all_task_statuses():
            self.cb_status.addItem(status['name'], status)

    @err_catcher(name=__name__)
    def onStateCreated(self, origin, state, stateData):
        self.connectToKitsu(raise_login_error=False)
        if hasattr(state, "gb_playblast"):
            wid = QGroupBox("Kitsu")
            layout = QVBoxLayout()
            wid.setLayout(layout)
            state.chb_publishToKitsu = QCheckBox("Publish To Kitsu")
            state.le_customKitsuPublishComment = QLineEdit()
            state.le_customKitsuPublishComment.setPlaceholderText("Input Custom comment here ...")
            state.chb_setPublishAsReview = QCheckBox("Set As Preview Thumbnail")
            state.chb_setPublishIndividualShots = QCheckBox("Publish Individual Shots")
            state.chb_setCreateShot = QCheckBox("Create Shot If Missing")
            state.chb_publishToKitsu.setChecked(True)
            state.chb_publishToKitsu.toggled.connect(self.setIsPublishOnPlayblast)
            if hasattr(state, "chb_useCameraSequencer"):
                state.chb_useCameraSequencer.setChecked(False)
                state.chb_setPublishIndividualShots.toggled.connect(state.chb_useCameraSequencer.setChecked)
            if hasattr(state, "chb_playblastEachShot"):
                state.chb_playblastEachShot.setChecked(False)
                state.chb_setPublishIndividualShots.toggled.connect(state.chb_playblastEachShot.setChecked)
            w_publishStatus = QWidget()
            w_publishStatus.setLayout(QHBoxLayout())
            w_publishStatus.layout().addWidget(QLabel("Publish Status: "))
            state.chb_taskStatus = QComboBox()
            for status in gazu.task.all_task_statuses():
                state.chb_taskStatus.addItem(status['name'], status)
            state.chb_taskStatus.currentTextChanged.connect(self.setPublishStatus)
            w_publishStatus.layout().addWidget(state.chb_taskStatus)
            layout.addWidget(state.chb_publishToKitsu)
            layout.addWidget(state.chb_setPublishAsReview)
            layout.addWidget(state.chb_setPublishIndividualShots)
            layout.addWidget(state.chb_setCreateShot)
            layout.addWidget(w_publishStatus)
            layout.addWidget(state.le_customKitsuPublishComment)
            # layout.setContentsMargins(10,10,10,10)
            state.gb_playblast.layout().insertWidget(0, wid)


    @err_catcher(name=__name__)
    def onPostPlayblast(self, state, scenefile, startframe, endframe, outputpath):
        if not state.chb_publishToKitsu.isChecked():
            return
        login_tokens, project_tokens = self.connectToKitsu(raise_login_error=False)
        if not (login_tokens and project_tokens):
            return
        scenefile = self.core.convertPath(scenefile, "global")
        data = self.core.entities.getScenefileData(scenefile)
        task_name = state.l_taskName.text()
        scenePath = scenefile
        entityName = data.get("entityName")
        entitytype = data.get("entity")
        version = data.get("version")
        step = STEP2TASKTRANSLATE.get( data.get("step")) or data.get("step")
        # status = gazu.task.get_task_status_by_name(state.chb_taskStatus.currentText())
        
        comment = state.le_customKitsuPublishComment.text() or data.get("comment").replace("-", " ")
        outputpath = outputpath.replace("..", ".")
        ouputname, ext = os.path.splitext(outputpath)
        filetype = ext.replace(".","")
        prism_username = self.core.getConfig("globals", "username")

        if is_image_type(filetype):
            outputpath = self.convertSeqToVideo(self.core.projectBrowser(), os.getenv("TMP"))
            ouputname, ext = os.path.splitext(outputpath)
            filetype = ext.replace(".","")
        
        publish_entities = []

        if entitytype == "shot":
            shotname, seqname = self.core.entities.splitShotname(entityName)
            if not shotname or not seqname or seqname == "no sequence":
                QMessageBox.critical(
                    self.core.messageParent,
                    "Kitsu Publish",
                    "shot or seq is none for entity {}".format(entityName),
                )
                return

            if project_tokens["production_type"] == "tvshow":
                try:
                    epName, seqname = seqname.split(".", 1)
                except:
                    epName = "Main Pack"
            else:
                epName = None

            if epName:
                ep = gazu.shot.get_episode_by_name(project_tokens, epName)
                if ep:
                    seq = gazu.shot.get_sequence_by_name(project_tokens, seqname, ep)
                else:
                    QMessageBox.critical(
                        self.core.messageParent,
                        "Kitsu Publish",
                        "No Episode name {} on Kitsu were found. Skipped publish to kitsu.".format(epName),
                    )
            else:
                seq = gazu.shot.get_sequence_by_name(project_tokens, seqname)

            if not seq:
                QMessageBox.critical(
                    self.core.messageParent,
                    "Kitsu Publish",
                    "No sequence name {} on Kitsu were found. Skipped publish to kitsu.".format(seqname),
                )
                return
            entity_dict = gazu.shot.get_shot_by_name(seq, shotname)
            if not entity_dict:
                QMessageBox.critical(
                    self.core.messageParent,
                    "Kitsu Publish",
                    "No shot name {} on Kitsu were found. Skipped publish to kitsu.".format(shotname),
                )
                return
            shots_path = os.path.join( os.path.dirname(self.core.convertPath(outputpath, "global")), "shots")
            logger.info("Check for shots in {}".format(shots_path))
            if state.chb_setPublishIndividualShots.isChecked() and os.path.exists(shots_path):
                files = (d for d in os.listdir(shots_path) if os.path.isfile(os.path.join(shots_path, d)))
                for shot_file in files:
                    try:
                        shotfilename =os.path.splitext(shot_file)[0]
                        try:
                            shotname, ranges = shotfilename.split("_", 1)
                        except ValueError:
                            shotname = shotfilename
                        try:
                            start_shotframe, end_shotframe = ranges.split("-",1)
                            start_shotframe = int(start_shotframe)
                            end_shotframe = int(end_shotframe)
                        except ValueError:
                            start_shotframe, end_shotframe = (0, 100)
                        if state.chb_setCreateShot.isChecked():
                            try:
                                shot_dict, isCreated, isUpdated = createKitsuShot(project_tokens, seq, shotname.capitalize(), (start_shotframe, end_shotframe))
                            except:
                                shot_dict = None
                        else:
                            shot_dict = gazu.shot.get_shot_by_name(seq, shotname)
                        if shot_dict:
                            publish_entities.append((shot_dict, os.path.join(shots_path, shot_file)))
                        else:
                            logger.error("Failed to find shot with name {}".format(shotname))
                    except Exception as why:
                        logger.error("Error when publish shot with name {}: \n{}".format(shotname, why))
        else:
            entity_dict = gazu.asset.get_asset_by_name(project_tokens, entityName)
            if not entity_dict:
                QMessageBox.critical(
                    self.core.messageParent,
                    "Kitsu Publish",
                    "No asset name {} on Kitsu were found. Skipped publish to kitsu.".format(entityName),
                )
                return
        publish_entities.append((entity_dict, outputpath))
        
        for entity_dict, outputpath in publish_entities:
            if is_movie_type(filetype) and entity_dict:
                try:
                    task_type_dict = gazu.task.get_task_type_by_name(step)
                    person_dict = gazu.client.get_current_user()
                    task_dict = gazu.task.get_task_by_name(entity_dict, task_type_dict)
                    if task_dict is None:
                        task_dict = gazu.task.new_task(entity_dict, task_type_dict)

                    type_status_dict = state.chb_taskStatus.currentData()

                    comment_dict = addComment(
                        task_dict,
                        type_status_dict,
                        comment=comment,
                        person=person_dict)

                    preview_dict = gazu.task.add_preview(task_dict,
                                                        comment_dict,
                                                        outputpath)

                    if state.chb_setPublishAsReview.isChecked():
                        gazu.task.set_main_preview(preview_dict)
                except Exception as why:
                    logger.error("Failed to submit playblast to kitsu for {}".format(entity_dict.get("name") or entity_dict))
                else:
                    logger.info("Playblast submited to kitsu for {}".format(entity_dict.get("name") or entity_dict))

            if not entity_dict.get("data"):
                entity_dict["data"] = {}

            if "metadata" not in entity_dict["data"]:
                entity_dict["data"]["metadata"] = {}

            #add RV metadata to shot
            if "RVMedia" not in entity_dict["data"]["metadata"]:
                entity_dict["data"]["metadata"]["RVMedia"] = {}
            if step not in entity_dict["data"]["metadata"]["RVMedia"]:
                entity_dict["data"]["metadata"]["RVMedia"][step] = []
            if not isinstance(entity_dict["data"]["metadata"]["RVMedia"][step], list):
                entity_dict["data"]["metadata"]["RVMedia"][step] = []
            for version in entity_dict["data"]["metadata"]["RVMedia"][step]:
                for k, v in version.items():
                    if k == "last":
                        entity_dict["data"]["metadata"]["RVMedia"][step].append(
                            {str(len(entity_dict["data"]["metadata"]["RVMedia"][step])-1): v}
                        )
                        entity_dict["data"]["metadata"]["RVMedia"][step].remove(version)
            entity_dict["data"]["metadata"]["RVMedia"][step].append( 
                {"last": os.path.normpath(outputpath)})

			#add prism metadata
            if "prism" not in entity_dict["data"]["metadata"]:
                entity_dict["data"]["metadata"]["prism"] = {}
            if step not in entity_dict["data"]["metadata"]["prism"]:
                entity_dict["data"]["metadata"]["prism"][step] = {}
            entity_dict["data"]["metadata"]["prism"][step].update(data)

            if entitytype == "shot":
                gazu.shot.update_shot(entity_dict)
            else:
                gazu.asset.update_asset(entity_dict)

    @err_catcher(name=__name__)
    def onPostRender(self, state, scenefile, settings):
        login_tokens, project_tokens = self.connectToKitsu(raise_login_error=False)
        data = self.core.entities.getScenefileData(scenefile)
        task_name = state.l_taskName.text()
        scenePath = scenefile
        entityName = data.get("entityName")
        version = data.get("version")
        step = STEP2TASKTRANSLATE.get( data.get("step")) or  data.get("step")
        comment = data.get("comment")
        username = self.core.getConfig("globals", "username")
        
        logger.debug("Render submited to kitsu")

    @err_catcher(name=__name__)
    def createAssets(self, assets):
        login_tokens, project_tokens = self.connectToKitsu()
        if not login_tokens:
            return [], []

        created_assets = []
        updated_assets = []
        configInfo = {}
        for asset_location in assets:
            assetInfo = {}
            # Remove pre-folder path and remove first character
            # before os.sep split and remove last object as it's
            # the name of the asset
            aBasePath = self.core.getAssetPath()
            asset_location = asset_location.replace(aBasePath, "")
            splits = asset_location[1:].split(os.sep)[:-1]

            # If not in any subfolder, assign to the empty asset-type
            if len(splits) == 0:
                splits.append("")

            asset_name = os.path.basename(asset_location)
            asset_type_name = splits[0]

            asset_description = self.core.getConfig(asset_name,
                                                    "description",
                                                    config="assetinfo")

            # If asset has subfolders, add to asset_description
            if len(splits) > 1:
                asset_description = "/".join(splits[1:]) + \
                    " - " + asset_description

            # Get preview image
            previewImgPath = os.path.join(os.path.dirname(self.core.prismIni),
                                          "Assetinfo",
                                          "%s_preview.jpg" % asset_name,
                                          )
            thumbnailURL = previewImgPath if os.path.exists(
                previewImgPath) else None

            asset_type_dict, created_asset_type = createKitsuAssetType(
                asset_type_name)

            asset_dict, created_asset = createKitsuAsset(project_tokens,
                                                         asset_type_dict,
                                                         asset_name,
                                                         asset_description,
                                                         extra_data={},
                                                         episode=None)
            metadata = getEntityConfigData(self.core, asset_location)
            updateKitsuMetadata(asset_dict, metadata, "asset")
            # Add thumbnail if preview image exists
            if thumbnailURL is not None and created_asset:
                while True:
                    # Get task type dict
                    if self.publish_type_dict is None:
                        self.publish_type_dict = getPublishTypeDict(self,
                                                                    "Asset")
                        if self.publish_type_dict is None:
                            if created_asset:
                                RemoveAsset(asset_dict)
                            if created_asset_type:
                                RemoveAssetType(asset_type_dict)
                            break

                    user_email = self.core.getConfig("kitsu", "username")

                    # Ask user to pick task to add thumbnail to
                    thumbnail_id = uploadThumbnail(
                        asset_dict["id"],
                        thumbnailURL,
                        self.publish_type_dict,
                        user_email
                    )
                    assetInfo["thumbnailID"] = thumbnail_id
                    break

            # Write out ID to config
            if created_asset:
                assetInfo["objID"] = asset_dict["id"]
                created_assets.append(asset_name)
                # Add info to config array
                configInfo[asset_name] = assetInfo

        if len(configInfo) > 0:
            # Write information
            self.core.setConfig(data=configInfo, config="assetinfo")

        # Clear the publishing type dict
        self.publish_type_dict = None

        return created_assets, updated_assets

    @err_catcher(name=__name__)
    def createShots(self, shots):
        login_tokens, project_tokens = self.connectToKitsu()

        created_shots = []
        updated_shots = []
        configInfo = {}
        for shot_name in shots:
            shotInfo = {}
            # Get range
            shotRanges = self.core.getConfig("shotRanges",
                                             shot_name,
                                             config="shotinfo"
                                             )

            # Get preview image
            previewImgPath = os.path.join(os.path.dirname(self.core.prismIni),
                                          "Shotinfo",
                                          "%s_preview.jpg" % shot_name,
                                          )

            # Split names
            shotName, seqName = self.core.entities.splitShotname(shot_name)
            if project_tokens["production_type"] == "tvshow":
                try:
                    epName, seqName = seqName.split(".", 1)
                except:
                    epName = "Main Pack"
            else:
                epName = "none"

            thumbnailURL = previewImgPath if os.path.exists(
                previewImgPath) else None

            episode_dict, created_ep = createKitsuEpisode(project_tokens,
                                                          epName)
            sequence_dict, created_seq = createKitsuSequence(project_tokens,
                                                             seqName,
                                                             episode_dict)
            shot_dict, created_shot, isUpdated = createKitsuShot(project_tokens,
                                                      sequence_dict,
                                                      shotName,
                                                      shotRanges)

            metadata = getEntityConfigData(self.core, self.core.getEntityPath(shot=shot_name))
            updateKitsuMetadata(shot_dict, metadata, "shot")
            thumbnailURL = None # force no preview
            # Add thumbnail if preview image exists
            if thumbnailURL is not None and (created_shot or isUpdated):
                while True:
                    # Get task type dict
                    if self.publish_type_dict is None:
                        self.publish_type_dict = getPublishTypeDict(self,
                                                                    "Shot")
                        if self.publish_type_dict is None:
                            if created_shot:
                                RemoveShot(shot_dict)
                                created_shot = False
                            if created_seq:
                                RemoveSequence(sequence_dict)
                            if created_ep:
                                RemoveEpisode(episode_dict)
                            break

                    user_email = self.core.getConfig("kitsu", "username")

                    # Ask user to pick task to add thumbnail to
                    thumbnail_id = uploadThumbnail(
                        shot_dict["id"],
                        thumbnailURL,
                        self.publish_type_dict,
                        user_email
                    )
                    shotInfo["thumbnailID"] = thumbnail_id
                    break

            # Write out ID to config
            if created_shot:
                shotInfo["objID"] = shot_dict["id"]
                created_shots.append(shot_name)
                # Add info to config array
                configInfo[shot_name] = shotInfo
            elif isUpdated:
                updated_shots.append(shot_name)

        if len(configInfo) > 0:
            # Write information
            self.core.setConfig(data=configInfo, config="shotinfo")
        return created_shots, updated_shots

    # Get Kitsu shots
    @err_catcher(name=__name__)
    def getKitsuShots(self, project_tokens={}):
        if not project_tokens:
            login_tokens, project_tokens = self.connectToKitsu()

        ksuShots = []

        # Check if only should get user assigned objects
        user_sync = self.core.getConfig("kitsu",
                                        "usersync",
                                        configPath=self.core.prismIni)


        # Check if tv show, meaning we're also dealing with episodes
        if project_tokens["production_type"] == "tvshow":
            episodes = GetEpisodes(project_tokens, user=user_sync)
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
                project_tokens, "from_project", user=user_sync)

            for sequence in sequences:
                shots = GetShots(sequence, "from_sequence", user=user_sync)

                for shot in shots:
                    ksuShots.append(shot)

        ksuShots = RemoveCanceled(ksuShots)

        return ksuShots


    # Get Kitsu shots
    @err_catcher(name=__name__)
    def getKitsuAssets(self):
        login_tokens, project_tokens = self.connectToKitsu()

        assetTypes = GetAssetTypes()
        ksuAssets = []

        # Check if only should get user assigned objects
        user_sync = self.core.getConfig("kitsu",
                                        "usersync",
                                        configPath=self.core.prismIni)
        for assetType in assetTypes:
            assets = GetAssets(project_tokens, assetType, user=user_sync)
            for asset in assets:
                ksuAssets.append(asset)
        if len(ksuAssets) == 0:
            return False
        ksuAssets = RemoveCanceled(ksuAssets)

        return ksuAssets

    # returns created, updated
    @err_catcher(name=__name__)
    def downloadThumbnail(self, name, preview_file_id, folder_name):
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
                    
                    parent_folder = (
                        os.path.join(
                            os.path.dirname(self.core.prismIni),
                            folder_name
                        )
                    )

                    if not os.path.exists(parent_folder):
                        mkdir_p(parent_folder)
                    
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

    @ err_catcher(name=__name__)
    def convertSeqToVideo(self, origin, temp_folder_name):
        mediaPlayback = origin.mediaPlaybacks["shots"]
        extension = ".mov"

        inputpath = os.path.join(
            mediaPlayback["basePath"], mediaPlayback["seq"][0]
        ).replace("\\", "/")
        inputExt = os.path.splitext(inputpath)[1]

        outputpath = os.path.join(temp_folder_name,
                                  os.path.splitext(mediaPlayback["seq"][0])[0]
                                  + extension)

        if mediaPlayback["prvIsSequence"]:
            inputpath = os.path.splitext(inputpath)[0]
            inputpath = inputpath[:-self.core.framePadding] + \
                "%04d".replace("4", str(self.core.framePadding)) + inputExt

        conversionSettings = {}
        conversionSettings["-c"] = "prores"
        conversionSettings["-profile"] = 2
        conversionSettings["-pix_fmt"] = "yuv422p10le"

        if mediaPlayback["prvIsSequence"]:
            startNum = mediaPlayback["pstart"]
        else:
            startNum = 0
            if inputExt == ".dpx":
                conversionSettings["-start_number"] = None
                conversionSettings["-start_number_out"] = None

        self.core.media.convertMedia(
            inputpath,
            startNum,
            outputpath,
            settings=conversionSettings
        )

        return outputpath
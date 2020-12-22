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

import os
import sys

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

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

modulePath = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "external_modules")
if modulePath not in sys.path:
    sys.path.append(modulePath)

class Prism_Kitsu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.callbacks = []
        self.registerCallbacks()

    @err_catcher(name=__name__)
    def isActive(self):
        return True


    @err_catcher(name=__name__)
    def registerCallbacks(self):
        self.callbacks.append(self.core.registerCallback("projectBrowser_getAssetMenu", self.projectBrowser_getAssetMenu))
        self.callbacks.append(self.core.registerCallback("projectBrowser_getShotMenu", self.projectBrowser_getShotMenu))

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

        lo_prjman.addWidget(origin.l_prjmanSite)
        lo_prjman.addWidget(origin.l_prjmanPrjName)
        lo_prjman.addWidget(origin.l_prjmanUserName)
        lo_prjman.addWidget(origin.l_prjmanUserPassword)
        lo_prjman.addWidget(origin.e_prjmanSite, 0, 1)
        lo_prjman.addWidget(origin.e_prjmanPrjName, 1, 1)
        lo_prjman.addWidget(origin.e_prjmanUserName, 2, 1)
        lo_prjman.addWidget(origin.e_prjmanUserPassword, 3, 1)

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

            actSSL = QAction("Kitsu assets to local", origin)
            actSSL.triggered.connect(lambda: self.prjmanAssetsToLocal(origin))
            prjmanMenu.addAction(actSSL)

            actSSL = QAction("Local assets to Kitsu", origin)
            actSSL.triggered.connect(lambda: self.prjmanAssetsToprjman(origin))
            prjmanMenu.addAction(actSSL)

            prjmanMenu.addSeparator()

            actSSL = QAction("Kitsu shots to local", origin)
            actSSL.triggered.connect(lambda: self.prjmanShotsToLocal(origin))
            prjmanMenu.addAction(actSSL)

            actLSS = QAction("Local shots to Kitsu", origin)
            actLSS.triggered.connect(lambda: self.prjmanShotsToprjman(origin))
            prjmanMenu.addAction(actLSS)

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
    def connectToKitsu(self, user=True):
        try:
            prjmanSite = self.core.getConfig("kitsu", "site", configPath=self.core.prismIni)
            prjmanUser = self.core.getConfig("kitsu", "username")
            prjmanUserPassword = self.core.getConfig("kitsu", "userpassword")
            prjmanName = self.core.getConfig("kitsu", "projectname", configPath=self.core.prismIni)
            import gazu
            api_host= prjmanSite+"/api"
            gazu.set_host(api_host)
            from qtazulite import utils
            try:
                login_tokens = gazu.log_in(prjmanUser, prjmanUserPassword)
            except:
                from qtazulite.widgets.login import Login
                login_window = Login(host = api_host, user=prjmanUser, password=prjmanUserPassword)
                login_window.logged_in.connect(self.prismSettings_saveLoginSettings)
                login_window._exec()
                login_tokens = login_window.login_tokens
            project_tokens = gazu.project.get_project_by_name(prjmanName)
            return login_tokens, project_tokens
        except:
            raise
            return None, None

    @err_catcher(name=__name__)
    def prismSettings_saveLoginSettings(self, user, password):
        self.core.setConfig("kitsu", "username", val=user)
        self.core.setConfig("kitsu", "userpassword", val=password)


    @err_catcher(name=__name__)
    def createprjmanAssets(self, assets=[]):
        import gazu
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
                

            


    @err_catcher(name=__name__)
    def createprjmanShots(self, shots=[]):
        import gazu
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
        kitsup._exec()

    def openprjman(self, shotName=None, eType="Shot", assetPath=""):
        login_tokens, project_tokens = self.connectToKitsu()
        import gazu
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
            subprocess.Popen("C:/Temp/Chromium/chrome.exe {}".format(project_url))
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
        import gazu
        from pathlib import Path
        assets = gazu.asset.all_assets_for_project(project_tokens)
        for asset in assets:
            asset_name = asset.get("name")
            asset_type = gazu.asset.get_asset_type(asset.get("entity_type_id")).get("name")
            assetPath = Path(self.core.assetPath) / asset_type / asset_name
            if not assetPath.exists():
                self.core.entities.createEntity("asset", str(assetPath))
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
        # add code here

        origin.refreshShots()

    @err_catcher(name=__name__)
    def prjmanShotsToprjman(self, origin):
        # add code here

        msgString = "No shots were created or updated."

        QMessageBox.information(self.core.messageParent, "Kitsu Sync", msgString)

    @err_catcher(name=__name__)
    def onProjectBrowserClose(self, origin):
        pass

    @err_catcher(name=__name__)
    def onSetProjectStartup(self, origin):
        pass




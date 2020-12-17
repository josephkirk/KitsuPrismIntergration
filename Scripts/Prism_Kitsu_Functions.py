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

from gazu import log_in, project

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
            prjmanMenu = QMenu("Kitsu", origin)

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

        sg = self.core.getConfig("kitsu", "active", configPath=self.core.prismIni)
        if sg:
            kitsuAction = QAction("Open in Kitsu", origin)
            kitsuAction.triggered.connect(
                lambda: self.openprjman(assetname, eType="Asset", assetPath=assetPath)
            )
            return kitsuAction

    @err_catcher(name=__name__)
    def projectBrowser_getShotMenu(self, origin, shotname):
        sg = self.core.getConfig("kitsu", "active", configPath=self.core.prismIni)
        if sg:
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
            "Kitsu", "active", configPath=self.core.prismIni
        )
        if not prjman:
            return

        origin.chb_createInKitsu = QCheckBox("Create asset in Kitsu")
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
        ):
            self.createprjmanAssets([assetPath])

    @err_catcher(name=__name__)
    def editShot_open(self, origin, shotName):
        if shotName is None:
            prjman = self.core.getConfig(
                "Kitsu", "active", configPath=self.core.prismIni
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
                login_window.exec()
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
        pass

    @err_catcher(name=__name__)
    def createprjmanShots(self, shots=[]):
        pass

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
            version=versionName,
            sources=imgPaths,
            startFrame=sf,
        )
        kitsup.exec()

    def openprjman(self, shotName=None, eType="Shot", assetPath=""):
        login_tokens, project_tokens = self.connectToKitsu()
        import gazu
        project_url = gazu.project.get_project_url(project_tokens)
        launch_url = project_url.replace("http://", login_tokens.get("access_token") + "@")
        import subprocess
        try:
            subprocess.Popen("C:/Temp/Chromium/chrome.exe {}".format(project_url))
        except:
            # pass
            import webbrowser

            webbrowser.open(launch_url)

    @err_catcher(name=__name__)
    def prjmanAssetsToLocal(self, origin):
        # add code here

        createdAssets = []
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




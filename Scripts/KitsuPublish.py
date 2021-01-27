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


import os
import sys
import traceback
import subprocess
import datetime
import platform
import imp
try:
    
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    psVersion = 2
    # from PySide2.QtQuick import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

    psVersion = 1

if sys.version[0] == "3":
    pVersion = 3
else:
    pVersion = 2

sys.path.append(os.path.join(os.path.dirname(__file__), "UserInterfaces"))

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

if psVersion == 1:
    import KitsuPublish_ui
else:
    import KitsuPublish_ui_ps2 as KitsuPublish_ui

try:
    import gazulite as gazu
except:
    import gazu

from Prism_Kitsu_Utils_Functions import *

class Publish(QDialog, KitsuPublish_ui.Ui_dlg_kitsuPublish):
    def __init__(
        self, core, origin, ptype, shotName, task, version, preview, sources, startFrame
    ):
        QDialog.__init__(self)
        self.setupUi(self)
        self.core = core
        self.core.parentWindow(self)
        self.ptype = ptype
        self.preview = preview
        self.shotName = shotName
        self.taskVersion = version
        self.fileSources = sources
        self.startFrame = startFrame
        self.shotList = {}
        self.login_tokens, self.project_tokens = origin.connectToKitsu()
        self.current_shot = shotName
        self.connectEvents()
        
        
        if not all([self.login_tokens, self.project_tokens]):
            return
        if ptype == "Asset":
            self.rb_asset.setChecked(True)
        elif ptype == "Shot":
            self.rb_shot.setChecked(True)
        # self.cb_status.append(self.task_types)
    @err_catcher(name=__name__)
    def updateStatus(self):
        self.cb_status.clear()
        for status in gazu.task.all_task_statuses():
            self.cb_status.addItem(status['name'], status)

    @err_catcher(name=__name__)
    def updateAssets(self, toggleStatus):
        if not toggleStatus:
            return
        self.data_token = gazu.asset.get_asset_by_name(self.project_tokens, self.current_shot)
        self.task_types = gazu.task.all_task_types_for_asset(self.data_token)
        self.cb_shot.clear()
        for asset in gazu.asset.all_assets_for_project(self.project_tokens):
            asset = gazu.asset.get_asset(asset['id'])
            self.cb_shot.addItem(asset['name'], asset)
        # self.cb_shot.setCurrentIndex(self.cb_shot.findText(shotname))

        self.updateStatus()
    
    @err_catcher(name=__name__)
    def updateShots(self, toggleStatus):
        if not toggleStatus:
            return
        shotname, seqname = self.core.entities.splitShotname(self.shotName)
        self.sequence = gazu.shot.get_sequence_by_name(self.project_tokens, seqname)
        self.shot = gazu.shot.get_shot_by_name(self.sequence, shotname)
        self.cb_shot.clear()
        for shot in gazu.shot.all_shots_for_project(self.project_tokens):
            shot = gazu.shot.get_shot(shot.get('id'))
            self.cb_shot.addItem("{}-{}".format(shot.get("sequence_name"),shot.get("name"), shot))
        
        self.cb_shot.setCurrentIndex(self.cb_shot.findText(shotname))
        # self.task_types = gazu.task.all_task_types()
        self.updateStatus()

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.rb_asset.toggled.connect(self.updateAssets)
        self.rb_shot.toggled.connect(self.updateShots)
    #     # 	self.b_addTask.clicked.connect(self.createTask)
    #     self.b_addTask.setVisible(False)
    #     self.cb_shot.activated.connect(self.updateTasks)
    #     self.b_sgPublish.clicked.connect(self.publish)
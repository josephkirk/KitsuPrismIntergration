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
if psVersion == 1:
    import KitsuPublish_ui
else:
    import KitsuPublish_ui_ps2 as KitsuPublish_ui

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
        login_tokens, project_tokens = origin.connectToKitsu()
        if not all([login_tokens, project_tokens]):
            return
        if ptype == "Asset":
            self.data_token = gazu.asset.get_asset_by_name(project_tokens, shotName)
            self.task_types = gazu.task.all_task_types_for_asset(self.data_token)
            self.rb_asset.setChecked(True)
        elif ptype == "Shot":
            shot, sequence = core.entities.splitShotname(shotName)
            self.sequence = gazu.shot.get_sequence_by_name(project_tokens, sequence)
            self.shot = gazu.shot.get_shot_by_name(self.sequence, shot)
            self.all_datas = [gazu.shot.get_shot(s.get('id')) for s in gazu.shot.all_shots_for_project(project_tokens)]
            all_shotname = ["{}-{}".format(s.get("sequence_name"),s.get("name")) for s in self.all_datas]
            self.cb_shot.addItems(all_shotname)
            
            # self.cb_shot.setCurrentIndex(self.cb_shot.findText(shotName.split("-")[-1]))
            self.task_types = gazu.task.all_task_types()
            self.rb_shot.setChecked(True)
            self.cb_status.addItems([i.get('name') for i in gazu.task.all_task_statuses()])
        
        # self.cb_status.append(self.task_types)
        
    # @err_catcher(name=__name__)
    # def connectEvents(self):
    #     self.rb_asset.pressed.connect(self.updateShots)
    #     self.rb_shot.pressed.connect(self.updateShots)
    #     # 	self.b_addTask.clicked.connect(self.createTask)
    #     self.b_addTask.setVisible(False)
    #     self.cb_shot.activated.connect(self.updateTasks)
    #     self.b_sgPublish.clicked.connect(self.publish)
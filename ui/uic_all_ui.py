#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: uic_all_ui.py
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 1 Apr 2016 15:32:13 AM CST
#########################################################################

import os
for root, dirs, files in os.walk('.'):
    for file_name in files:
        if file_name.endswith('.ui'):
            print file_name
            os.system('pyuic4 -o ui_%s.py -x %s' % (file_name.rsplit('.', 1)[0], file_name))
        elif file_name.endswith('.qrc'):
            print file_name
            os.system('pyrcc4 -o %s_rc.py %s' % (file_name.rsplit('.', 1)[0], file_name))

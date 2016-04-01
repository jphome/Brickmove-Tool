#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: main.pyw
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 02 Apr 2016 01:27:47 AM CST
#########################################################################
# -- change log --
# 2016.03.31    添加获取、设置osd功能
# 2016.04.01    添加osd搜索显示功能、添加公众号图片
# 2016.04.02    简化sdk代码、实现sadp搜索多线程异步
# 待优化：版本信息、是否开启预览开关
import sys
import os
import time
import datetime
import threading
from ctypes import *

from PyQt4 import QtCore,QtGui
from ui import *

from common import *

from sdk.Sadp import *
from sdk.HCNetSDK import *

sadp = Sadp()
online_devices = {}

def sadpSlotFun():
    print 'trans signal'
    myapp.refresh_online_devlist()

class sadpThread(QtCore.QThread, QtCore.QObject):
    sadpslot = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
    def run(self):
        global online_devices
        sadp.sadp_start()
        online_devices = sadp.sadp_get_online_devices_info()
        sadp.sadp_stop()
        print 'sadp search finish'
        self.sadpslot.emit()
        
sadp_thread = sadpThread()
sadp_thread.sadpslot.connect(sadpSlotFun)

class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent = None):
            QtGui.QWidget.__init__(self, parent)
            
            ## 类静态变量
#            self.sadp = Sadp()
            self.hcnetsdk = HCNetSDK()
            # play句柄
            self.lRealPlayHandle = 0
            # playing flag
            self.RealPlay = 0
            # 配置参数
            self.cfg_pic = None
            
            self.mainwindow = QtGui.QMainWindow()
            self.mainwindow_ui = Ui_MainWindow()
            self.mainwindow_ui.setupUi(self.mainwindow)
            self.mainwindow.show()
            
            self.hPlayWnd = self.mainwindow_ui.Preview_frame.winId()
            
            # IP地址、激活状态、设备序列号、MAC地址
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(0, 64)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(1, 120)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(2, 80)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(3, 45)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(4, 35)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(5, 80)
            self.mainwindow_ui.treeWidget_devinfo.setColumnWidth(6, 120)
            
            # 信号绑定
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_refresh, QtCore.SIGNAL('clicked()'), self.sadp_search)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_clear, QtCore.SIGNAL('clicked()'), self.clear_dev_status)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_plus,  QtCore.SIGNAL('clicked()'), self.ip_plus)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_minus,  QtCore.SIGNAL('clicked()'), self.ip_minus)
            QtCore.QObject.connect(self.mainwindow_ui.treeWidget_devinfo,  QtCore.SIGNAL('itemSelectionChanged()'),  self.dev_selected)
            
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_getNetInfo, QtCore.SIGNAL('clicked()'), self.getLocalNetInfo)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_setNetInfo, QtCore.SIGNAL('clicked()'), self.setLocalNetInfo)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_setOsd, QtCore.SIGNAL('clicked()'), self.setOsd)

            # 打开软件即刻搜索
#            self.refresh_online_devlist()
#            self.mainwindow_ui.Preview_frame.setSceneRect
            
    def dev_selected(self):
        """
            登陆、预览设备；
            更新配置信息；
        """
        # 更新设备信息
        lpDeviceInfo = None
        password = self.mainwindow_ui.lineEdit_devPassword.text()
        select_items = self.mainwindow_ui.treeWidget_devinfo.selectedItems()
        IP_Address = ''
        if select_items != []:
            select_item = select_items[0]
            IP_Address = select_item.text(2)
            self.mainwindow_ui.lineEdit_ip.setText(IP_Address)
        else:
            self.mainwindow_ui.lineEdit_ip.setText('255.255.255.255')
            return
        
        # 登陆设备
        try:
            lpDeviceInfo = self.hcnetsdk.netsdk_connect_device(str(IP_Address),8000,'admin',password)
        except Exception, errorCode:
            # 密码错误，登陆失败
            # 此处错误校验有问题
            if errorCode == 1:
                warning = u'密码错误'
            else:
                warning = u'登陆失败'
            message = QtGui.QMessageBox(self)
            message.setText(warning)
            message.setWindowTitle(u'登陆')
            message.exec_()
            if self.RealPlay:
                self.hcnetsdk.netsdk_stop_realPlay(self.lRealPlayHandle)
                self.mainwindow_ui.Preview_frame.update()
                self.RealPlay = 0
            return
        
        # 更新OSD信息
        self.cfg_pic = self.hcnetsdk.netsdk_get_pic_cfg()
        channel_name = unicode(self.cfg_pic.sChanName, 'gbk', 'ignore')
        self.mainwindow_ui.lineEdit_osd.setText(channel_name)
        
        # 开始预览
        if self.mainwindow_ui.checkBox_ifPreview.isChecked():
            if (not self.RealPlay):
                self.lRealPlayHandle = self.hcnetsdk.netsdk_realPlay(1, 1, int(self.hPlayWnd))
                if self.lRealPlayHandle == -1:
                    self.RealPlay = 0
                else:
                    self.RealPlay = 1
            else:
                self.hcnetsdk.netsdk_stop_realPlay(self.lRealPlayHandle)
                self.mainwindow_ui.Preview_frame.update()
                self.lRealPlayHandle = self.hcnetsdk.netsdk_realPlay(1, 1, int(self.hPlayWnd))
                if self.lRealPlayHandle == -1:
                    self.RealPlay = 0
                else:
                    self.RealPlay = 1

    def clear_dev_status(self):
        """
            清空设备列表
        """
        global online_devices
        if self.RealPlay:
            self.hcnetsdk.netsdk_stop_realPlay(self.lRealPlayHandle)
            self.mainwindow_ui.Preview_frame.update()
            self.RealPlay = 0
        self.mainwindow_ui.treeWidget_devinfo.clear()
        self.mainwindow_ui.label_online_dev_num.setText('0')
        online_devices = {}

    def sadp_search(self):        
        if len(online_devices) != 0:
            message = QtGui.QMessageBox(self)
            message.setText(u'请先点击“清除”')
            message.setWindowTitle(u'警告')
            message.exec_()
            return
        else:
            print 'sadp start search'
            sadp_thread.start()
        
    def refresh_online_devlist(self):
        """
            更新设备列表
        """
        print 'refresh_online_devlist'
        num_online_devices = len(online_devices)
        self.mainwindow_ui.label_online_dev_num.setText(str(num_online_devices))
        
        # tree控件显示在线设备信息
        # 1-序号，2-设备型号，3-IP地址，4-OSD，5-激活状态，6-序列号，7-MAC地址，8-启动时间
        index = 1
        for keys in online_devices:
            line = QtGui.QTreeWidgetItem(self.mainwindow_ui.treeWidget_devinfo)
            if index < 10:
                line.setText(0,  '00'+str(index))
            elif index >99:
                line.setText(0,  str(index))
            else:
                line.setText(0,  '0'+str(index))
            index = index + 1
            line.setText(1, online_devices[keys]['DeviceType'])
            line.setText(2, online_devices[keys]['IP'])
            if online_devices[keys]['Activated'] == 0:
                line.setText(4, 'YES')
            else:
                line.setText(4, 'NO')
            line.setText(5, online_devices[keys]['SerialNO'][-9:])
            line.setText(6,  online_devices[keys]['MAC'])
            line.setText(7,  online_devices[keys]['BootTime'])
            
            # OSD信息
            devPassword = self.mainwindow_ui.lineEdit_devPassword.text()
            localIp = get_local_ip()[0].split('.')
            devIp = online_devices[keys]['IP'].split('.')
            if localIp[0]==devIp[0] and localIp[1]==devIp[1] and localIp[2]==devIp[2]:
                devAvailable = True
            else:
                devAvailable = False
            # 同一网段并且勾选osd需求才进行osd通道信息获取
            if self.mainwindow_ui.checkBox_osd.isChecked() and devAvailable:
                try:
                    self.hcnetsdk.netsdk_connect_device(str(online_devices[keys]['IP']),8000,'admin',devPassword)
                    try:
                        self.cfg_pic = self.hcnetsdk.netsdk_get_pic_cfg()
                        channel_name = unicode(self.cfg_pic.sChanName, 'gbk', 'ignore')
                        line.setText(3,  channel_name)
                    except:
                        print 'getpic except'
                        line.setText(3,  u'不支持')
                except:
                    print 'connect except'
                    line.setText(3,  u'不支持')
            else:
                line.setText(3,  u'不支持')

    def setOsd(self):
        """
            通道名称osd配置
        """
        channel_name_pyqt = self.mainwindow_ui.lineEdit_osd.text()
        channel_name_unicode = unicode(channel_name_pyqt)
        channel_name_gbk = channel_name_unicode.encode('gbk')
        self.cfg_pic.sChanName = channel_name_gbk
        self.hcnetsdk.netsdk_set_pic_cfg(self.cfg_pic)

    def ip_plus(self):
        ip_str = self.mainwindow_ui.lineEdit_ip.text()
        ip_secs = ip_str.split('.')
        if int(ip_secs[3]) > 253:
            ip_secs[3] = '0'
        else:
            ip_secs[3] = str(int(ip_secs[3]) + 1)
        ip_str = ip_secs[0]+'.'+ip_secs[1]+'.'+ip_secs[2]+'.'+ip_secs[3]
        self.mainwindow_ui.lineEdit_ip.setText(ip_str)
        
    def ip_minus(self):
        ip_str = self.mainwindow_ui.lineEdit_ip.text()
        ip_secs = ip_str.split('.')
        if int(ip_secs[3]) == 0:
            ip_secs[3] = '253'
        else:
            ip_secs[3] = str(int(ip_secs[3]) - 1)
        ip_str = ip_secs[0]+'.'+ip_secs[1]+'.'+ip_secs[2]+'.'+ip_secs[3]
        self.mainwindow_ui.lineEdit_ip.setText(ip_str)
        
    def getLocalNetInfo(self):
        self.mainwindow_ui.lineEdit_localIp.setText(get_local_ip()[0])
    def setLocalNetInfo(self):
        set_local_ip(ip=str(self.mainwindow_ui.lineEdit_localIp.text()))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    app.exec_()

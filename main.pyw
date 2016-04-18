#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: main.pyw
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 02 Apr 2016 01:27:47 AM CST
#########################################################################
# -- change log --
# 2016.03.31    添加获取，设置osd功能
# 2016.04.01    添加osd搜索显示功能，添加公众号图片
# 2016.04.02    简化sdk代码，实现sadp搜索多线程异步
# 2016.04.12    add版本信息，修改pc ip（以管理员身份运行），设备osd配置规则功能实现
# 2016.04.14    删除确认按钮（回车替代），捕捉上下键实现+-，双击设备ip时打开系统默认浏览器访问
# 2016.04.16    优化异步搜索设备，增加快捷键F4、F5、↑、↓、PageUp、PageDown，增加设备ip配置
# TODO：设备列表导出到excel、（批量）激活设备、批量配置、操作日志记录、（批量）修改设备密码
import sys
import os
import webbrowser
from ctypes import *

from PyQt4 import QtCore,QtGui
from ui import *

from common import *
from local import *

from sdk.Sadp import *
from sdk.HCNetSDK import *

sadp = None
online_devices = {}

class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent = None):
            QtGui.QWidget.__init__(self, parent)
            
            ## 类静态变量
            self.hcnetsdk = HCNetSDK()
            # play句柄
            self.lRealPlayHandle = 0
            # playing flag
            self.RealPlay = 0
            # 配置参数
            self.cfg_pic = None
            # 密码
            self.password = 'abcd1234'
            # 选中设备的IP地址
            self.IP_Address = ''
            # 选中设备的MAC地址
            self.MAC = ''
            
            self.sadp_thread = sadpThread()
#            self.sadp_thread.sadpslot.connect(sadpSlotFun)
            self.sadp_thread.start()
            
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
#            self.mainwindow_ui.pushButton_refresh.clicked.connect(self.refresh_device_list)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_clear, QtCore.SIGNAL('clicked()'), self.clear_device_list)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_refresh, QtCore.SIGNAL('clicked()'), self.refresh_device_list)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_excel, QtCore.SIGNAL('clicked()'), self.export_to_excel)
            
            QtCore.QObject.connect(self.mainwindow_ui.treeWidget_devinfo,  QtCore.SIGNAL('itemSelectionChanged()'),  self.dev_selected)
            QtCore.QObject.connect(self.mainwindow_ui.treeWidget_devinfo,  QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*,int)'),  self.browser_dev)
            
            # 配置IP地址
            QtCore.QObject.connect(self.mainwindow_ui.lineEdit_ip, QtCore.SIGNAL('returnPressed()'), self.setIp)
            # 配置OSD
            QtCore.QObject.connect(self.mainwindow_ui.lineEdit_osd, QtCore.SIGNAL('returnPressed()'), self.setOsd)
            
            # 实用工具菜单
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_getNetInfo, QtCore.SIGNAL('clicked()'), self.getLocalNetInfo)
            QtCore.QObject.connect(self.mainwindow_ui.pushButton_setNetInfo, QtCore.SIGNAL('clicked()'), self.setLocalNetInfo)
            
            # 线程输出
            self.connect(self.sadp_thread, QtCore.SIGNAL("refresh_online_devlist()"), self.refresh_online_devlist)
            
            # 安装事件过滤器，捕捉按键
            self.mainwindow_ui.lineEdit_ip.installEventFilter(self)
            self.mainwindow_ui.lineEdit_osd.installEventFilter(self)
            self.mainwindow_ui.BMTool_frame.installEventFilter(self)

            # 打开软件即刻搜索
#            self.refresh_device_list()

    def eventFilter(self, source, event):
        """
            事件过滤器处理按键需求
        """
        if event.type() == QtCore.QEvent.KeyPress:
            # F4
            if event.key() == QtCore.Qt.Key_F4:
                self.clear_device_list()
            # F5
            if event.key() == QtCore.Qt.Key_F5:
                self.refresh_device_list()
            # Arrow UP按键
            if event.key() == QtCore.Qt.Key_Up:
                if source == self.mainwindow_ui.lineEdit_ip:
                    ip_str = str(self.mainwindow_ui.lineEdit_ip.text())
                    ip_secs = ip_str.split('.')
                    ip_tail = eval(ip_secs[3]+'+1')
                    if ip_tail > 253:
                        ip_tail = 2
                    elif ip_tail < 2:
                        ip_tail = 253
                    ip_secs[3] = str(ip_tail)
                    ip_str = '.'.join(ip_secs)
                    self.mainwindow_ui.lineEdit_ip.setText(ip_str)
                elif source == self.mainwindow_ui.lineEdit_osd:
                    old_str = str(self.mainwindow_ui.lineEdit_osd.text())
                    new_int = eval(old_str + '+1')
                    self.mainwindow_ui.lineEdit_osd.setText(str(new_int))
            # Arrow DOWN按键
            elif event.key() == QtCore.Qt.Key_Down:
                if source == self.mainwindow_ui.lineEdit_ip:
                    ip_str = str(self.mainwindow_ui.lineEdit_ip.text())
                    ip_secs = ip_str.split('.')
                    ip_tail = eval(ip_secs[3]+'-1')
                    if ip_tail > 253:
                        ip_tail = 2
                    elif ip_tail < 2:
                        ip_tail = 253
                    ip_secs[3] = str(ip_tail)
                    ip_str = '.'.join(ip_secs)
                    self.mainwindow_ui.lineEdit_ip.setText(ip_str)
                elif source == self.mainwindow_ui.lineEdit_osd:
                    old_str = str(self.mainwindow_ui.lineEdit_osd.text())
                    new_int = eval(old_str + '-1')
                    self.mainwindow_ui.lineEdit_osd.setText(str(new_int))
            # PageUp按键
            elif event.key() == QtCore.Qt.Key_PageUp:
                if source == self.mainwindow_ui.lineEdit_osd:
                    select_items = self.mainwindow_ui.treeWidget_devinfo.selectedItems()
                    if len(select_items) == 1:
                        item_current = select_items[0]
                        item_above = self.mainwindow_ui.treeWidget_devinfo.itemAbove(item_current)
                        if item_above:
                            self.mainwindow_ui.treeWidget_devinfo.setItemSelected(item_current, False)
                            self.mainwindow_ui.treeWidget_devinfo.setItemSelected(item_above, True)
            # PageDown按键
            elif event.key() == QtCore.Qt.Key_PageDown:
                if source == self.mainwindow_ui.lineEdit_osd:
                    select_items = self.mainwindow_ui.treeWidget_devinfo.selectedItems()
                    if len(select_items) == 1:
                        item_current = select_items[0]
                        item_below = self.mainwindow_ui.treeWidget_devinfo.itemBelow(item_current)
                        if item_below:
                            self.mainwindow_ui.treeWidget_devinfo.setItemSelected(item_current, False)
                            self.mainwindow_ui.treeWidget_devinfo.setItemSelected(item_below, True)
        return QtGui.QMainWindow.eventFilter(self, source, event)#将事件交给上层对话框

    def dev_selected(self):
        """
            登陆、预览设备；
            更新配置信息；
        """
        # 更新设备信息
        lpDeviceInfo = None
        self.password = self.mainwindow_ui.lineEdit_devPassword.text()
        select_items = self.mainwindow_ui.treeWidget_devinfo.selectedItems()
        if len(select_items) == 1:
            select_item = select_items[0]
            self.IP_Address = select_item.text(2)
            self.MAC = select_item.text(6)
            self.mainwindow_ui.lineEdit_ip.setText(self.IP_Address)
        else:
            self.mainwindow_ui.lineEdit_ip.setText('255.255.255.255')
            return
        
        # 登陆设备
        try:
            lpDeviceInfo = self.hcnetsdk.netsdk_connect_device(str(self.IP_Address),8000,'admin',self.password)
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
#        self.mainwindow_ui.comboBox_osdrule.setCurrentIndex(0)
        
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

    def clear_device_list(self):
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

    def refresh_device_list(self):
        if self.mainwindow_ui.treeWidget_devinfo.topLevelItemCount () != 0:
            message = QtGui.QMessageBox(self)
            message.setText(u'请先点击“清除”')
            message.setWindowTitle(u'警告')
            message.exec_()
            return
        else:
            print 'sadp start search'
            self.sadp_thread.update()
        
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
            self.password = self.mainwindow_ui.lineEdit_devPassword.text()
            localIp = get_local_ip().split('.')
            devIp = online_devices[keys]['IP'].split('.')
            if localIp[0]==devIp[0] and localIp[1]==devIp[1] and localIp[2]==devIp[2]:
                devAvailable = True
            else:
                devAvailable = False
            # 同一网段并且勾选osd需求才进行osd通道信息获取
            if self.mainwindow_ui.checkBox_osd.isChecked() and devAvailable:
                try:
                    self.hcnetsdk.netsdk_connect_device(str(online_devices[keys]['IP']),8000,'admin',self.password)
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

    def setIp(self):
        dst_ip = self.mainwindow_ui.lineEdit_ip.text()
        self.password = self.mainwindow_ui.lineEdit_devPassword.text()
        device_info = []
        device_info.append(online_devices[str(self.MAC)])
        ret = sadp.sadp_modify_device_net_parameters('ip', self.IP_Address, device_info, self.password, IP=dst_ip)
        if ret:
            current_item = self.mainwindow_ui.treeWidget_devinfo.selectedItems()[0]
            current_item.setText(2, dst_ip)
            self.mainwindow_ui.treeWidget_devinfo.setCurrentItem(current_item)
            self.dev_selected()
        
    def setOsd(self):
        """
            通道名称osd配置
        """
        if not self.cfg_pic:
            return
        osdrule_dict = {
            0:  lambda ip:'', # 空
            1:  lambda ip:ip.split('.')[-1],  # IP地址末1位
            2:  lambda ip:'.'.join(ip.split('.')[-2:]),     # IP地址末2位
            3:  lambda ip:ip,   # 完整IP地址
        }
        osden_dict = {
            0: '', 
            1: 'E', 
            2: 'F', 
            3: 'G', 
        }
        osd_rule_index = self.mainwindow_ui.comboBox_osdrule.currentIndex()
        ip_QString = self.IP_Address
        ip_unicode = unicode(ip_QString)
        osd_head_unicode = osdrule_dict[osd_rule_index](ip_unicode)
        
        osd_mid_index = self.mainwindow_ui.comboBox_en.currentIndex()
        osd_mid_unicode = osden_dict[osd_mid_index]
        
        osd_tail_QString = self.mainwindow_ui.lineEdit_osd.text()
        osd_tail_unicode = unicode(osd_tail_QString)
        
        channel_name_unicode = osd_head_unicode + ' ' + osd_mid_unicode + osd_tail_unicode
        print 'Setup channel name: %s' % channel_name_unicode
        osd_gbk = channel_name_unicode.encode('gbk')
        self.cfg_pic.sChanName = osd_gbk
        self.hcnetsdk.netsdk_set_pic_cfg(self.cfg_pic)

    def browser_dev(self, item, column):
        """
            使用默认浏览器访问设备
        """
        if column == 2:
            webbrowser.open(self.IP_Address)
            print 'Browser open %s done' % self.IP_Address

    def getLocalNetInfo(self):
        self.mainwindow_ui.lineEdit_localIp.setText(get_local_ip())
    def setLocalNetInfo(self):
        set_local_ip(ip=str(self.mainwindow_ui.lineEdit_localIp.text()))
        
    def export_to_excel(self):
        message = QtGui.QMessageBox(self)
        message.setText(u'已导出至桌面')
        message.setWindowTitle(u'已导出至桌面')
        message.exec_()
        if len(online_devices) == 0:
            return


class sadpThread(QtCore.QThread, QtCore.QObject):
    update_flag = False
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        global sadp
        sadp = Sadp()
    def run(self):
        """
            sadp线程运行函数
        """
        print 'Sdap thread start'
        global online_devices
        sadp.sadp_start()
        while(True):
            online_devices = sadp.sadp_get_online_devices_info()
            print 'Sadp update finish'
            if self.update_flag:
                self.emit(QtCore.SIGNAL("refresh_online_devlist()"))
                self.update_flag = False
    def update(self):
        self.update_flag = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
#    sadp_thread.start()
    app.exec_()

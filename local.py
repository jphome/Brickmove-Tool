#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: local.py
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 06 Apr 2016 16:05:46 AM CST
#########################################################################
import wmi
#http://cache.baiducontent.com/c?m=9f65cb4a8c8507ed4fece763105392230e54f733628a854d2c90c05f93130716017ba0fc7f794c5a8e99296401ae540faaa16c2973543db799ca8d57dfbf8f282d952434771a874705d36ef58d197bd565cd1abfa05bacfcaa6fcfb9d2a29a0b08dd52756df6f29c2c7703ba65e76537f4a7e91357&p=8d49ce5f9c8c12a05abd9b7d0d12c1&newp=84769a47cc9915f340bd9b7d0d12bb231610db2151d4d213658ec7148b&user=baidu&fm=sc&query=python+wmi%D0%DE%B8%C4ip&qid=d60f07e40004363c&p1=8

import sys,time,platform

localWMI = wmi.WMI()
os = platform.system()

def get_system_info(): 
    """  
    获取操作系统版本。  
    """  
    print 
    print "Operating system:" 
    if os == "Windows": 
        for sys in localWMI.Win32_OperatingSystem(): 
            print '\t' + "Version :\t%s" % sys.Caption.encode("GBK") 
            print '\t' + "Vernum :\t%s" % sys.BuildNumber 

def get_memory_info(): 
    """  
    获取物理内存和虚拟内存。  
    """  
    print 
    print "memory_info:" 
    if os == "Windows": 
        cs = localWMI.Win32_ComputerSystem()  
        pfu = localWMI.Win32_PageFileUsage()  
        MemTotal = int(cs[0].TotalPhysicalMemory)/1024/1024 
        print '\t' + "TotalPhysicalMemory :" + '\t' + str(MemTotal) + "M" 
        #tmpdict["MemFree"] = int(os[0].FreePhysicalMemory)/1024  
        SwapTotal = int(pfu[0].AllocatedBaseSize) 
        print '\t' + "SwapTotal :" + '\t' + str(SwapTotal) + "M" 
        #tmpdict["SwapFree"] = int(pfu[0].AllocatedBaseSize - pfu[0].CurrentUsage) 
 
def get_disk_info():  
    """  
    获取物理磁盘信息。  
    """  
    print 
    print "disk_info:" 
    if os == "Windows": 
        tmplist = []  
        for physical_disk in localWMI.Win32_DiskDrive(): 
            if physical_disk.Size: 
                print '\t' + str(physical_disk.Caption) + ' :\t' + str(long(physical_disk.Size)/1024/1024/1024) + "G" 
 
def get_cpu_info():  
    """  
    获取CPU信息。  
    """  
    print 
    print "cpu_info:" 
    if os == "Windows": 
        tmpdict = {}  
        tmpdict["CpuCores"] = 0  
        for cpu in localWMI.Win32_Processor():             
            tmpdict["CpuType"] = cpu.Name  
        try:  
            tmpdict["CpuCores"] = cpu.NumberOfCores  
        except:  
            tmpdict["CpuCores"] += 1  
            tmpdict["CpuClock"] = cpu.MaxClockSpeed     
        print '\t' + 'CpuType :\t' + str(tmpdict["CpuType"]) 
        print '\t' + 'CpuCores :\t' + str(tmpdict["CpuCores"]) 
 
 
def get_network_info():  
    """  
    获取网卡信息和当前TCP连接数。  
    """  
    print 
    print "network_info:" 
    if os == "Windows": 
        tmplist = []
        for interface in localWMI.Win32_NetworkAdapterConfiguration (IPEnabled=1):  
                tmpdict = {}  
                tmpdict["Description"] = interface.Description  
                tmpdict["IPAddress"] = interface.IPAddress[0]  
                tmpdict["IPSubnet"] = interface.IPSubnet[0]  
                tmpdict["MAC"] = interface.MACAddress 
                tmplist.append(tmpdict)  
        for i in tmplist: 
            print '\t' + i["Description"] 
            print '\t' + '\t' + "MAC :" + '\t' + i["MAC"] 
            print '\t' + '\t' + "IPAddress :" + '\t' + i["IPAddress"] 
            print '\t' + '\t' + "IPSubnet :" + '\t' + i["IPSubnet"] 
        for interfacePerfTCP in localWMI.Win32_PerfRawData_Tcpip_TCPv4():  
                print '\t' + 'TCP Connect :\t' + str(interfacePerfTCP.ConnectionsEstablished)  

def get_local_ip():
    ip_list = []
    for interface in localWMI.Win32_NetworkAdapterConfiguration (IPEnabled=1): 
        ip_list.append(interface.IPAddress[0])
    return ip_list[0]

def set_local_ip(ip):
    colNicConfigs = localWMI.Win32_NetworkAdapterConfiguration(IPEnabled = True)
    if len(colNicConfigs) < 1:
        print u'没有找到可用的网络适配器'
        return
    objNicConfig = colNicConfigs[0]
    IPAddresses = []
    IPAddresses.append(ip)
    returnValue = objNicConfig.EnableStatic(IPAddress = IPAddresses, SubnetMask = ['255.255.255.0'])
    if returnValue[0] == 0:
        print u'成功设置IP'
    elif returnValue[0] == 1:
        print u'成功设置IP，需要重新pc'
    else:
        print u'修改IP失败(IP设置发生错误)'
        return
    
if __name__ == "__main__":
    print get_local_ip()

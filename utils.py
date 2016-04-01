#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: utils.py
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 02 Apr 2016 01:30:23 AM CST
#########################################################################
import sys
import time
import string
from ctypes import Structure
if sys.platform == 'win32':
    from ctypes.wintypes import BYTE
    if sys.hexversion > 50331648:
        import winreg
    else:
        import _winreg as winreg
elif sys.platform.startswith('linux'):
    from ctypes import c_ubyte as BYTE

def timestamp():
    return time.strftime('%Y%m%d%X', time.localtime()).replace(':', '')


def log_timestamp():
    return time.strftime('[%Y-%m-%d %X] ', time.localtime())


def file_timestamp():
    return time.strftime('%Y-%m-%d_%X_', time.localtime()).replace(':', '')


def file_timestamp_suffix():
    return time.strftime('_%Y-%m-%d_%X', time.localtime()).replace(':', '')


def cbytearray_to_string(byte_array):
    string = ''
    for i in byte_array:
        if i == 0:
            break
        else:
            string = string + chr(i)

    return string


def cbytearray_to_chr_list(byte_array):
    chr_list = []
    for i in byte_array:
        chr_list.append(chr(i))

    return chr_list


def mac_string_to_byte_array(mac_address):
    class DATA_STRUCT(Structure):
        _fields_ = [('byMACAddr', BYTE * 6)]

    datastruct = DATA_STRUCT()
    mac_num_list = mac_address.split(':')
    if len(mac_num_list) == 6:
        for i in range(6):
            datastruct.byMACAddr[i] = string.atoi(mac_num_list[i], 16)

    else:
        raise Exception('Wrong Mac format !')
    return datastruct.byMACAddr


def byte_array_to_mac_string(byte_array):
    string_list = []
    for byte in byte_array:
        string_list.append('%02X' % byte)

    return ':'.join(string_list)


def gbk_cbytearray_to_unicode(byte_array):
    text = ''
    for i in byte_array:
        if i == 0:
            break
        else:
            text = text + chr(i & 255)

    return text.decode('gbk')


def unicode_to_gbk_cbytearray(hanzi, byte_size):
    class DATA_STRUCT(Structure):
        _fields_ = [('data', BYTE * byte_size)]

    datastruct = DATA_STRUCT()
    string = hanzi.strip().encode('gbk')
    string_length = len(string)
    if string_length > byte_size:
        string_length = byte_size
    for i in range(string_length):
        datastruct.data[i] = ord(string[i]) - 256

    return datastruct.data


def string_to_cbytearray(string, byte_size):

    class DATA_STRUCT(Structure):
        _fields_ = [('data', BYTE * byte_size)]

    datastruct = DATA_STRUCT()
    string = str(string).strip()
    for i in range(len(string)):
        datastruct.data[i] = ord(string[i])

    return datastruct.data


def string_to_cchararray(string, char_size):

    class DATA_STRUCT(Structure):
        _fields_ = [('data', c_char * byte_size)]

    datastruct = DATA_STRUCT()
    string = str(string).strip()
    for i in range(len(string)):
        datastruct.data[i] = ord(string[i])

    return datastruct.data


class Win32Environment:

    def __init__(self, scope):
        if not scope in ('user', 'system'):
            raise AssertionError
            self.scope = scope
            self.root = scope == 'user' and winreg.HKEY_CURRENT_USER
            self.subkey = 'Environment'
        else:
            self.root = winreg.HKEY_LOCAL_MACHINE
            self.subkey = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'

    def get_env_variable(self, name):
        """
        >>> system_env = Win32Environment("system")
        >>> system_env.get_env_variable("NUMBER_OF_PROCESSORS")
        """
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, name)
        except WindowsError as e:
            print e.message
            value = ''

        return value

    def set_env_variable(self, name, value):
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)


if __name__ == '__main__':
    print byte_array_to_mac_string(mac_string_to_byte_array('00:00:00:01:FE:68'))
    import doctest
    doctest.testmod()

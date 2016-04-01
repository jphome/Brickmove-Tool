#!/usr/bin/env python
# -*- coding=utf-8 -*-
#########################################################################
# File Name: common.py
# Author: jphome
# mail: jphome98@163.com
# Created Time: Sat 02 Apr 2016 01:26:17 AM CST
#########################################################################
import os
import sys
import locale
import time
import re
import socket
import struct
if 'win' in sys.platform:
    import _winreg
from ctypes import windll

def get_timestamp(format_string = '%Y%m%d%H%M%S', atime = 'Now'):
    if atime.strip().lower() == 'now':
        return time.strftime(format_string, time.localtime())
    else:
        return time.strftime(format_string, time.strptime(atime, '%Y%m%d%H%M%S'))


def get_ntp_server_time(server_add = ''):
    import ntplib
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request(server_add)
    timestamp = response.tx_time
    server_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    return server_time


def set_time_to_pc(server_time = None):
    timestamp = time.mktime(time.strptime(server_time, '%Y-%m-%d %H:%M:%S'))
    _date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
    _time = time.strftime('%X', time.localtime(timestamp))
    try:
        os.system('date {} && time {}'.format(_date, _time))
    except Exception as e:
        raise Exception(u'Set time to PC error! Error Message: %s.' % e.message)


def get_stability_capture_files(files_list, time_begin, time_after, file_type = '', event_type = ''):
    new_list = []
    time_begin = time.mktime(time.strptime(time_begin, '%Y-%m-%d %H:%M:%S'))
    time_after = time.mktime(time.strptime(time_after, '%Y-%m-%d %H:%M:%S'))
    for afile in files_list:
        file_name, file_ext = os.path.splitext(afile)
        if file_type != '':
            if event_type != '':
                if file_name[-len(event_type):] == event_type and file_type == file_ext:
                    if len(afile.split('_')) == 4:
                        file_time = afile.split('_')[2]
                        file_time = time.mktime(time.strptime(file_time, '%Y%m%d%H%M%S'))
                        if time_begin <= file_time <= time_after:
                            new_list.append(afile)
            elif file_type == file_ext:
                if len(afile.split('_')) == 4:
                    file_time = afile.split('_')[2]
                    file_time = time.mktime(time.strptime(file_time, '%Y%m%d%H%M%S'))
                    if time_begin <= file_time <= time_after:
                        new_list.append(afile)
        elif event_type != '':
            if file_name[-len(event_type):] == event_type:
                if len(afile.split('_')) == 4:
                    file_time = afile.split('_')[2]
                    file_time = time.mktime(time.strptime(file_time, '%Y%m%d%H%M%S'))
                    if time_begin <= file_time <= time_after:
                        new_list.append(afile)
        elif len(afile.split('_')) == 4:
            print afile.split('_')
            file_time = afile.split('_')[2]
            file_time = time.mktime(time.strptime(file_time, '%Y%m%d%H%M%S'))
            if time_begin <= file_time <= time_after:
                new_list.append(afile)

    return new_list


def check_name_of_files_list(files_list, ip, channel, file_type = '.jpg'):
    error_file_list = []
    print files_list
    if int(channel) < 10:
        channel = '0%s' % int(channel)
    else:
        channel = '%s' % channel
    for afile in files_list:
        if re.search('%s_%s_\\d+_\\w+%s' % (ip, channel, file_type), afile) is None:
            error_file_list.append(afile)
            print '*WARN* File %s name error!' % afile

    return error_file_list


def check_interval_of_files_list(files_list, interval, wucha):
    error_list = []
    if len(files_list) < 2:
        print u'*WARN* File number less than 2.'
        return
    for i in xrange(len(files_list) - 1):
        this_file = time.mktime(time.strptime(files_list[i].split('_')[2], '%Y%m%d%H%M%S'))
        next_file = time.mktime(time.strptime(files_list[i + 1].split('_')[2], '%Y%m%d%H%M%S'))
        max_time = interval + wucha
        min_time = interval - wucha
        if next_file - this_file > max_time or next_file - this_file < min_time:
            error_list.append((files_list[i], files_list[i + 1]))
            print '*WARN* %s ~ %s interval not between %s ~ %s.' % (files_list[i],
             files_list[i + 1],
             min_time,
             max_time)

    return error_list


def ping_strings_get_ping_cfg(strings = None):
    parameter_value_dict = {}
    rawstr = 'min/avg/max = (\\d+\\.?\\d{0,3})/(\\d+\\.?\\d{0,3})/(\\d+\\.?\\d{0,3})'
    ret = re.search(rawstr, strings)
    if ret is not None:
        parameter_value_dict['Minimum'] = ret.group(1)
        parameter_value_dict['Average'] = ret.group(2)
        parameter_value_dict['Maximum'] = ret.group(3)
    else:
        rawstr = 'Minimum = (\\d+\\.?\\d{0,3})ms, Maximum = (\\d+\\.?\\d{0,3})ms, Average = (\\d+\\.?\\d{0,3})ms'
        ret = re.search(rawstr, strings)
        if ret is not None:
            parameter_value_dict['Minimum'] = ret.group(1)
            parameter_value_dict['Average'] = ret.group(2)
            parameter_value_dict['Maximum'] = ret.group(3)
    rawstr = '\\d+ packets transmitted, \\d+ packets received, (\\d+\\.?\\d{0,3}%) packet loss'
    ret = re.search(rawstr, strings)
    if ret is not None:
        parameter_value_dict['Lost'] = ret.group(1)
    else:
        rawstr = 'Packets: Sent = \\d+, Received = \\d+, Lost = \\d+ \\((\\d+\\.?\\d{0,3}%) loss\\)'
        ret = re.search(rawstr, strings)
        if ret is not None:
            parameter_value_dict['Lost'] = ret.group(1)
    return parameter_value_dict


def get_local_ip():
    ip_list = socket.gethostbyname_ex(socket.gethostname())
    return ip_list[2]


def get_local_mac():
    mac = None
    lines = os.popen('ipconfig /all').readlines()
    conunt = 0
    if sys.platform == 'win32':
        for line in lines:
            if locale.getdefaultlocale()[0] == 'zh_CN':
                if '\xe6\x9c\xac\xe5\x9c\xb0\xe8\xbf\x9e\xe6\x8e\xa5' in line.decode('gbk').lstrip():
                    mac = lines[conunt + 4].split(':')[1].strip().replace('-', ':')
                    break
                elif locale.getdefaultlocale()[0] == 'en_US':
                    if line.lstrip().startswith('Physical Address'):
                        mac = line.split(':')[1].strip().replace('-', ':')
                        break
            conunt = conunt + 1

    return mac


def ip_string_to_ip_int(ip_string):
    return socket.ntohl(struct.unpack('I', socket.inet_aton(str(ip_string)))[0])


def ip_int_to_ip_string(ip_int = None):
    return socket.inet_ntoa(struct.pack('I', socket.htonl(ip_int)))


def ip_string_add_value(ip_string = None, interval = 1):
    ip_list = ip_string.split('.')
    result = len(ip_list) == 4 and len(filter(lambda x: x >= 0 and x <= 255, map(int, filter(lambda x: x.isdigit(), ip_list)))) == 4
    if result:
        ip_value = ip_string_to_ip_int(ip_string)
        ip_value += int(interval)
        return ip_int_to_ip_string(ip_value)
    else:
        print 'ip error'
        return False


def set_local_ip(ip = None, subnetmask = '255.255.255.0', gateway = None, dnsserver = None):
    if 'win' in sys.platform:
        net_cfg_instance_id = None
        hkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'System\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}')
        key_info = _winreg.QueryInfoKey(hkey)
        for index in range(key_info[0]):
            h_sub_key_name = _winreg.EnumKey(hkey, index)
            h_sub_key = _winreg.OpenKey(hkey, h_sub_key_name)
            try:
                h_ndi_inf_key = _winreg.OpenKey(h_sub_key, 'Ndi\\Interfaces')
                lower_range = _winreg.QueryValueEx(h_ndi_inf_key, 'LowerRange')
                if lower_range[0] == 'ethernet':
                    net_cfg_instance_id = _winreg.QueryValueEx(h_sub_key, 'NetCfgInstanceID')[0]
                    break
                _winreg.CloseKey(h_ndi_inf_key)
            except WindowsError:
                pass

            _winreg.CloseKey(h_sub_key)

        _winreg.CloseKey(hkey)
        if net_cfg_instance_id is None:
            print 'Not found NetworkInterfaceCard'
            return False
        str_key_name = 'System\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\\\' + net_cfg_instance_id
        hkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, str_key_name, 0, _winreg.KEY_WRITE)
        ip_address = []
        subnetmask_list = []
        gateway_list = []
        dns_server_list = []
        try:
            if ip:
                ip_address.append(ip)
                _winreg.SetValueEx(hkey, 'IPAddress', None, _winreg.REG_MULTI_SZ, ip_address)
            if subnetmask:
                subnetmask_list.append(subnetmask)
                _winreg.SetValueEx(hkey, 'SubnetMask', None, _winreg.REG_MULTI_SZ, subnetmask_list)
            if gateway:
                gateway_list.append(gateway)
                _winreg.SetValueEx(hkey, 'DefaultGateway', None, _winreg.REG_MULTI_SZ, gateway_list)
            if dns_server_list:
                dns_server_list.append(dnsserver)
                _winreg.SetValueEx(hkey, 'NameServer', None, _winreg.REG_SZ, ','.join(dns_server_list))
        except WindowsError:
            print 'Set IP Error'
            return False

        _winreg.CloseKey(hkey)
        dhcp_notify_config_change = windll.dhcpcsvc.DhcpNotifyConfigChange
        dhcp_notify_config_change(None, net_cfg_instance_id, True, 0, struct.unpack('I', socket.inet_aton(str(ip_address[0])))[0], struct.unpack('I', socket.inet_aton(str(subnetmask_list[0])))[0], 0)
        return True
    elif 'linux' in sys.platform:
        print '**WARN**linux does not support set_local_ip!'
        return False
    else:
        return


def get_keys_of_dictionary(dictionary = None, value = '', separate = '/'):
    keys = dictionary.keys()
    key_list = []
    for key in keys:
        if value in dictionary[key].split(separate):
            key_list.append(key)

    return key_list


def get_values_of_dictionary(dictionary = None, key = '', separate = '/'):
    keys = dictionary.keys()
    if key in keys:
        return dictionary[key].split(separate)
    raise Exception(u'Key:%s input error!')


def _netsdk_get_diction_value(dict_name, key):
    return_value = dict_name.get(key) if dict_name.get(key) is not None else int(key)
    return return_value


def cli_get_lastest_file(output, file_type = ''):
    output_list = output.split('\r')
    print output_list
    if len(output_list) == 0:
        raise Exception(u'%s is empty' % output)
    else:
        for i in range(len(output_list)):
            pattern = '^-.*:\\d\\d\\s(.*)'
            result = re.findall(pattern, output_list[i].replace('\n', ''))
            if len(result) != 0:
                if file_type == '':
                    return result[0]
                if result[0].endswith(file_type):
                    return result[0]

    raise Exception(u'file of %s is not on dir' % file_type)


def cli_get_filename_on_dir(output, file_type = ''):
    output_list = output.split('\r')
    target_list = []
    print output_list
    if len(output_list) == 0:
        raise Exception(u'%s is empty' % output)
    else:
        for i in range(len(output_list)):
            pattern = '^-.*:\\d\\d\\s(.*)'
            result = re.findall(pattern, output_list[i].replace('\n', ''))
            if len(result) != 0:
                if file_type == '':
                    target_list.append(result[0])
                elif result[0].endswith(file_type):
                    target_list.append(result[0])

    if len(target_list) == 0:
        raise Exception(u'file of %s is not on dir' % file_type)
    else:
        return target_list


def parse_dspstatus6_text(input_str, key_str = ''):
    input_str = str(input_str).strip().strip('\\#').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    if key_str == '':
        return _get_all_fields_value(input_str)
    else:
        return _get_field_value(input_str, key_str)


def list_to_string(input_list, character = ','):
    if isinstance(input_list, list):
        str_list = []
        for i in input_list:
            str_list.append(str(i))

        return character.join(str_list)
    else:
        return input_list


def _get_all_fields_value(input_str):
    deccheak_status_dic = {}
    check_err_list = []
    if len(input_str) == 0:
        raise Exception(u'%s is empty' % input_str)
    else:
        dec_mode_dic = {}
        dic_str_list = ['Dec_mode',
         'Pack_type',
         'hik_flag',
         'Dec_bps',
         'auido_type',
         'auido_fps',
         'sample_rate',
         'bit_rate',
         'audio_frm']
        dec_mode_dic = _get_deccheak_dic(input_str, '(\\d*:(.*))\\s*-*\\s*Chan\\s*video', '\\d*:\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)', dic_str_list)
        video_type = {}
        dic_str_list = ['video_type',
         'video_fps',
         'dec_wide',
         'dec_high',
         'dec_2field',
         'time_offset',
         'video_frm',
         'i_frm',
         'p_frm',
         'b_frm']
        video_type = _get_deccheak_dic(input_str, 'Frm\\s*Frm\\s*-*\\s*(\\d*:(.*))\\s*-*\\s*Chan\\s*rec\\s*rec', '\\s*\\d*:\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)', dic_str_list)
        rec_data = {}
        dic_str_list = ['rec_data',
         'rec_invdata',
         'dec_data',
         'config_cnt',
         'erri_cnt',
         'erri_ret',
         'errp_cnt',
         'errp_ret',
         'errb_cnt',
         'errb_ret',
         'err_afrm',
         'err_aret',
         'err_mode',
         'err_ret']
        rec_data = _get_deccheak_dic(input_str, 'mode\\s*Ret\\s*--*\\s*(\\d*:(.*))\\s*-*\\s*&&*\\sCheck', '\\s*\\d*:\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)', dic_str_list)
        items_dic = {}
        for i in range(len(rec_data)):
            key = i
            items_dic = dec_mode_dic[key]
            items_dic.update(video_type[key])
            items_dic.update(rec_data[key])
            deccheak_status_dic.update({i: items_dic})
            items_dic = {}

        check_err_pattern = 'chan:\\s*(\\d*.*)\\,\\s*-'
        check_err_str = re.findall(check_err_pattern, input_str, re.DOTALL)
        check_err_list = check_err_str[0].split(',  - Error chan:')
        check_err_chan_dic = {}
        check_err_chan_list = []
        for i in range(len(check_err_list)):
            tmp_value_pattern = '\\]\\s*(\\w*)'
            check_err_chan_list = re.findall(tmp_value_pattern, check_err_list[i].replace('-\\s*', '').replace('\\s', '').strip(), re.S)
            check_err_chan_dic.update({i: check_err_chan_list})

        check_time_pattern = 'min\\s*sec\\s*(.*)\\s*--'
        check_time_str = re.findall(check_time_pattern, input_str, re.DOTALL)
        check_time_list = check_time_str[0].replace('-', '')
        check_tmp_pattern = '\\d*:\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)\\s*(\\w*)'
        check_tmp_list = re.findall(check_tmp_pattern, check_time_list, re.DOTALL)
        check_time_dic = {}
        check_time_chan_dic = {}
        for i in range(len(check_tmp_list)):
            check_time_dic = dict(start_year=check_tmp_list[i][0], start_month=check_tmp_list[0][1], start_day=check_tmp_list[0][2], start_min=check_tmp_list[0][3], start_sec=check_tmp_list[0][4], end_year=check_tmp_list[0][5], end_month=check_tmp_list[0][6], end_day=check_tmp_list[0][7], end_min=check_tmp_list[0][8], end_sec=check_tmp_list[0][9])
            check_time_chan_dic.update({i: check_time_dic})

        errorinfo_pattern = ''
        if 'dspstatus 10' in input_str:
            errorinfo_pattern = 'second\\s*\\w*:\\d*(-.*)'
        else:
            errorinfo_pattern = 'second\\s*(-.*)'
        errorinfos_str = re.findall(errorinfo_pattern, input_str, re.DOTALL)
        errorinfos_list = errorinfos_str[0].split('-Error I Gloable Time-')
        i_chan_dic = {}
        p_chan_dic = {}
        b_chan_dic = {}
        audio_chan_dic = {}
        del errorinfos_list[0]
        for i in range(len(errorinfos_list)):
            errorinfos_str = str(errorinfos_list[i])
            i_dic = _get_gloable_time_dic(errorinfos_str, '', '-Error P Gloable Time')
            i_chan_dic.update({i: i_dic})
            p_dic = _get_gloable_time_dic(errorinfos_str, 'P Gloable Time-', '-Error B Gloable Time')
            p_chan_dic.update({i: p_dic})
            b_dic = _get_gloable_time_dic(errorinfos_str, 'B Gloable Time-', '-Error Audio Gloable Time')
            b_chan_dic.update({i: b_dic})
            audio_dic = _get_gloable_time_dic(errorinfos_str, 'Audio Gloable Time-', '')
            audio_chan_dic.update({i: audio_dic})

        dspstatus_info_dic = dict(deccheak_status=deccheak_status_dic, check_error_curbuf_status=check_err_chan_dic, check_time=check_time_chan_dic, error_i_gloable_time=i_chan_dic, error_p_gloable_time=p_chan_dic, error_b_gloable_time=b_chan_dic, error_audio_gloable_time=audio_chan_dic)
        return dspstatus_info_dic


def _get_deccheak_dic(input_str, deccheak_val_decmode_pattern, decmode_tmp_pattern, dic_str_list):
    decmode_chan_dic = {}
    deccheak_val_decmode_str = re.findall(deccheak_val_decmode_pattern, input_str, re.S)
    deccheak_val_decmode_value = deccheak_val_decmode_str[0][0].replace('-', '').strip()
    deccheak_val_decmode_list = re.findall(decmode_tmp_pattern, deccheak_val_decmode_value, re.DOTALL)
    for i in range(len(deccheak_val_decmode_list)):
        deccheak_val_decmode_dic = {}
        for j in range(len(dic_str_list)):
            deccheak_val_decmode_dic.update({dic_str_list[j]: deccheak_val_decmode_list[i][j]})

        decmode_chan_dic.update({i: deccheak_val_decmode_dic})

    return decmode_chan_dic


def _get_gloable_time_dic(input_str, begin_flag, end_flag):
    begin_flag = begin_flag.replace(' ', '\\s')
    end_flag = end_flag.replace(' ', '\\s')
    if len(input_str) == 0:
        raise Exception(u'%s is empty' % input_str)
    else:
        i_time_dic = {}
        i_time_item_dic = {}
        i_time_pattern = begin_flag + '(.*)\\s*' + end_flag
        i_time_tmp_list = re.findall(i_time_pattern, input_str, re.DOTALL)
        i_time_list = i_time_tmp_list[0]
        itime_value_pattern = '\\d*:\\s*(\\d*)\\s*(\\d*)\\s*(\\d*)\\s*(\\d*)\\s*(\\d*)'
        tmp_value = re.findall(itime_value_pattern, i_time_list, re.S)
        for i in range(len(tmp_value)):
            i_time_item_dic.update({'year': tmp_value[i][0],
             'month': tmp_value[i][1],
             'day': tmp_value[i][2],
             'minute': tmp_value[i][3],
             'second': tmp_value[i][4]})
            i_time_dic.update({i: i_time_item_dic})
            i_time_item_dic = {}

    return i_time_dic


def _get_field_value(input_str, key_str):
    result_value = ''
    dspstatus_info_dic = _get_all_fields_value(input_str)
    if len(dspstatus_info_dic) == 0:
        raise Exception(u'the dic %s is empty' % dspstatus_info_dic)
    else:
        for k, v in dspstatus_info_dic.iteritems():
            if k == key_str:
                result_value = v

    if result_value == '':
        raise Exception(u'the key string %s is not in Dic' % key_str)
    else:
        return result_value


class _VideoResolution:
    video_resolution = [(0, u'528*384/528*320', u'DCIF'),
     (1, u'352*288/352*240', u'CIF'),
     (2, u'176*144/176*120', u'QCIF'),
     (3, u'704*576/704*480', u'4CIF'),
     (4, u'704*288/704*240', u'2CIF'),
     (6, u'320*240', u'QVGA'),
     (7, u'160*120', u'QQVGA'),
     (12, u'384*288', u'384*288'),
     (13, u'576*576', u'576*576'),
     (16, u'640*480', u'VGA'),
     (17, u'1600*1200', u'UXGA'),
     (18, u'800*600', u'SVGA'),
     (19, u'1280*720', u'HD720P'),
     (19, u'1280*720', u'720P'),
     (20, u'1280*960', u'XVGA'),
     (20, u'1280*960', u'HD960P'),
     (20, u'1280*960', u'960P'),
     (21, u'1600*900', u'HD900P'),
     (22, u'1360*1024', u'SXGAp'),
     (23, u'1536*1536', u'1536*1536'),
     (24, u'1920*1920', u'1920*1920'),
     (27, u'1920*1080', u'1920*1080'),
     (27, u'1920*1080', u'HD1080P'),
     (27, u'1920*1080', u'1080P'),
     (27, u'1920*1080', u'1920*1080p'),
     (28, u'2560*1920', u'2560*1920'),
     (29, u'1600*304', u'1600*304'),
     (30, u'2048*1536', u'2048*1536'),
     (31, u'2448*2048', u'2448*2048'),
     (32, u'2448*1200', u'2448*1200'),
     (33, u'2448*800', u'2448*800'),
     (34, u'1024*768', u'XGA'),
     (35, u'1280*1024', u'SXGA'),
     (36, u'960*576/960*480', u'WD1'),
     (37, u'1920*1080', u'1080i'),
     (38, u'1440*900', u'WXGA'),
     (39, u'1920*1080/1280*720', u'HD_F'),
     (40, u'1920*540/1280*360', u'HD_H'),
     (41, u'960*540/630*360', u'HD_Q'),
     (42, u'2336*1744', u'2336*1744'),
     (43, u'1920*1456', u'1920*1456'),
     (44, u'2592*2048', u'2592*2048'),
     (45, u'3296*2472', u'3296*2472'),
     (46, u'1376*768', u'1376*768'),
     (47, u'1366*768', u'1366*768'),
     (48, u'1360*768', u'1360*768'),
     (49, u'1680*1050', u'WSXGA'),
     (50, u'720*720', u'720*720'),
     (51, u'1280*1280', u'1280*1280'),
     (52, u'2048*768', u'2048*768'),
     (53, u'2048*2048', u'2048*2048'),
     (54, u'2560*2048', u'2560*2048'),
     (55, u'3072*2048', u'3072*2048'),
     (56, u'2304*1296', u'2304*1296'),
     (57, u'1280*800', u'WXGA'),
     (58, u'1600*600', u'1600*600'),
     (59, u'1600*900', u'1600*900'),
     (60, u'2752*2208', u'2752*2208'),
     (62, u'4000*3000', u'4000*3000'),
     (63, u'4096*2160', u'4096*2160'),
     (64, u'3840*2160', u'3840*2160'),
     (65, u'4000*2250', u'4000*2250'),
     (66, u'3072*1728', u'3072*1728'),
     (67, u'2592*1944', u'2592*1944'),
     (68, u'2464*1520', u'2464*1520'),
     (69, u'1280*1920', u'1280*1920'),
     (70, u'2560*1440', u'2560*1440'),
     (71, u'2560*1440', u'2560*1440'),
     (72, u'160*128', u'160*128'),
     (73, u'324*240', u'324*240'),
     (74, u'324*256', u'324*256'),
     (75, u'336*256', u'336*256'),
     (76, u'640*512', u'640*512'),
     (77, u'2720*2048', u'2720*2048'),
     (78, u'384*256', u'384*256'),
     (79, u'384*216', u'384*216'),
     (80, u'320*256', u'320*256'),
     (81, u'320*180', u'320*180'),
     (82, u'320*192', u'320*192'),
     (83, u'512*384', u'512*384'),
     (84, u'352*256', u'352*256'),
     (85, u'256*192', u'256*192'),
     (86, u'640*360', u'640*360'),
     (91, u'1920*1200', u'1920*1200'),
     (96, u'2560*2660', u'2560*2660'),
     (97, u'2688*1536', u'2688*1536'),
     (98, u'2688*1520', u'2688*1520'),
     (99, u'3072*3072', u'3072*3072'),
     (104, u'704*1056', u'704*1056'),
     (105, u'352*528', u'352*528'),
     (110, u'4000*3072', u'4000*3072'),
     (116, u'3840*1680', u'3840*1680'),
     (118, u'704*320', u'704*320'),
     (124, u'4096*1800', u'4096*1800'),
     (125, u'1280*560', u'1280*560'),
     (132, u'2720*1192', u'2720*1192'),
     (255, u'Auto', u'Auto')]

    def __init__(self):
        self.video_resolution_list = []
        for res in self.video_resolution:
            one_resolution = {}
            one_resolution['index'] = res[0]
            one_resolution['resolution'] = str(res[1]).split('/')
            one_resolution['description'] = str(res[2]).upper().split('/')
            self.video_resolution_list.append(one_resolution)

    def _index_exist(self, index):
        for video_resolution in self.video_resolution_list:
            if video_resolution['index'] == index:
                return video_resolution

    def get_all_by_index(self, index):
        one_res = self._index_exist(index)
        if one_res is not None:
            return one_res
        else:
            return


def get_video_resolution_by_description(description):
    res = _VideoResolution()
    for video_resolution in res.video_resolution_list:
        if description.upper() in video_resolution['description']:
            return video_resolution['resolution']


def get_video_description_by_resolution(resolution):
    res = _VideoResolution()
    description_list = []
    for video_resolution in res.video_resolution_list:
        if resolution.upper() in video_resolution['resolution']:
            description_list.extend(video_resolution['description'])

    if len(description_list) == 0:
        return
    return list(set(description_list))


def get_video_description_by_index(index):
    res = _VideoResolution()
    index = int(index)
    for idx, resolution, descript in res.video_resolution:
        if idx == index:
            description = descript
            break
        else:
            description = index

    return description


def get_video_index_by_description(description):
    res = _VideoResolution()
    tag = 0
    for idx, resolution, descript in res.video_resolution:
        if cmp(descript.upper(), description.upper()) == 0:
            index = idx
            tag = 1
            break

    if tag == 0:
        print u'*WARN* Not support the resolution %s' % description
        index = description
    return index


def video_resolution_match(*video_resolution):
    if len(video_resolution) < 2 or len(video_resolution) > 3:
        raise Exception(u'Parameter num wrong')
    index = None
    resolutions = []
    for item in video_resolution:
        if re.compile('^\\d+$').match(str(item)):
            index = int(item)
        elif str(item) == '0xff':
            index = int('0xff', 16)
        else:
            resolutions.append(str(item).upper())

    res = _VideoResolution()
    if index is not None:
        all_info = res.get_all_by_index(index)
        if all_info is None:
            raise Exception(u'Index not exist')
        if len(resolutions) == 1:
            if resolutions[0] not in all_info['resolution'] and resolutions[0] not in all_info['description']:
                raise Exception(u'Resolution not match')
            return
        if len(resolutions) == 2:
            first_resolution_match = False
            second_resolution_match = False
            if resolutions[0] in all_info['resolution'] and resolutions[1] in all_info['description']:
                first_resolution_match = True
            if resolutions[1] in all_info['resolution'] and resolutions[0] in all_info['description']:
                second_resolution_match = True
            if not (first_resolution_match or second_resolution_match):
                raise Exception(u'Resolution not match')
            return
    resolution_list = get_video_description_by_resolution(resolutions[0])
    if resolution_list is not None and resolutions[1] in resolution_list:
        return
    else:
        description_list = get_video_resolution_by_description(resolutions[0])
        if description_list is not None and resolutions[1] in description_list:
            return
        raise Exception(u'Resolution not match')
        return


def log_gbk(message, level = 'INFO', html = False, console = False):
    from robot.libraries import BuiltIn
    buildin = BuiltIn.BuiltIn()
    buildin.log(message.decode('gbk'), level=level, html=html, console=console)


def get_default_hita_output_path():
    from settings import HITA_OUTPUT_PATH
    return HITA_OUTPUT_PATH


def get_default_log_path():
    from settings import LOG_PATH
    return LOG_PATH


def get_default_picture_path():
    from settings import Picture_PATH
    return Picture_PATH


def get_default_video_path():
    from settings import Video_PATH
    return Video_PATH


def set_string_decode(string, encoding = 'utf-8'):
    return string.decode(encoding, 'replace')


def get_string_form_list(input_list, *parameter):
    if not isinstance(input_list, list):
        print 'The input_list is not a list ,is ', type(input_list)
        return ''
    re_str = '\\S*'.join(parameter)
    for item in input_list:
        pattern = re.compile('\\S*' + re_str + '\\S*', re.I)
        if_match = False
        if pattern.match(item):
            return item

    print 'Can not match: ', input_list, parameter
    return ''

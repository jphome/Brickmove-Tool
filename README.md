## Brickmove-Tool项目介绍
搬砖神器，何为搬砖神器，即别人一次搬十块砖，用了这个工具，力能扛鼎，一次搬一百块不是梦，比元邦效果还好。
<br/>
哈哈哈，玩笑话，此为基于PyQt4.9.4 GUI开发平台使用Python2.7开发的一款针对海康威视前端设备（暂时only支持IPC、IPD）的搜索、批量配置工具。

### 版权说明
开放的源码为本人撰写，License参照LICENSE文件，欢迎参考or抄袭，谢谢。
<br/>
海康的开放sdk库（dll）由于比较大，没有上传，可至[海康威视官网](http://www.hikvision.com/cn/download_61.html)下载最新版本。
<br/>
sdk文件部分python字节码代码，功能类比于Android中的jni，用于承接C++&Python，站在巨人肩膀上得来，不好意思开放源码，感兴趣者请搜索Easy Python Decompiler，一般人我不告诉他。

### Usage
* 工程商等小白用户，扫码关注微信公众号（or搜索“天王盖地虎”），回复“搬砖神器”即获得绿色软件包下载地址
<pre>
软件纯天然绿色无污染，无须安装，即下即用，不定时更新加入新颖实用功能；but请注意，不要放到中文文件夹中使用哦，会起不来。。。
</pre>
* 动手能力比较强的朋友
<pre>
step1 安装python-2.7.5.msi
step2 安装pywin32-218.win32-py2.7.exe
step3 安装PyQt-Py2.7-x86-gpl-4.9.4-1.exe
step4 安装setuptools-1.1.5.tar.gz
step5 安装PyInstaller-2.1.tar.gz
step6 环境变量确认 PATH C:\Python27\Scripts;C:\Python27;C:\Python27\Lib\site-packages\PyQt4;
step7 down代码，编辑ui文件，撰写python代码，执行使用
</pre>

### 功能说明
* 已实现功能
	- 20160404 多线程实现在线设备异步搜索、设备预览、设备osd信息读取&设置、设备osd信息批量读取
* TODO
	- 设备IP地址配置、设备激活、设备osd配置规则功能实现

![gui](https://github.com/jphome/Brickmove-Tool/blob/master/gui.jpg)
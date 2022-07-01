# patching IPM IPAi Tool by Hans Kim, 2022-03-12
# enable SSH in Device // enableSSH
#  Connet sftp
#  create /mnt/plugin/crpt
#  write a file /mnt/plugin/crpt/post_script.sh
#  copy file "mk_ct_report.cgi" to "/mnt/plugin/crpt/"

#  copy file countreport.cgi to "/mnt/plugin/crpt/"
#  make directory "/root/web/cgi/bin/operator/"
#  ln -s /mnt/plugin/crpt/countreport.cgi  /root/web/cgi/bin/operator/countreport.cgi


import os, time, sys
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64, re
import paramiko
import tkinter as tk
from tkinter import ttk

PHP_CGI = '/usr/bin/php-cgi -q '


absdir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(absdir)
print (absdir)

# view SSH
# http://192.168.132.6/cgi-bin/admin/security.cgi?msubmenu=service&action=view
# enable SSH
# http://192.168.1.136/cgi-bin/admin/security.cgi?msubmenu=service&action=apply&support_ssh=1

server = "192.168.1.136"
user ="root"
httppw = "Rootpass12345"
sshpw = "cpro0109"
dest_dir = "/mnt/plugin/patch"

# tm = time.localtime()
# print (tm)
# print (tm.tm_year,  type(tm.tm_year))
# time.strftime('%Y%m%d%H%M')
# d_str = time.strftime("year=%Y&mon=%m&day=%d&hour=%H&min=%M&sec=%S")
# print(d_str)
# sys.exit()

prog_state = 0
prog_step  = 100

def sshcmd(ssh, str):
    stdin, stdout, stderr = ssh.exec_command(str)
    lines = stdout.readlines()
    return (''.join(lines))

def mklink(ssh, src, dest):
    ex = dest.split('/')
    fn = ex.pop()
    x = sshcmd(ssh, "ls -al " + '/'.join(ex) + " |grep " + fn + " |awk '{print $9}'")
    if not x:
        sshcmd(ssh, 'ln -s ' + src + ' ' + dest )

def checkAuthMode(url, rootid, rootpw):
    r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPDigestAuth(rootid, rootpw))
    if r.text.find('Unauthorized') < 0:
        return HTTPDigestAuth(rootid, rootpw)
    
    r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPBasicAuth(rootid, rootpw))
    if r.text.find('Unauthorized') <0:
        return HTTPBasicAuth(rootid, rootpw)
    
    return False

def enableSSH(dev_ip, rootpw):
    arr_auth = [HTTPDigestAuth('root', rootpw), HTTPBasicAuth('root', rootpw)]
    for authkey in arr_auth:
        for i in range(2):
            r = requests.get('http://' + dev_ip +'/cgi-bin/admin/security.cgi?msubmenu=service&action=view', auth=authkey)
            if r.text.find('support_ssh=1') >=0:
                return True

            r = requests.get('http://' + dev_ip + '/cgi-bin/admin/security.cgi?msubmenu=service&action=apply&support_ssh=1', auth=authkey)
            time.sleep(1)

    return False

def setDatetime(ssh):
    gmt =20, # timezone : gmt 20
    sshcmd(ssh, PHP_CGI + '/root/web/cgi-bin/admin/system.cgi "msubmenu=timezone&action=apply&gmt=%d"' %gmt)
    progress(1)
    # /cgi-bin/admin/system.cgi?msubmenu=datetime&action=apply&sync_type=1&year=2022&mon=3&day=14&hour=16&min=29&sec=48
    d_str = time.strftime("year=%Y&mon=%m&day=%d&hour=%H&min=%M&sec=%S")
    x = sshcmd(ssh, PHP_CGI + '/root/web/cgi-bin/admin/system.cgi  "msubmenu=datetime&action=apply&sync_type=1&%s"'  %d_str)
    progress(2)
    if x.find('NG') >0:
        return False
    return True
    
# dest_dir = "/mnt/plugin/patch/"
# ex = dest_dir.split("/")
# d = ex.pop()
# d = ex.pop()
# ld = "/".join(ex)

# print(d)
# print(ld)
# sys.exit()

def mkRemoteDir(ssh):
    arr_dir = [
        dest_dir,
        "/root/web/cgi-bin/operator",
        "/mnt/plugin/vca/web/www/counting_report",
        "/mnt/plugin/vca/web/www/hosted_service"
    ]
    for dir in arr_dir:
        ex = dir.split("/")
        d = ex.pop()
        ld = "/".join(ex)
        ex_str = "ls -al %s |grep ^d |awk '{print $9}'" %ld
        print(ex_str)
        x = sshcmd(ssh, ex_str)
        if x.find(d) < 0:
            showMessage ("create directory: %s" %dir)
            sshcmd(ssh, "mkdir %s" %dir)
        progress(2)

def addRemoteWebMenu(ssh):
    flag = False
    cwd = os.getcwd()
    sftp = ssh.open_sftp()
    sftp.get("/etc/init.d/make_plugin_info.sh", "%s/make_plugin_info.sh" %cwd)
    
    with open("%s/make_plugin_info.sh" %cwd, "r") as f:
        body =  f.read()
    if body.find("<submenuname>counting_report") <0 :
        flag = True
        with open("%s/make_plugin_info.sh" %cwd, "a") as f:
            f.write("""\nsed -i'' -r -e "/<submenuname>advanced/i\<submenuname>counting_report</submenuname>\\n<cgi>/cgi-bin/admin/vca/counting_report/setup_vca_crpt.cgi</cgi>" /tmp/plugin/plugin_info_list.xml""")

        sshcmd(ssh, """sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>counting_report</submenuname>\\n<cgi>/cgi-bin/admin/vca/counting_report/setup_vca_crpt.cgi</cgi>" /tmp/plugin/plugin_info_list.xml""")

    if body.find("<submenuname>hosted_service") <0 :
        flag = True
        with open("%s/make_plugin_info.sh" %cwd, "a") as f:
            f.write("""\nsed -i'' -r -e "/<submenuname>advanced/i\<submenuname>hosted_service</submenuname>\\n<cgi>/cgi-bin/admin/vca/hosted_service/setup_vca_hosted_service.cgi</cgi>" /tmp/plugin/plugin_info_list.xml""")
        
        sshcmd(ssh, """sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>hosted_service</submenuname>\\n<cgi>/cgi-bin/admin/vca/hosted_service/setup_vca_hosted_service.cgi</cgi>" /tmp/plugin/plugin_info_list.xml""")

    if flag:
        print ("uploading")
        x = sshcmd(ssh, "mv /etc/init.d/make_plugin_info.sh /etc/init.d/make_plugin_info.sh.bk")
        sftp.put("%s/make_plugin_info.sh" %cwd, "/etc/init.d/make_plugin_info.sh")
    sftp.close()
    sshcmd(ssh, "tr -d '\015' < /etc/init.d/make_plugin_info.sh > /tmp/make_plugin_info.tr.sh")
    sshcmd(ssh, "mv /tmp/make_plugin_info.tr.sh  /etc/init.d/make_plugin_info.sh")
    sshcmd(ssh, "chmod 755 /etc/init.d/make_plugin_info.sh")




def patchBin(ssh):
    # 1. add menu to /tmp/plugin/plugin_info_list.xml, origin is /mnt/plugin/vca/info.dat
    # 2. mkdir /root/web/cgi-bin/vca/counting_report
    # 3. copy files to /mnt/plugin/crpt/
    # 4. symbolic link to /root/cgi-bin/operator and /
    IP_addr = devEntry.get()
    cwd = os.getcwd()

    # check directories
    mkRemoteDir(ssh)

    arr_file = [
        "post_startup.sh", 
        "mk_ct_report.cgi",
        "countreport.php",
        "param.php",
        "tlss.cgi",
        "setup_vca_crpt.php",
        "setup_vca_hosted_service.php"
    ]

    for file in arr_file :
        if os.path.isfile("%s/src/%s" %(cwd, file) ):
            showMessage ("%s/src/%s exist, OK" %(cwd, file))
        else :
            showMessage("%s/src/%s NOT exist, FAIL" %(cwd, file), "error")
            return False

    # copy files to /mnt/plugin/patch/
    if not os.path.isdir("%s/bk/%s/" %(cwd, IP_addr)) :
        os.makedirs("%s/bk/%s/" %(cwd, IP_addr))

    sftp = ssh.open_sftp()
    for file in arr_file:
        showMessage("uploading file: %s" %file)
        x = sshcmd(ssh, "ls -al %s/%s | awk '{print $9}'" %(dest_dir, file))
        if x :
            sftp.get("%s/%s" %(dest_dir, file), "%s/bk/%s/%s_%s" %(cwd, IP_addr, str(time.strftime('%Y%m%d%H%M')),file))
            x = sshcmd(ssh, "mv %s/%s %s/%s.bk" %(dest_dir, file, dest_dir, file))
        sftp.put("%s/src/%s" %(cwd, file), "%s/%s" %(dest_dir, file))
        progress(1)
    
    sftp.close()

    sshcmd(ssh, "tr -d '\015' < %s/post_startup.sh > /tmp/post_startup.tr.sh" %dest_dir)
    sshcmd(ssh, " mv /tmp/post_startup.tr.sh %s/post_startup.sh" %dest_dir)
    sshcmd(ssh, "chmod 755 %s/post_startup.sh" %dest_dir)

    # # create symbolic links
    links = [
        ("%s/countreport.php" %dest_dir,             "/root/web/cgi-bin/operator/countreport.cgi"),
        ("%s/param.php" %dest_dir,                   "/root/web/cgi-bin/operator/param.cgi"),
        ("%s/snapshot.php" %dest_dir,                "/root/web/cgi-bin/operator/snapshot.cgi"),
        ("%s/metadata.php" %dest_dir,                "/root/web/cgi-bin/operator/metadata.cgi"),
        ("%s/setup_vca_crpt.php" %dest_dir,          "/mnt/plugin/vca/web/www/counting_report/setup_vca_crpt.cgi"),
        ("%s/setup_vca_hosted_service.php" %dest_dir,"/mnt/plugin/vca/web/www/hosted_service/setup_vca_hosted_service.cgi"),
    ]        
    for src, dst in links:
        mklink(ssh, src, dst)

    addRemoteWebMenu(ssh)
    progress(2)
    showMessage("Patching counting report complete!!")
    progress(2)

    return True

def patchBinXX(ssh):
    # 1. add menu to /tmp/plugin/plugin_info_list.xml, origin is /mnt/plugin/vca/info.dat
    # 2. mkdir /root/web/cgi-bin/vca/counting_report
    # 3. copy files to /mnt/plugin/crpt/
    # 4. symbolic link to /root/cgi-bin/operator and /

    cwd = os.getcwd()
    arr_file = [
        {"name": "post_startup.sh",             "path": "/mnt/plugin/crpt/"},
        {"name": "mk_ct_report.cgi",            "path": "/mnt/plugin/crpt/"},
        {"name": "countreport.cgi",             "path": "/mnt/plugin/crpt/"},
        {"name": "param.cgi",                   "path": "/mnt/plugin/crpt/"},
        {"name": "tlss.cgi",                    "path": "/mnt/plugin/crpt/"},
        {"name": "setup_operator.cgi",          "path": "/mnt/plugin/crpt/"},
        {"name": "crpt.ini",                    "path": "/mnt/plugin/crpt/"},
        {"name": "tlss.ini",                    "path": "/mnt/plugin/crpt/"},
        {"name": "setup_vca_crpt.cgi",          "path": "/mnt/plugin/crpt/"},
        {"name": "setup_vca_hosted_service.cgi","path": "/mnt/plugin/crpt/"},
    ]

    for file in arr_file :
        if os.path.isfile(cwd + "/src/" + file['name'] ):
            showMessage (cwd + "/src/" + file['name'] +" exist, OK")
        else :
            showMessage(cwd + "/src/" + file['name'] +" not exist, Fail", "error")
            return False

    x = sshcmd(ssh,"ls -al /mnt/plugin/ |grep ^d |awk '{print $9}'")
    if x.find("crpt") < 0:
        print ("create directory: /mnt/plugin/crpt")
        sshcmd(ssh, "mkdir /mnt/plugin/crpt")
    progress(2)

    x = sshcmd(ssh, "ls -al /root/web/cgi-bin/ |grep ^d |awk '{print $9}'")
    if x.find("operator") < 0:
        print ("create directory: /root/web/cgi-bin/operator")
        sshcmd(ssh, "mkdir /root/web/cgi-bin/operator")
    progress(2)

    # files: countreport.cgi, mk_ct_report.cgi, post_startup.sh
    sftp = ssh.open_sftp()
    for file in arr_file:
        showMessage("uploading file: " + file['path'] + file['name'])
        x = sshcmd(ssh, "ls -al " + file['path'] + file['name'] + " | awk '{print $9}'")
        if x :
            sftp.get(file['path'] + file['name'], cwd + "/src/bk/" + str(time.strftime('%Y%m%d%H%M')) + "_" + file['name'])
            x = sshcmd(ssh, "mv " + file['path'] + file['name'] + " " + file['path'] + file['name'] + ".bk")
        sftp.put(cwd + "/src/" + file['name'], file['path'] + file['name'] )
        progress(1)
    
    sftp.close()

    sshcmd(ssh, "tr -d '\015' < /mnt/plugin/crpt/post_startup.sh > /mnt/plugin/crpt/post_startup.tr.sh")
    sshcmd(ssh, " mv /mnt/plugin/crpt/post_startup.tr.sh /mnt/plugin/crpt/post_startup.sh")
    sshcmd(ssh, "chmod 755 /mnt/plugin/crpt/post_startup.sh")

    links = [
        ("/mnt/plugin/crpt/countreport.cgi",    "/root/web/cgi-bin/operator/countreport.cgi"),
        ("/mnt/plugin/crpt/param.cgi",          "/root/web/cgi-bin/operator/param.cgi"),
        ("/mnt/plugin/crpt/setup_operator.cgi", "/root/web/cgi-bin/operator/setup_operator.cgi"),
    ]        
    for src, dst in links:
        mklink(ssh, src, dst)

    # x = sshcmd(ssh, "ls -al /root/web/cgi-bin/operator |grep countreport.cgi |awk '{print $9}'")
    # if not x:
    #     sshcmd(ssh, 'ln -s /mnt/plugin/crpt/countreport.cgi /root/web/cgi-bin/operator/countreport.cgi')
    
    # x = sshcmd(ssh, "ls -al /root/web/cgi-bin/operator |grep param.cgi |awk '{print $9}'")
    # if not x:
    #     sshcmd(ssh, 'ln -s /mnt/plugin/crpt/param.cgi /root/web/cgi-bin/operator/param.cgi')

    # x = sshcmd(ssh, "ls -al /root/web/cgi-bin/operator |grep setup_operator.cgi |awk '{print $9}'")
    # if not x:
    #     sshcmd(ssh, 'ln -s /mnt/plugin/crpt/setup_operator.cgi /root/web/cgi-bin/operator/setup_operator.cgi')

    x = sshcmd(ssh, "ls -al /root/web/cgi-bin/operator |grep snapshot.cgi |awk '{print $9}'")
    if not x:
        sshcmd(ssh, """sed "s/_define.inc/\/root\/web\/cgi-bin\/_define.inc/g" /root/web/cgi-bin/video.cgi >> /tmp/tmp""")
        sshcmd(ssh, """sed "s/.\/class/\/root\/web\/cgi-bin\/class/g" /tmp/tmp > /root/web/cgi-bin/operator/snapshot.cgi""")

    showMessage("Patching counting report complete!!")
    progress(2)
    return True


def addLangToMenu(ssh, lang):
    pass

def patchLanguagePack(ssh):
    # /root/web/js/lang.json 
    # /mnt/plugin/vca/web/pluglang.json ==> not a complete json file. copy to /tmp/plugin/pluginlang.json (complete json file)
    # /root/web/lang_json_edit.cgi
    # edit "/root/web/js/lang.js" and "root/web/cgi-bin/admin/setup_system_language.js"
  
    cwd = os.getcwd()
    IP_addr = devEntry.get()
    arr_file = [
        {"name": "lang_json_edit.php",      "path": dest_dir + "/"},
        {"name": "lang.json",               "path": "/root/web/js/"},
        {"name": "pluginlang.json",         "path": "/mnt/plugin/vca/web/"},
        {"name": "lang.js",                 "path": "/root/web/js/"},
        {"name": "setup_system_language.js","path": "/root/web/cgi-bin/admin/"}
    ]
    # check if necessary files exist.
    for file in arr_file :
        if os.path.isfile(cwd + "/src/" + file['name'] ):
            showMessage (cwd + "/src/" + file['name'] + " exist, OK")
        else :
            showMessage(cwd + "/src/" + file['name'] + " not exist, Fail", "error")
            return False

    # upload files
    if not os.path.isdir("%s/bk/%s/" %(cwd, IP_addr)) :
        os.makedirs("%s/bk/%s/" %(cwd, IP_addr))

    sftp = ssh.open_sftp()
    for file in arr_file :
        showMessage("uploading file: %s%s" %(file['path'], file['name']))
        x = sshcmd(ssh, "ls -al  %s%s | awk '{print $9}'" %(file['path'], file['name']))
        if x :
            sftp.get("%s%s" %(file['path'], file['name']), "%s/bk/%s/%s_%s" %(cwd, IP_addr, str(time.strftime('%Y%m%d%H%M')),file['name']))
            sshcmd(ssh, "mv %s%s %s%s.bk" %(file['path'], file['name'], file['path'],file['name']))
        
        sftp.put("%s/src/%s" %(cwd, file['name']), "%s%s" %(file['path'], file['name']))
        if file['name'] == "pluginlang.json":
            with open ("%s/src/%s" %(cwd, file['name']), "r") as f:
                body = f.read()
            with open ("%s/src/%s.tmp" %(cwd , file['name']), "w") as f:
                f.write('{\r\n"language":[\r\n' + body + '\r\n]\r\n}')
            
            sftp.put("%s/src/%s.tmp" %(cwd , file['name']), "/tmp/plugin/%s" %file['name'])
            os.unlink("%s/src/%s.tmp" %(cwd , file['name']))

        progress(1)
    sftp.close()
    # sshcmd(ssh, "ln -s /mnt/plugin/patch/lang_json_edit.php /root/web/cgi-bin/operator/lang_json_edit.cgi" )
    mklink(ssh, "/mnt/plugin/patch/lang_json_edit.php", "/root/web/cgi-bin/operator/lang_json_edit.cgi")
    showMessage("Patching language complete!!")
    return True

def changeModel(ssh, model, brand, device_name) :
    # check if send one cgi command, system will reboot, so can not excuete other cgi command.
    cgi_str = {
        'brand':       '/cgi-bin/system/setup.cgi?msubmenu=system&action=apply&model_manufacturer=%s' %brand,
        'model':       '/cgi-bin/system/setup.ci?msubmenu=system&action=apply&model_name=%s' %model,
        'device_name': '/cgi-bin/admin/system.cgi?msubmenu=device_info&action=apply&device_name=%s' %device_name,
    }

def hideMenu(ssh):
    cwd = os.getcwd()
    flag = False
    sftp = ssh.open_sftp()
    sftp.get("/root/web/cgi-bin/admin/setup_main.js", "%s/setup_main.js" %cwd)

    with open("%s/setup_main.js" %cwd, "r", encoding='utf-8') as f:
        body = f.read()

    body_n= ""
    for line in body.splitlines():
        l = line.strip()
        if l.find("""["Service", "setup_security_service.cgi"]""") >= 0 and l[0:2] != "//":
            print(l)
            flag = True
            line = "//" + line
        body_n += "\n"+line
    if flag:
        sshcmd(ssh, "mv /root/web/cgi-bin/admin/setup_main.js /root/web/cgi-bin/admin/setup_main.js.bk")
        with open("%s/setup_main.js.tmp" %cwd, "w", encoding='utf-8') as f:
            f.write(body_n)
        sftp.put("%s/setup_main.js.tmp" %cwd, "/root/web/cgi-bin/admin/setup_main.js")
    sftp.close()
    # ["Service", "setup_security_service.cgi"] to // ["Service", "setup_security_service.cgi"] in setup_main.js

   
#ssh = paramiko.SSHClient()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#ssh.connect(server, port=22, username='root', password=sshpw)
#hideMenu(ssh)

#ssh.close()

#sys.exit()


def checkIP(ip_addr):
    cmd_str = "ping -n 1 -w 2 %s > nul" %ip_addr
    exit_code = os.system(cmd_str)

    if(exit_code == 0) :
        return True
    return False

def showMessage(strs, type="info"):
    if strs == True:
        strs = 'True'
    elif strs == False:
        strs = 'False'
    print(strs)
    tx.insert("end", strs + "\n")
    if type == "error" :
        s = tx.index("end").split('.')
        st = "%d.0" %(int(s[0])-2)
        tt = "%d.0" %(int(s[0])-1)
        #		print st	
        tx.tag_add("tag", st , tt)
        tx.tag_config("tag", foreground="red")
    try:
        tx.see('end')
    except:
        pass

def progress(p):
    global prog_state
    global prog_step
    if not p:
        prog_state = 0
    if p == 100:
        prog_state = 100
    else :
        prog_state += p*prog_step
    prog["value"] = prog_state
    prog.update()
    print(prog_state)

def doPatch():
    global Trial
    global sshpw
    global prog_step
    
    progress(0)
    server = devEntry.get()
    httppw = pwEntry.get()
    ck_func = [ckv0.get(), ckv1.get(), ckv2.get()]
    prog_step = round(100/(int(ckv0.get()*3 + int(ckv1.get())*12 + int(ckv2.get())*5 + 2) ) )
    print ("progress step", prog_step)

    if not checkIP(server):
        showMessage("device ip: "+ server+" is unreachable!", "error")
        return False

    if not httppw:
        showMessage("Type the password of root" , "error")
        return False


    showMessage("device ip: "+ server+" is online!")
    progress(1)

    if Trial <1:
        showMessage("Your IP is blocked, reboot the device" , "error")
        return False

    authkey = checkAuthMode(server, 'root', httppw)
    if not authkey:
        Trial -=1
        showMessage("device ip: "+ server+" SSH service is not enabled", "error")
        showMessage("Check the device is IPAi or correct password of root", "error")
        showMessage("You have %d times chance" %Trial, "error")
        return False

    enssh = enableSSH(server, httppw)
    if enssh:
        showMessage("device ip: "+ server+" SSH service is enabled")
        progress(1)


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(server, port=22, username='root', password=sshpw)

    if ck_func[0]:
        if setDatetime(ssh):
            showMessage('set time and timezone OK')
        else :
            showMessage('set time Fail', 'error')

    if ck_func[1]:
        showMessage('patching Counting Report')
        patchBin(ssh)
    
    if ck_func[2]:
        showMessage('patching Language Pack')
        patchLanguagePack(ssh)
    
    ssh.close()
    progress(100)

def cancel():
	print ("Cancel")
	window.destroy()

def printPos(event):
    print(event.x, event.y)


if __name__ == "__main__":
    Trial =3
    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    window.title("IP Ai Patch Tool by Hans Kim")
    window.geometry("460x220")
    window.resizable(True, True)

    window.bind("<Button-1>", printPos)   

    devLabel = tk.Label(window, text="IP addr")
    devLabel.place(x=20, y=15)
    devEntry = tk.Entry(window, width=20)
    devEntry.place(x=70, y= 15)

    pwLabel = tk.Label(window, text="root Password")
    pwLabel.place(x=210, y=15)
    pwEntry = tk.Entry(window, show="*", width=20)
    pwEntry.place(x=300, y= 15)

    ckv0 = tk.IntVar()
    ttk.Checkbutton(window, text = "Date and Time", variable=ckv0).place(x=20, y=46) 

    ckv1 = tk.IntVar()
    ttk.Checkbutton(window, text = "patch Binaries", variable=ckv1).place(x=137, y=46) 

    ckv2 = tk.IntVar()
    ttk.Checkbutton(window, text = "language Pack", variable=ckv2).place(x=270, y=46) 

    tx=tk.Text(window, height=5, width=58)
    tx.place(x=20, y=75)


    b2 = tk.Button(window, text="Patch", command=doPatch, width=10, height=1)
    b2.place(x=200, y= 175)

    b3 = tk.Button(window, text="Cancel", command=cancel, width=10, height=1)
    b3.place(x=300, y= 175)

    prog = ttk.Progressbar(window, maximum=100, length=410, mode="determinate")
    prog.place(x=20, y= 150)
    prog["value"] = 0

    devEntry.insert(0, server)
    pwEntry.insert(0, httppw)
 
    window.mainloop()

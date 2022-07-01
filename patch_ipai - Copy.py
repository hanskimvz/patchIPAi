
# enable SSH in Device // enableSSH
#  Connet sftp
#  create /mnt/plugin/crpt
#  write a file /mnt/plugin/crpt/post_script.sh
#  copy file "mk_ct_report.cgi" to "/mnt/plugin/crpt/"

#  copy file countreport.cgi to "/mnt/plugin/crpt/"
#  make directory "/root/web/cgi/bin/operator/"
#  ln -s /mnt/plugin/crpt/countreport.cgi  /root/web/cgi/bin/operator/countreport.cgi

from ast import operator
import os, time, sys
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64, re
import paramiko
import tkinter as tk
from tkinter import ttk

absdir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(absdir)

from document_src import body_crpt_sh, body_crpt_cgi, body_view_crpt_cgi, body_lang_json_edit


# view SSH
# http://192.168.132.6/cgi-bin/admin/security.cgi?msubmenu=service&action=view
# enable SSH
# http://192.168.132.6/cgi-bin/admin/security.cgi?msubmenu=service&action=apply&support_ssh=1

server = "192.168.132.6"
user ="root"
httppw = "Rootpass12345~"
sshpw = "cpro0109"

def enableSSH(url, rootid, rootpw):
    mode= 'basic'
    enabled = True
    
    def checkAuthMode(url):
        r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPDigestAuth(rootid, rootpw))
        if r.text.find('Unauthorized') < 0:
            return HTTPDigestAuth(rootid, rootpw)
        
        r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPBasicAuth(rootid, rootpw))
        if r.text.find('Unauthorized') <0:
            return HTTPBasicAuth(rootid, rootpw)
        
        return False

    authkey = checkAuthMode(url)
    if not authkey:
        return False

    r = requests.get('http://'+url+'/cgi-bin/admin/security.cgi?msubmenu=service&action=view', auth=authkey)
    if r.text.find('support_ssh=1') >=0:
        return True
    
    else :
        r = requests.get('http://'+url+'/cgi-bin/admin/security.cgi?msubmenu=service&action=apply&support_ssh=1', auth=authkey)
        time.sleep(1)
        r = requests.get('http://'+url+'/cgi-bin/admin/security.cgi?msubmenu=service&action=view', auth=authkey)
        if r.text.find('support_ssh=1') >=0:
            return True 
    return False

# def readyDoc(paragraph=""):
#     with open ("./document.src") as f:
#         body = f.read()
  
#     # body = body.replace("$", "\\$")
    
#     sepertor = re.compile(r"\[([a-zA-Z_]+)\]", re.IGNORECASE)
#     m = sepertor.finditer(body)
#     arr = []
#     para = {}
#     for x in m:
#         arr.append({"name": x.groups()[0], "start":x.start(), "end": x.end()})
    
#     for i in range(0, len(arr)):
#         name = arr[i]['name']
#         start = arr[i]['end'] +1
#         end = arr[i+1]['start'] if i < (len(arr)-1) else len(body)

#         para[name] = body[start:end]
#         # with open(name+".txt", "w") as f:
#         #     f.write(para[name])
#     if paragraph:
#         return para[paragraph]
#     return para    

# def addSlashes(str):
#     str = str.replace("\\", "\\\\")
#     str = str.replace("$", "\\$")
#     str = str.replace('"', '\\"')
#     str = str.replace("`", "\`")
#     return str

# def OperateSSH_CTRPT(ssh, sftp):
#     p=20
#     def sshcmd(str):
#         stdin, stdout, stderr = ssh.exec_command(str)
#         lines = stdout.readlines()
#         return (''.join(lines))

#     x = sshcmd("ls -al /mnt/plugin/ |grep ^d |awk '{print $9}'")
#     if x.find("crpt") < 0:
#         print ("create directory: /mnt/plugin/crpt")
#         sshcmd("mkdir /mnt/plugin/crpt")
#     p+=10
#     progress(p)

#     x = sshcmd("ls -al /root/web/cgi-bin/ |grep ^d |awk '{print $9}'")
#     if x.find("operator") < 0:
#         print ("create directory: /root/web/cgi-bin/operator")
#         sshcmd("mkdir /root/web/cgi-bin/operator")
#     p+=10
#     progress(p)
#     # print(x)

#     # files: countreport.cgi, mk_ct_report.cgi, post_startup.sh
#     textbody = readyDoc()
#     # print (textbody)
#     cmdstr = 'echo  "%s" > /mnt/plugin/crpt/post_startup.sh' %(addSlashes(textbody['body_sh']))
#     x = sshcmd(cmdstr)
#     p+=10; progress(p)    
    
#     cmdstr = "chmod 755 /mnt/plugin/crpt/post_startup.sh"
#     x = sshcmd(cmdstr)
#     p+=10; progress(p)

#     cmdstr = 'echo  "%s" > /mnt/plugin/crpt/mk_ct_report.cgi' %(addSlashes(textbody['body_cgi']))
#     x = sshcmd(cmdstr)
#     p+=10; progress(p)

#     cmdstr = 'echo  "%s" > /mnt/plugin/crpt/countreport.cgi' %(addSlashes(textbody['body_view']))
#     x = sshcmd(cmdstr)
#     p+=10; progress(p)
#     # link 
#     x = sshcmd("ls -al /root/web/cgi-bin/operator |grep countreport.cgi |awk '{print $9}'")
#     # print (x)
#     if not x:
#         cmdstr = 'ln -s /mnt/plugin/crpt/countreport.cgi /root/web/cgi-bin/operator/countreport.cgi'
#     p+=10; progress(p)


# def patchLanguageChinese(ssh, sftp):
#     # /root/web/js/lang.lang 
#     # /mnt/plugin/vca/web/pluglang.json ==> not a complete json file. copy to /tmp/plugin/pluginlang.json (complete json file)
#     # /root/web/lang_json_edit.cgi
#     def sshcmd(str):
#         stdin, stdout, stderr = ssh.exec_command(str)
#         lines = stdout.readlines()
#         return (''.join(lines))
    
#     textbody = readyDoc()
#     cmdstr = 'echo  "%s" > /root/web/lang_json_edit.cgi' %(addSlashes(textbody['lang_json_edit']))
#     # x = sshcmd(cmdstr)


def OperateSSH_CTRPT(ssh):
    p=20
    def sshcmd(str):
        stdin, stdout, stderr = ssh.exec_command(str)
        lines = stdout.readlines()
        return (''.join(lines))

    x = sshcmd("ls -al /mnt/plugin/ |grep ^d |awk '{print $9}'")
    if x.find("crpt") < 0:
        print ("create directory: /mnt/plugin/crpt")
        sshcmd("mkdir /mnt/plugin/crpt")
    p+=10
    progress(p)

    x = sshcmd("ls -al /root/web/cgi-bin/ |grep ^d |awk '{print $9}'")
    if x.find("operator") < 0:
        print ("create directory: /root/web/cgi-bin/operator")
        sshcmd("mkdir /root/web/cgi-bin/operator")
    p+=10
    progress(p)
    # print(x)

    # files: countreport.cgi, mk_ct_report.cgi, post_startup.sh
    sftp = ssh.open_sftp()
    cwd = os.getcwd()
    print (cwd)
    
    # sftp.put()
    # print (textbody)
    # cmdstr = 'echo  "%s" > /mnt/plugin/crpt/post_startup.sh' %(addSlashes(textbody['body_sh']))
    # x = sshcmd(cmdstr)
    # p+=10; progress(p)    
    
    # cmdstr = "chmod 755 /mnt/plugin/crpt/post_startup.sh"
    # x = sshcmd(cmdstr)
    # p+=10; progress(p)

    # cmdstr = 'echo  "%s" > /mnt/plugin/crpt/mk_ct_report.cgi' %(addSlashes(textbody['body_cgi']))
    # x = sshcmd(cmdstr)
    # p+=10; progress(p)

    # cmdstr = 'echo  "%s" > /mnt/plugin/crpt/countreport.cgi' %(addSlashes(textbody['body_view']))
    # x = sshcmd(cmdstr)
    # p+=10; progress(p)
    # # link 
    # x = sshcmd("ls -al /root/web/cgi-bin/operator |grep countreport.cgi |awk '{print $9}'")
    # # print (x)
    # if not x:
    #     cmdstr = 'ln -s /mnt/plugin/crpt/countreport.cgi /root/web/cgi-bin/operator/countreport.cgi'
    # p+=10; progress(p)
    
    sftp.close()


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
    prog["value"] = p
    prog.update()
    print(p)

def doPatch():
    global Trial
    global sshpw
    server = devEntry.get()
    if not checkIP(server):
        showMessage("device ip: "+ server+" is unreachable!", "error")
        return False
    else :
        showMessage("device ip: "+ server+" is online!")
        progress(10)

    httppw = pwEntry.get()
    if not httppw:
        showMessage("Type the password of root" , "error")
        return False

    if Trial <1:
        showMessage("You have %d times chance" %Trial, "error")
        showMessage("Your IP is blocked, reboot the device" , "error")
        return False

    enssh = (enableSSH(server, 'root', httppw))
    
    if enssh:
        showMessage("device ip: "+ server+" SSH service is enabled")
        progress(20)
        Trial = 3
    else:
        Trial -=1
        showMessage("device ip: "+ server+" SSH service is not enabled", "error")
        showMessage("Check the device is IPAi or correct password of root", "error")
        showMessage("You have %d times chance" %Trial, "error")
        return False
    

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(server, port=22, username='root', password=sshpw)

    if ckv1.get():
        showMessage('patching Counting Report')
        OperateSSH_CTRPT(ssh)
    
    # if ckv2.get():
    #     showMessage('patching Language Pack')
    #     patchLanguageChinese(ssh, sftp)
    
    ssh.close()
    progress(100)

    
    


def cancel():
	print ("Cancel")
	window.destroy()

def printPos(event):
    # print(event.x, event.y)
    print (ckv1.get())

if __name__ == "__main__":
    Trial = 3
    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    window.title("IP Ai Patch Tool by Hans Kim")
    window.geometry("460x220")
    window.resizable(True, True)

    # window.bind("<Button-1>", printPos)   

    devLabel = tk.Label(window, text="IP addr")
    devLabel.place(x=20, y=15)
    devEntry = tk.Entry(window, width=20)
    devEntry.place(x=70, y= 15)

    pwLabel = tk.Label(window, text="root Password")
    pwLabel.place(x=210, y=15)
    pwEntry = tk.Entry(window, show="*", width=20)
    pwEntry.place(x=300, y= 15)

    ckv1 = tk.IntVar()
    ttk.Checkbutton(window, text="Count Report", variable=ckv1).place(x=20, y=46) 

    ckv2 = tk.IntVar()
    ttk.Checkbutton(window, text="language Pack", variable=ckv2).place(x=137, y=46) 

    tx=tk.Text(window, height=5, width=58)
    tx.place(x=20, y=75)


    b2 = tk.Button(window, text="Patch", command=doPatch, width=10, height=1)
    b2.place(x=200, y= 175)

    b3 = tk.Button(window, text="Cancel", command=cancel, width=10, height=1)
    b3.place(x=300, y= 175)

    prog = ttk.Progressbar(window, maximum=100, length=410, mode="determinate")
    prog.place(x=20, y= 150)
    prog["value"] = 0

 
    window.mainloop()

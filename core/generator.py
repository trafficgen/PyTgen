'''
Copyright (c) 2012 Sven Reissmann <sven@0x80.io>

This file is part of the PyTgen traffic generator.

PyTgen is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyTgen is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyTgen. If not, see <http://www.gnu.org/licenses/>.
'''

import logging
import random
import datetime
import time
import base64
import string
import os

import ping
import urllib2
import smtplib
import ftplib
import shutil
import paramiko


class ping_gen():
    __generator__ = 'ping'
    
    def __init__(self,
                 params):
        self._host = params[0]
        self._num = params[1]
        
    def __call__(self):
        for _ in range(self._num):
            logging.getLogger(self.__generator__).info("Pinging: %s", self._host)
            if ping.do_one(dest_addr=self._host,
                           timeout=5,
                           psize=64) is not None:
                logging.getLogger(self.__generator__).debug("Got PONG from %s", self._host)

class http_gen():
    __generator__ = 'http'
    
    def __init__(self,
                 params):
        self._url = params[0]
        self._num = params[1]
        
    def __call__(self):
        for _ in range(self._num):
            logging.getLogger(self.__generator__).info("Requesting: %s", self._url)
            response = urllib2.urlopen(self._url)
            logging.getLogger(self.__generator__).debug("Recieved %s byte from %s", str(len(response.read())), self._url)
            time.sleep(random.random() * 5)    
    
class smtp_gen():
    __generator__ = "smtp"
    
    def __init__(self,
                 params):
        self._host = params[0]
        self._user = params[1]
        self._pass = params[2]
        self._from = params[3]
        self._to = params[4]
        
    def __call__(self):
        rnd = ''
        for _ in xrange(int(10000 * random.random())):
            rnd = rnd + random.choice(string.letters)
        
        msg = "From: " + self._from + "\r\n" \
            + "To: " + self._to + "\r\n" \
            + "Subject: PyTgen " + str(datetime.datetime.now()) + "\r\n\r\n" \
            + rnd + "\r\n"
        
        logging.getLogger(self.__generator__).info("Connecting to %s", self._host)
        
        try: 
            sender = smtplib.SMTP(self._host, 25)
        
            try:
                sender.starttls()
            except:
                pass
            
            try:
                sender.login(self._user, self._pass)
            except smtplib.SMTPAuthenticationError:
                sender.docmd("AUTH LOGIN", base64.b64encode(self._user))
                sender.docmd(base64.b64encode(self._pass), "")
            
            sender.sendmail(self._from, self._to, msg)
            logging.getLogger(self.__generator__).debug("Sent mail via %s", self._host)
                
        except:
            raise
        
        else:
            sender.quit()

class ftp_gen():
    __generator__ = 'ftp'
    
    def __init__(self,
               params):
        self._host = params[0]
        self._user = params[1]
        self._pass = params[2]
        self._put = params[3]
        self._get = params[4]
        self._num = params[5]
        
    def __call__(self):
        logging.getLogger(self.__generator__).info("Connecting to %s", self._host)
        
        ftp = ftplib.FTP(self._host,
                         self._user,
                         self._pass)
        
        for _ in xrange(self._num):
            if self._put is not None:
                logging.getLogger(self.__generator__).debug("Uploading %s", self._put)
                f = open("files/" + self._put, 'r')
                ftp.storbinary("STOR " + self._put, f)
                f.close()
            
            time.sleep(5 * random.random())   
            
            if self._get is not None:
                logging.getLogger(self.__generator__).debug("Downloading %s", self._get)
                ftp.retrbinary('RETR ' + self._get, self.__getfile)
                
            time.sleep(5 * random.random())
        
        ftp.quit()
        
    def __getfile(self,
                  file):
        pass

class copy_gen():
    __generator__ = "copy"
    
    def __init__(self,
                 params):
        self._src = params[0]
        self._dst = params[1]
        
    def __call__(self):
        logging.getLogger(self.__generator__).info("Copying from %s to %s", self._src, self._dst)
        
        if os.path.isdir(self._src):
            dst = self._dst + "/" + self._src
            
            if os.path.exists(dst):
                logging.getLogger(self.__generator__).debug("Destination %s exists. Deleting it.", dst)
                shutil.rmtree(dst)
                
            shutil.copytree(self._src, dst)
            
        else:
            shutil.copy2(self._src, self._dst)

class ssh_gen():
    __generator__ = "ssh"
    
    def __init__(self,
                 params):
        self._host = params[0]
        self._port = 22
        self._user = params[1]
        self._pass = params[2]

    def __call__(self):
        logging.getLogger(self.__generator__).info("Connecting to %s", self._host)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self._host, 
                       self._port, 
                       self._user, 
                       self._pass)
        
        (stdin, stdout, stderr) = client.exec_command("ls")
        print stdout.readlines()
        
        client.close()
        
class sftp_gen():
    __generator__ = "sftp"
    
    def __init__(self,
                 params):
        self._host = params[0]
        self._port = 22
        self._user = params[1]
        self._pass = params[2]
        self._src = params[3]
        self._dst = params[4]

    def __call__(self):
        logging.getLogger(self.__generator__).info("Connecting to %s", self._host)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self._host, 
                       self._port, 
                       self._user, 
                       self._pass)
        
        sftp = paramiko.SFTPClient(client.get_transport())
        #sftp.get(self._dst, self._src, self._getfile)
        #sftp.put(self._src, self._dst)
        
        client.close()
        
    def _getfile(self,
                  file):
        pass
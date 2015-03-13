#!/usr/bin/env python
# NetGSM SMS Gateway
# Copyright (C) 2015 Ertugrul T. Kara   ( ertugrulk@live.com )
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import smtplib
import email
from email.MIMEText import MIMEText
import ConfigParser
import logging
import time
from string import Template
from urlparse import parse_qs

class SMSGateway(object):
	def __init__(self,configpath):
		self.cfgfile = configpath
		self.config = ConfigParser.RawConfigParser()
		self.initconfig()


	def initconfig(self):
		self.config.read(self.cfgfile)
		if not self.config.has_section("SMTP"):
			self.config.add_section("SMTP")
			self.config.set("SMTP","Username","test@gmail.com")
			self.config.set("SMTP","Password","MySuperSecretPass55")
			self.config.set("SMTP","Host","smtp.gmail.com")
			self.config.set("SMTP","Port",465)
			self.config.set("SMTP","UseSSL","1")
		if not self.config.has_section("Prefs"):
			self.config.add_section("Prefs")
			self.config.set("Prefs","DestinationEmail","test@gmail.com")
			self.config.set("Prefs","EmailSubject","SMS FROM $sender")
			self.config.set("Prefs","EmailText","Received from $sender at $datetime: $message")
		with open(self.cfgfile,"w") as myfile:
			self.config.write(myfile)


	def send_email(self,msubject,mtext):
		username = self.config.get("SMTP","Username")
		password = self.config.get("SMTP","Password")
		smtphost = self.config.get("SMTP","Host")
		smtpport = self.config.get("SMTP","Port")
		mto = self.config.get("Prefs","DestinationEmail")
		smtpIsSSL = self.config.get("SMTP","UseSSL")
		msg = email.MIMEMultipart.MIMEMultipart()
		msg['From'] = username
		msg['To'] = email.Utils.COMMASPACE.join([mto])
		msg['Subject'] = msubject
		msg.attach(MIMEText('\n'+mtext, 'plain'))
		try:
			if smtpIsSSL=="1":
				server = smtplib.SMTP_SSL(smtphost, smtpport)
			else:
				server = smtplib.SMTP(smtphost, smtpport)
			server.ehlo()
			#server.starttls()
			server.ehlo
			server.login(username, password)
			server.sendmail(username, [mto], msg.as_string())
			server.close()
			return True
		except:
			logging.error("Error during the SMTP authentication. ",exc_info=True)
			return False


	def handle_incoming_sms(self,sender,message):
		datetime = time.strftime('%x %X')
		values = {"sender":sender,"datetime":datetime,"message":message}
		tmpsubject = Template(self.config.get("Prefs","EmailSubject"))
		tmptext = Template(self.config.get("Prefs","EmailText"))
		subject = tmpsubject.substitute(values)
		text = tmptext.substitute(values)
		if self.send_email(subject,text):
			logging.info("INCOMING SMS: %s %s SENT"% (subject,text))
			return True
		else:
			logging.error("INCOMING SMS: %s %s NOT SENT"% (subject,text))
			return False

def application(environ, start_response):
	apppath = "/path/to/your/application"
	output = "ERROR"
	try:
		logging.basicConfig(level=logging.DEBUG, filename=apppath+"smsapp.log", format='[%(asctime)s][%(levelname)s] %(message)s', )
	except:
		output = "Permission error, please check app path variable."
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	if environ['REQUEST_METHOD'] == 'POST':
		try:
			qsl = parse_qs(request_body)
			sender = qsl["ceptel"][0]
			message = qsl["mesaj"][0]
			gateway = SMSGateway(apppath+"config.cfg")
			if gateway.handle_incoming_sms(sender,message):
				output = "OK"
		except (IndexError):
			logging.error("Error parsing form data. ",exc_info=True)
	output_len = sum(len(line) for line in output)
	start_response('200 OK', [('Content-type', 'text/html'),
								('Content-Length', str(output_len))])
	return output


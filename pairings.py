import csv 
import os
import smtplib
import sys
import random
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage

REQRD = (
	'USERNAME',
	'PASSWORD',
	'FROM',
	'SUBJECT',
	)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'info.yml')

HEADER = """Content-Type: text/HTML; charset="utf-8"
From: {frm}
To: {to}
Subject: {subject}
"""

class Person:
	def __init__(self, name, email):
		self.name = name
		self.email = email

class Pair:
	def __init__(self, giver, reciever):
		self.giver = giver 
		self.reciever = reciever 

def pairing_generator(giver, reciever_list):
	if not reciever_list:
		raise Exception('No recievers in list')
	choice = random.choice(reciever_list)
	if choice.name == giver.name:
		if len(reciever_list) is 1:
			raise Exception('Only one reciever left')
		return pairing_generator(giver, reciever_list)
	else:
		return choice

def create_pairs(participants):
	pairs = []
	recievers_list = participants[:]
	for giver in participants:
		try:
			reciever = pairing_generator(giver, recievers_list)
			recievers_list.remove(reciever)
			pairs.append(Pair(giver, reciever))
		except:
			create_pairs(participants)
	return pairs

def parse_yaml(yaml_path=CONFIG_PATH):
    return yaml.load(open(yaml_path)) 

def main():
	
	participants_list = []
	with open(sys.argv[1], 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				participants_list.append(Person(row[0], row[1]))

	if len(participants_list) < 2:
		raise Exception('Not enough participants specified.')

	pairings = create_pairs(participants_list)
	config = parse_yaml()

	sender = config['SENDER']
	username = config['USERNAME']
	password = config['PASSWORD']
	subject = config['SUBJECT']
	frm = config['FROM']

	for key in REQRD:
		if key not in config.keys():
			raise Exception('Required parameter %s not in yaml config file!' % (key,))

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.set_debuglevel(1)
	server.login(username, password)

	for pair in pairings:
		giver_name = pair.giver.name
		giver_email = pair.giver.email
		reciever_name = pair.reciever.name
		body = (HEADER+config['MESSAGE']).format(frm=frm,
			to=giver_email,
			subject=subject,
			santa=giver_name,
			santee=reciever_name,
		)

		server.sendmail(sender, giver_email, body)
		print "Successfully sent email"
		
if __name__ == "__main__":
    sys.exit(main())

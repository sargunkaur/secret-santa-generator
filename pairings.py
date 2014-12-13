import csv 
import os
import smtplib
import sys
import random
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage


sender = 'sargunjot.kaur@gmail.com'

REQRD = (
	'USERNAME',
	'PASSWORD',
	'FROM',
	'SUBJECT',
	'MESSAGE',
	)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'info.yml')

HEADER = """Content-Type: text/html; charset="utf-8"
From: {frm}
To: {to}
Subject: {subject} 
"""

html = """\
   	<html>
   		<head></head>
	   		<body>
	   			<p>Dear {santa}<br>
	   			<img src="cid:image1">
			       &nbsp;&nbsp;&nbsp;&nbsp;This year you are <strong>{santee}'s</strong> Secret Santa!<br>
			       The decided spending is approx $10.00.<br>
			       This message was automagically generated from a computer. So nothing can possibly go wrong...<br>
			       But really, I may or may not have written unit tests, so if something is off, please let me know immediately! Sorry for the delay in 
   getting this to y'all!<br>
   				   script - https://github.com/sargunkaur/secret-santa-generator<br><br>
   				   Happy Holidays!<br>
			    </p>
	  		</body>
	</html>
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

	username = config['USERNAME']
	password = config['PASSWORD']
	message = config['MESSAGE']
	subject = config['SUBJECT']
	frm = config['FROM']

	for key in REQRD:
		if key not in config.keys():
			raise Exception('Required parameter %s not in yaml config file!' % (key,))

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.set_debuglevel(2)
	server.login(username, password)

	for pair in pairings:
		giver_name = pair.giver.name
		giver_email = pair.giver.email
		reciever_name = pair.reciever.name
		
		body = html.format(
			santa=giver_name,
			santee=reciever_name,
		)

		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['FROM'] = frm
		msg['TO'] = giver_email

		html_format = MIMEText(body, 'html')
		msg.attach(html_format)

		fp = open('blah.jpg', 'rb')
    	img = MIMEImage(fp.read())
    	fp.close()

    	img.add_header('Content-ID', '<image1>',)
    	msg.attach(img)
    	
    	server.sendmail(sender, giver_email, msg.as_string())
    	print "Successfully sent email"

	server.quit()
	
if __name__ == "__main__":
    sys.exit(main())

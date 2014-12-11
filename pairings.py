import csv 
import smtplib
import sys
import random

sender = 'test@gmail.com'

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
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

def main():
	
	participants_list = []
	with open(sys.argv[1], 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				participants_list.append(Person(row[0], row[1]))
	pairings = create_pairs(participants_list)

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.set_debuglevel(2)

	for pair in pairings:
		giver_name = pair.giver.name
		giver_email = pair.giver.email
		reciever_name = pair.reciever.name

		server.sendmail(sender, giver_email, message)       
		print "Successfully sent email"
	server.quit()
	
if __name__ == "__main__":
    sys.exit(main())

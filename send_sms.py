from twilio.rest import TwilioRestClient

def send_responce(client, number = "+17742185184", txt = "Default message"):
	message = client.messages.create(to=number, from_="+15169864627", body=txt)
	#client.messages.delete(message.sid)




account_sid = 'AC0c0ef57b1f1d72fb7459217fe973acc5'; 
auth_token = 'e7d5395ff8430ecaa90e9156f47dea30'; 
client = TwilioRestClient(account_sid, auth_token)
last_sid = client.messages.list()[0].sid

while 1:
	if len(client.messages.list(to = "+15169864627")):
		msg = client.messages.list(to = "+15169864627")[0]
		print(msg.body)
		client.messages.delete(msg.sid)
	else:
		print("no messages found")

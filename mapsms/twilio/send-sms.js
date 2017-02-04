// Twilio Credentials 
var accountSid = 'AC0c0ef57b1f1d72fb7459217fe973acc5'; 
var authToken = 'e7d5395ff8430ecaa90e9156f47dea30'; 
 
//require the Twilio module and create a REST client 
var client = require('twilio')(accountSid, authToken); 
 
client.messages.create({ 
    to: "+17818798963", 
    from: "+15169864627", 
    body: "This is the ship that made the Kessel Run in fourteen parsecs?", 
}, function(err, message) { 
	if (err) {
		console.log(err.message);
	} else {
    	console.log(message.sid); 
	}
});
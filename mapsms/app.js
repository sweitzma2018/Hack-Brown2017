MODE_INDEX = 1;
SRC_INDEX = 2;
DEST_INDEX = 3;
REQUEST_FORMAT = "Request must have the following format:\n";

var http = require('http'),
    express = require('express'),
    twilio = require('twilio'),
    bodyParser = require('body-parser');
    regex = require('regex');

var app = express();
app.use(bodyParser.urlencoded({ extended: true })); 
testParsing();

app.post('/sms', function(req, res) {
    var twilio = require('twilio');
    var twiml = new twilio.TwimlResponse();
    response = parseMessage(req.body.Body);
    twiml.message(response);
    res.writeHead(200, {'Content-Type': 'text/xml'});
    res.end(twiml.toString());
});

function parseMessage(text) {
    var regex = /(\w*)\s+[Ff][Rr][Oo][Mm]\s+(.+)\s+[Tt][Oo]\s+(.+)/;
    if (regex.test(text)) {
        input = text.match(regex);
        mode = input[MODE_INDEX];
        src = input[SRC_INDEX];
        dest = input[DEST_INDEX];
        return getDirections(mode,src,dest);
    } else {
        return REQUEST_FORMAT;
    }
}

function getDirections(mode,src,dest) {
    var driveRegex = /[Dd][Rr][Ii][Vv][Ee]/;
    var walkRegex = /[Ww][Aa][Ll][Kk]/;
    if (driveRegex.test(mode)) {
        return getDirectionsHelper("drive",src,dest);
    } else if(walkRegex.test(mode)) {
        return getDirectionsHelper("walk",src,dest);
    } else {
        return REQUEST_FORMAT;
    }
}

function getDirectionsHelper(mode,src,dest) {
    return "Take a left until you reach Zeek's vagina."
    //FILL THIS IN
}

function testParsing() {
    var stdin = process.openStdin();
    stdin.on('data', function(chunk) { 
        console.log(parseMessage(chunk.toString())); 
    });
}

http.createServer(app).listen(1337, function () {
    console.log("Express server listening on port 1337");
});
import re
import requests

REQUEST_FORMAT = "Request must have the following format:\n'<mode> from <start> to <end>'"
MODE_INDEX = 1;
SRC_INDEX = 2;
DEST_INDEX = 3;

def parseMessage(text):
	regex = '(\w*)\s+[Ff][Rr][Oo][Mm]\s+(.+)\s+[Tt][Oo]\s+(.+)'
	if re.match(regex, text) is not None:
		m = re.search(regex, text)
		mode = m.group(MODE_INDEX).lower()
		src = m.group(SRC_INDEX)
		dest = m.group(DEST_INDEX)

		if (mode != 'drive' and mode != 'walk'):
			return REQUEST_FORMAT
		else:
			return getDirections(mode, src, dest)
	else:
		return REQUEST_FORMAT

def getDirections(mode, src, dest):
	url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + src + '&destination=' + dest + '&mode=' + mode + '&key=AIzaSyCkq49CClP9wIO-ZlkXFbKRRPvVYly4kFE';
	r = requests.get(url)
	json = r.json()
	steps = json['routes'][0]['legs'][0]['steps']
	steps_text = map(lambda x: x['html_instructions'] + ', ' + x['distance']['text'], steps)
	directions = ". ".join(steps_text)
	directions = re.sub(r"(<[^<>]+>)", "", directions)
	
	return directions

print(parseMessage('walk from 23 james st providence to 90 thayer st providence'))

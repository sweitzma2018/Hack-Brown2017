from twilio.rest import TwilioRestClient
from twilio.rest import exceptions
from math import ceil
import re
import requests
import signal
import sys

# Constants
MODE_INDEX = 1                                  
SRC_INDEX = 2
DEST_INDEX = 3
MAX_TXT_LEN = 1500      # the longest string that can fit in a text message
ERROR_TXT_LEN = 10000   # won't send messages longer than this constant
ACCOUNT_SID = 'AC0c0ef57b1f1d72fb7459217fe973acc5'
AUTH_TOKEN = 'e7d5395ff8430ecaa90e9156f47dea30'
SERVER_NUMBER = "+15169864627"


# handles an interrupt signal
def signal_handler(signal, frame):
    response = input('\r\nAre you sure you want to close the server? [y/n]: ')
    if response.lower() in 'yes':
        print('[+] Closing server.')
        sys.exit(0)
    else:
        print('[+] Server resuming...')

# Parses the texts from the users
def parse_message(text):
    help =  "Request must have the following format:"
    help += "\n\n<mode> from <origin> to <destination>\n\n"
    help += " - mode: \"drive\", \"walk\", \"bike\"\n"
    help += " - origin: starting location\n"
    help += " - destination: ending location"

    regex = '(\w*)\s+[Ff][Rr][Oo][Mm]\s+(.+)\s+[Tt][Oo]\s+(.+)'
    if re.match(regex, text) is not None:
        m = re.search(regex, text)
        mode = m.group(MODE_INDEX).lower()
        src = m.group(SRC_INDEX)
        dest = m.group(DEST_INDEX)

        if mode == 'drive':
            return get_directions('driving', src, dest)
        elif mode == 'walk':
            return get_directions('walking', src, dest)
        elif mode == 'bike':
            return get_directions('bicycling', src, dest)
        else:
            return help
    else:
        return help

# gets the directions from the google maps api
def get_directions(mode, src, dest):
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + src + '&destination=' + dest + '&mode=' + mode + '&key=AIzaSyCkq49CClP9wIO-ZlkXFbKRRPvVYly4kFE';
    #print(url)
    r = requests.get(url)
    json = r.json()

    # handle invalid requests
    if json['status'] != 'OK':
        return handle_error_status(json)

    # title to make it look nicer
    title = 'mapsms\n' + json['routes'][0]['copyrights'] + '\n\n'

    # add an overview to the beginning of the message
    overview = 'OVERVIEW\n'
    overview += 'Total Distance: ' + json['routes'][0]['legs'][0]["distance"]['text'] + '\n'
    overview += 'Total Time: ' + json['routes'][0]['legs'][0]["duration"]['text'] + '\n'
    overview += 'Start Address: ' + json['routes'][0]['legs'][0]["start_address"] + '\n'
    overview += 'End Address: ' + json['routes'][0]['legs'][0]["end_address"]

    steps = json['routes'][0]['legs'][0]['steps']

    directions = '\n\nDIRECTIONS\n'
    for i in range(len(steps)):
        # add a step count
        step = '[' + str(i + 1) + '] '

        # add the actual step instructions
        step += steps[i]['html_instructions'] 

        # find and format notes
        index = step.find('<div', 0)
        while index != -1:
            spacer = '\n   [+] '
            step = step[:index] + spacer + step[index:]
            index = step.find('<div', index + 1 + len(spacer))

        # remove all of the html tags
        step = re.sub(r"(<[^<>]+>)", "", step)

        # tack on the distance in the right location
        index = step.find('\n')
        if index == -1:
            step = step + ', ' + steps[i]['distance']['text'] + '\n'
        else:
            step = step[:index] + ', ' + steps[i]['distance']['text'] + step[index:] + '\n'

        # add step to directions
        directions += step

    
    return title + overview + directions

# handles invalid queries
def handle_error_status(json):
    status = json['status']

    if status == 'NOT_FOUND':
        if json['geocoded_waypoints'][0]["geocoder_status"] == 'ZERO_RESULTS':
            return "Origin could not be found."
        else:
            return "Destination could not be found."
    elif status == 'ZERO_RESULTS':
        return "No route could be found between the origin and destination."
    elif 'MAX_WAYPOINTS_EXCEEDED':
        return "Too many waypoints were provided in the request."
    elif status == 'MAX_ROUTE_LENGTH_EXCEEDED':
        return "Requested route is too long and cannot be processed."
    elif status == 'INVALID_REQUEST':
        return "Request was invalid"
    elif status == 'OVER_QUERY_LIMIT':
        return "Server has hit its query limit for the day."
    elif status == 'REQUEST_DENIED':
        return "Google denied use of the directions service by your application."
    elif status == 'UNKNOWN_ERROR':
        return "Directions request could not be processed due to a server error"

# runs the server
def main():
    # set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # set up twilio server
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    print('[+] Server up and running, text', SERVER_NUMBER, 'for directions.')
    empty = False # for printing purposes

    # loop forever
    while True:
        message_count = len(client.messages.list(to = SERVER_NUMBER))
        
        # if there are incoming messages
        if message_count: 
            print('[+] Server handling incoming message, total messages ('+str(message_count)+').')
            empty = False
            
            msg = client.messages.list(to = SERVER_NUMBER)[-1]  # get message that has been in the queue the longest
            txt = parse_message(msg.body)                       # get response based on text 

            # message is too long, probably an error
            if len(txt) >= ERROR_TXT_LEN:
                txt =  "Directions were too long to send. This may be a sign that "
                txt += "your origin or destination was misinterpreted."
                client.messages.create(to= msg.from_, from_=SERVER_NUMBER, body=txt) # respond 
            
            # message needs to be split into multiple texts
            elif len(txt) > MAX_TXT_LEN:
                txts = [txt[i:i+MAX_TXT_LEN] for i in range(0, len(txt), MAX_TXT_LEN)]
                ending = ' of ' + str(len(txts)) + '\n\n'
                for i in range(len(txts)):
                    txt = 'Part ' + str(i + 1) + ending
                    txt += txts[i]
                    client.messages.create(to= msg.from_, from_=SERVER_NUMBER, body=txt) # respond 

            # message can be sent in one text
            else:
                client.messages.create(to= msg.from_, from_=SERVER_NUMBER, body=txt) # respond 

            client.messages.delete(msg.sid) # delete message from the queue
            print('  [-] Message handled.')

        # no incoming messages
        elif not empty: 
            print("[+] No more messages in queue, waiting on more...")
            empty = True


# run it!
main()
            
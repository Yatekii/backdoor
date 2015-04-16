# Bastli Backdoor Client-Server Protocol

The protocol is based on JSON messages, which are sent over TCP. A newline charachter (\n) is used to delimit
the end of a message.

## BASE MESSAGE

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": <CMD>, "service": <SERVICE>, "params": <PARAMS>}}

<TOKEN> is your token to authenticate yourself.
<TIMESTAMP> is the current unix time
<CMD> is the preferred command to be executed
<SERVICE> the service to whose featureset <CMD> belongs
<PARAMS> is a list of all additional params required for <CMD>


### REGISTER

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "REGISTER", "params": []}}
    
Always needs to be issued by the client before sending anything else, 
any requests before it will be rejected by the server.


### REGISTER WEBUI

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "REGISTER WEBUI", "params": [<COMMUNICATION_TOKEN>]}}
    
Same as REGISTER except that it's meant for a webui instance, <COMMUNICATION_TOKEN> is a random 512 bit token the webui chooses for the session.
Any further queries should contain <COMMUNCIATION_TOKEN> in the <TOKEN> parameter.

### OPEN

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "OPEN", "params": [<DEVICE_TOKEN>]}}
   
Opens door at device registered with <DEVICE_TOKEN>

### ACCESS

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "ACCESS", "params": [<USER_TOKEN>]}}

Issues a GRANT response if <USER_TOKEN> has access at device with token <TOKEN>; otherwise a DENY response is issued

### GRANT

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "GRANT", "params": [<USER_TOKEN>]}}

Is issued after ACCESS has passed with valid tokens.

### DENY

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "DENY", "params": [<USER_TOKEN>]}}

Is issued after ACCESS has not passed.

### FLASH

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "FLASH", "params": [<USER_TOKEN>[,<DEVICE_TOKEN>]]}}

Issues a request to flash <USER_TOKEN>. If the request is sent from a webui, <DEVICE_TOKEN> needs to be set.

FLASHED

    {"auth": {"token": <TOKEN>, "time": <TIMESTAMP>}, "cmd": {"method": "FLASHED", "params": [<USER_TOKEN>]}}

Is issued after FLASH was successful.

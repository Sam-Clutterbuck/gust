############################################
# Created by: Samuel Clutterbuck
# Started : 24/03/2023
# Language : Python
# Version: Dev
#
############################################

############################################
Aim and goals:

Single app but 2 goals depending on location
An app that bridges an air gapped environment securely

Reciever 
- In airgapped side 
- Only able to connect to the source and nothing else
- unable to run any commands or execute any of the downloaded files
- triggers the connection to source not the other way
- recieves an md5 file of the target file first and places recieved file in a quarenteen zone untill it can confirm the hash matches 
    - Deletes and logs any missmatches

Source
- On Connected side
- can connect to internet but only to specific allowed sites
    - Able to connect to a specific download location 
    - if download location changes on versions can configure a regex query for it
- every source file must have a hash file associated
- Will not save the file if hashes dont match
- no connection to the system other than a port that recieves the request to transfer accross the gap 
- unable to run commands or execute files


Flow plan:

Source -> web url (hash)
Source <- hash file
Source -> web url (file)
Source <- file
Source -- Hash check
Source -- Save file to save location and listen on port

Reciever -> Source (Call on port)
Reciever <- Source (Send dictionary of all sources [not including child sections])
Reciever -> Source (Request a source hash)
Reciever <- Source (Send source hash file or value)
Reciever -> Source (Request the file)
Reciever <- Source (send the file)
Reciever -- hash check in issolated environment
Reciever -- save passed hashed files

possibly use docker containers
- one for isolated testing (docker in docker?)
- one for the application
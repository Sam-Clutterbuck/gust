# Config Files
## Core
>These Config files effect both client and server functionality
### commands.yaml
**Default location:** */core/data/commands.yaml*
**Use case:** The commands.yaml file contains all possible commands that can be carried out by the client and on the server. The file also has an extended functionality in code to redirect the commands to the appropriate functions for that command. 
*(note that some commands are system specific and are not designed to be called by the user, e.g. `![AUTHORISED]`)*
```
Default configuration (as of 10/04/2023)

list options:
	command: "![LIST]"
	func: None
update sources:
	command: "![UPDATE_SOURCES]"
	func: None
download files:
	command: "![DOWNLOAD]"
	func: None
transfer files:
	command: "![TRANSFER]"
	func: None
quit:
	command: "![QUIT]"
	func: None
authorised:
	command: "![AUTHORISED]"
	func: None
disconnect:
	command: "![DISCONNECT]"
	func: None
end transfer:
	command: "![END]"
	func: None
ready check:
	command: "![READY]"
	func: None
	
```

## Server
>These Config files effect server functionality
### downloads.yaml
**Default location:** */server/data/downloads.yaml*
**Use case:** The downloads.yaml file stores a list of all the downloaded sources with their file name, hash file name and the date they were last updated. This is used by the server to a store a list of the raw file names for it to obtain the file from when beginning a transfer so it isn't transferring to the client directly from the web url.
```
Default configuration (as of 10/04/2023)

example source:
	file: filename.tar.gz
	hash_file: filename_hash.tar.gz.sha256
	last updated: Day Month Year - Time
	
```

### gust_store.yaml
**Default location:** */server/data/gust_store.yaml*
**Use case:** The gust_store.yaml file is the location where all of the sources are stored and the core of the system. The direct urls for the source file and hash file are stored here alongside a reference of what type of hash is used.
```
Default configuration (as of 10/04/2023)

example source:
	file: https://www.provider.com/download/filename.tar.gz
	hash_file: https://www.provider.com/download/hash/filename.tar.gz.sha256
	hash_type: sha256
	
```
### passwd
**Default location:** */server/data/passwd.yaml*
**Use case:** The passwd file is a raw text file containing the user login info split by line comprised of a username with a hashed password. The server reads this file when users attempt to login via web gui or cli in order to authenticate their credentials.
```
Default configuration (as of 10/04/2023)

user::::hashhashhashhashhashhashhashhash

```
### server_config.yaml
**Default location:** */server/data/server_config.yaml*
**Use case:** The server_config.yaml file contains some data that configures how the server functions and feeds important global variables into the server classes. Such data includes the default ports / ip, max users, storage locations, etc...
```
Default configuration (as of 10/04/2023)

######################################
# Server / Source Options
######################################
#Default setup as loopback address
ip : '127.0.0.1'
port : 11811

#set how many login attempts before disconnected
connection attempt limit: 3

#max number of users at one time
max concurrent users: 2

#storage locations
server_sources_loc : server/data/gust_store.yaml
download_log_loc : server/data/downloads.yaml
download_loc : server/data/downloads/
logins_loc: server/data/passwd

```

## Client
>These Config files effect client functionality
### client_config.yaml
**Default location:** */client/data/client_config.yaml*
**Use case:** The client_config.yaml file contains the target address for the server as well as a few links to used storage locations to facilitate the transfer of files and allow connection to the server.
```
Default configuration (as of 10/04/2023)

######################################
# Client / Reciever Options
######################################
#Default setup as loopback address
target ip : '127.0.0.1'
target port : 11811

#storage locations
client_sources_loc : client/data/pulled_store.yaml
download_loc : client/data/downloads/

```
### pulled_store.yaml
**Default location:** */client/data/pulled_store.yaml*
**Use case:** The pulled_store.yaml is similar to the servers gust_store and also stores a list of all the sources however due to being on an non internet connected system it doesn't store any urls just the hash type so that it can run integrity checks on any files transferred. 
(note that this file is not designed to be edited on the client directly and instead should pull the corresponding data from the server so that it is transferring the correct files)
```
Default configuration (as of 10/04/2023)

example source:
	hash_type: sha256
	
```
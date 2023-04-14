# Roadmap tasks
## phase 1

 - [x] custom docker container
	 - [x] deploys either a server or client with the relevant packages
	 - [x] creates the required folders and structures
	 - [ ] locked down and secure base image
	 - [x] only having the min required python packages in docker image
	 - [ ] strict and custom firewall ruling
		 - [ ] one way traffic in specific use cases
		 - [ ] only open on required ports
	 - [ ] Server docker have http(s) traffic blocking to only allow from selected urls
	 - [ ] Add custom users and folder access control
	 - [ ] only have read write access 
	 	 - [ ] allow execute access for cli tools and services only
 - [x] add ability to trigger file download from web gui
	 - [x] have a list of what files are and aren't downloaded and the dates
	 - [x] ability to select a file to download on its own
	 - [x] download percentage bars
 - [x] Cli tools for client and server controling
	 - [x] server cli
	 - [x] client cli
 - [ ] User creation, editing and password reset functionality
	 - [x] python code
	 - [ ] Web gui version
	 - [x] Cli version
 - [x] Launch 0.1.0 alpha version
	 - [x] Docker release
	 - [x] Github pull

## future plans

 - [ ] some kind of automations (pull downloads once a day?)
 - [ ] separate user and admin level accounts with separate views
 - [ ] ability to assign sources to specific users 
 - [ ] RBAC
 - [ ] more elements to server web page
 - [ ] client web interface?

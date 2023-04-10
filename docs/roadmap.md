# Roadmap tasks
## phase 1

 - [ ] custom docker container
	 - [ ] deploys either a server or client with the relevant packages
	 - [ ] creates the required folders and structures
	 - [ ] locked down and secure base image
	 - [ ] only having the min required python packages in docker image
	 - [ ] strict and custom firewall ruling
		 - [ ] one way traffic in specific use cases
		 - [ ] only open on required ports
	 - [ ] Server docker have http(s) traffic blocking to only allow from selected urls
 - [ ] add ability to trigger file download from web gui
	 - [ ] have a list of what files are and aren't downloaded and the dates
	 - [ ] ability to select a file to download on its own
	 - [ ] download percentage bars?

## future plans

 - [ ] separate user and admin level accounts with separate views
 - [ ] ability to assign sources to specific users 
 - [ ] RBAC
 - [ ] more elements to server web page
 - [ ] client web interface?

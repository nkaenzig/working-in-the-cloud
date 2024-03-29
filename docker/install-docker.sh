#!/bin/bash

echo uninstall old docker versions
sudo apt-get remove docker docker-engine docker.io containerd runc

echo "install docker (test with docker run hello-world)"
sudo apt-get update
sudo apt-get install \
	    apt-transport-https \
	        ca-certificates \
		    curl \
		        gnupg-agent \
			    software-properties-common
sudo add-apt-repository \
	   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
	      $(lsb_release -cs) \
	         stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io


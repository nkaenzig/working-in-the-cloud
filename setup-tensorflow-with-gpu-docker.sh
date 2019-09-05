#!/bin/bash
echo "INSTALL GPU DRIVERS (nvidia-352 is the long branch driver including support for Tesla and Quadro)"
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt-get update && sudo apt-get install nvidia-352

echo "UNINSTALL OLD DOCKER VERSIONS"
sudo apt-get remove docker docker-engine docker.io containerd runc

echo "INSTALL DOCKER (TEST WITH DOCKER RUN HELLO-WORLD)"
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

echo "SETUP NVIDIA-DOCKER"
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo apt-get install nvidia-container-runtime
sudo systemctl restart docker

echo "REGISTER THE NEW RUNTIME TO THE DOCKER DAEMON"
sudo systemctl stop docker
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/override.conf <<EOF
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --host=fd:// --add-runtime=nvidia=/usr/bin/nvidia-container-runtime
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "LOAD AND RUN TENSORFLOW DOCKER CONTAINER"
sudo docker pull tensorflow/tensorflow:latest-gpu-py3
sudo docker run -it --rm --runtime=nvidia tensorflow/tensorflow:latest-gpu-py3 bash


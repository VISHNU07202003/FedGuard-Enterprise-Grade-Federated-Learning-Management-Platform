#!/bin/bash
# Bootstraps an Amazon Linux 2023 or Ubuntu EC2 instance for FedGuard Backend

set -e

echo "Updating system..."
sudo yum update -y || sudo apt update -y

echo "Installing Docker..."
# For Amazon Linux:
sudo yum install -y docker || sudo apt install -y docker.io
sudo service docker start || sudo systemctl start docker
sudo usermod -aG docker $USER

echo "Installing Docker Compose..."
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

echo "Bootstrap complete. Please log out and back in to apply Docker group changes."
echo "Then clone the repo and run: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"

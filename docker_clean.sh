#!/bin/bash

# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -q)

# Remove all containers
echo "Removing all containers..."
docker rm $(docker ps -a -q)

# Remove all images
echo "Removing all images..."
docker rmi -f $(docker images -q)

# Remove all networks (excluding the default ones)
echo "Removing all networks..."
docker network prune -f

# Remove all volumes
echo "Removing all volumes..."
docker volume prune -f

# Optional: Remove all dangling build cache
echo "Removing dangling build cache..."
docker builder prune -f

echo "All Docker containers, images, networks, and volumes have been removed."

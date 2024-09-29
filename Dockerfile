# Use the Jupyter base image
FROM jupyter/scipy-notebook:latest

# Switch to root to install packages
USER root

# Set the working directory to Jupyter's home
WORKDIR /home/jovyan

# Copy the requirements.txt file to the working directory
COPY requirements.txt /home/jovyan/

# Install the Python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file into the container (renamed from .envrc)
COPY .envrc /home/jovyan/.envrc

# Switch back to the default user (jovyan)
USER $NB_UID

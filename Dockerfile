# Use the Jupyter base image
FROM jupyter/scipy-notebook:latest

# Set the working directory to Jupyter's home
WORKDIR /home/jovyan

# Copy the requirements.txt file to the working directory
COPY requirements.txt /home/jovyan/

# Install the Python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

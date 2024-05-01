# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12.3-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install git+https://github.com/fdenivac/python-qobuz

# Run app.py when the container launches
CMD ["python", "./main.py"]

#Use python image as base image 
FROM python:3.8-slim-buster

# Set working directory in the container to /app
WORKDIR /app

#copy current directory into /app into container app
COPY . /app

# upgrade pip
RUN pip install --upgrade pip

#install any nneded packages 
RUN pip install --no-cache-dir -r requirements.txt

# set thed defalut commands to run when starting the container 
CMD ["python", "app.py"]
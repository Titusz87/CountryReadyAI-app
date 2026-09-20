#python version for base image
FROM python:3.14-slim

#set working directory inside container
WORKDIR /app

#copy dependency list inside the container to workdir 
COPY requirements.txt .

#install dependencies  
RUN pip install --no-cache-dir -r dependencies.txt

#copy the app folder into container environment 
COPY app/ .

#start uvicorn 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
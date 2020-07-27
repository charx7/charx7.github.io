---
type: blog-post
post_id: 2
tags: python, spark, pyspark, docker
author: Carlos Huerta 
title: Parallel fp-growth algorithm using spark, docker and mongodb (1) 
date: Jul 27 2020 
---

### How to build an scalable recomendation engine ⚙️
Last Year in collaboration with <a  target="_blank" href="https://www.linkedin.com/in/ankit001mittal/">Ankit Mittal</a> and <a target="_blank" href="https://www.linkedin.com/in/myuja/">Michael Yuja</a>  we had a project in mind. To develop a **recommendation engine** for the e-commerce website www.agglobal.com that sells hardware solutions in Honduras. The website has listed more than 7000 products and can be very hard for the daily user to navigate around all the different products and categories for them to find what they need.

Fortunately, we can resort to big-data and data science solutions to solve this issue. 
Similar to Amazon's "People who also bought X also bought Y..." that displays when browsing through Amazon's humongous catalog; to achieve that, we seek to develop a similar solution.

## 1. Set-up the spark-cluster using docker
We are going to use the **Big Data Europe** docker-spark container images as base images for our project. Nevertheless we need to set-up a folder structure as follows:

### 1.1 Spark-master set-up
* Create a `spark_master` directory, inside it create a `dockerfile` and a `master.sh` file. 
<div class="input">
  MY_PROJECT_NAME/spark_master/dockerfile
</div>
```
FROM bde2020/spark-base:2.4.0-hadoop2.7

COPY master.sh /

ENV SPARK_MASTER_PORT 7077
ENV SPARK_MASTER_WEBUI_PORT 8080
ENV SPARK_MASTER_LOG /spark/logs

EXPOSE 8080 7077 6066

CMD ["/bin/bash", "/master.sh"]
```
The `dockerfile` pulls a base docker image from dockerhub and sets some necessary environmental variables 
* `SPARK_MASTER_PORT`: defines in which port (inside the docker container) will our spark master run.
* `SPARK_MASTER_WEBUI_PORT`: defines the port to access the web UI
* `SPARK_MASTER_LOG`: the logs route

`EXPOSE` tells which container ports we are going to expose. `8080` for the web UI, `7077` to connect to the spark-master and `6066` is the spark-master port for the REST URL.

<div class="input">
  MY_PROJECT_NAME/spark_master/master.sh
</div>
```bash
#!/bin/bash

export SPARK_MASTER_HOST=`hostname`

source "/spark/sbin/spark-config.sh"

source "/spark/bin/load-spark-env.sh"

mkdir -p $SPARK_MASTER_LOG

export SPARK_HOME=/spark

ln -sf /dev/stdout $SPARK_MASTER_LOG/spark-master.out

cd /spark/bin && /spark/sbin/../bin/spark-class org.apache.spark.deploy.master.Master \
--ip $SPARK_MASTER_HOST --port $SPARK_MASTER_PORT --webui-port $SPARK_MASTER_WEBUI_PORT >> $SPARK_MASTER_LOG/spark-master.out
```
This bash script executes spark scripts that will load the configuration and the spark environment; you can inspect them by executing a shell inside the container(more on this later as it is a handy debugging tool for docker related issues), then makes a directory for our logs and sets the necessary `SPARK_HOME` environmental variable inside our docker container. Finally, it will execute spark binaries using the previously defined environmental variables. TLDR: This script executes our spark-master for us.

* ### 1.2 Spark-workers set-up
In the root of your project create a directory `spark_worker` and create a `dockerfile`.
<div class="input">
  MY_PROJECT_NAME/spark_worker/dockerfile
</div>
```
FROM bde2020/spark-base:2.4.0-hadoop2.7

COPY worker.sh /

ENV SPARK_WORKER_WEBUI_PORT 8081
ENV SPARK_WORKER_LOG /spark/logs
ENV SPARK_MASTER "spark://spark-master:7077"

EXPOSE 8081

# Copy the requirements.txt first, for separate dependency resolving and downloading
# the -p is to make it recursive
RUN mkdir -p /app
COPY requirements.txt /app/
RUN cd /app \
    && pip3 install -r requirements.txt

# Configure the following environment variables (unless the default value satisfies):
ENV SPARK_MASTER_NAME "spark-master"
ENV SPARK_MASTER_PORT "7077"

CMD ["/bin/bash", "/worker.sh"]
```
For this dockerfile, we need to set the `SPARK_MASTER`` SPARK_WORKER_WEBUI_PORT` and `SPARK_WORKER_LOG` environmental variables, we also copy and install requirements declared on a requirements.txt file (OPTIONAL), this could be useful if your project has external dependencies that you wish to install on every worker. We will be exposing the port `8081` inside our container and will define the map to the external port on the docker=compose file (part 2).

As in the `spark_master` directory, we will also add a script file.
<div class="input">
  MY_PROJECT_NAME/spark_worker/worker.sh
</div>
```bash
#!/bin/bash

. "/spark/sbin/spark-config.sh"

. "/spark/bin/load-spark-env.sh"

mkdir -p $SPARK_WORKER_LOG

export SPARK_HOME=/spark

ln -sf /dev/stdout $SPARK_WORKER_LOG/spark-worker.out

# Toggle to debug a greater sleep, some sleep is needed to give time to the master 
sleep 20

# Execute the connection to the master
/spark/sbin/../bin/spark-class org.apache.spark.deploy.worker.Worker \
 --webui-port $SPARK_WORKER_WEBUI_PORT $SPARK_MASTER \
 --memory 1G --cores 1  >> $SPARK_WORKER_LOG/spark-worker.out
```
This script will also source the configuration and env scripts, declare our SPARK_HOME environmental variable and finally call the spark binary that registers our spark-worker to the master. You can also modify the amount of **memory** and **cores** assigned to each worker.

### 1.3 Spark-submit and spark-job set-up
To submit a spark job with the appropriate structure and dependencies, we need to create a *python package egg*, so it will be necessary to create a python-package structure inside our project, but first we should create a venv that will be used to build and create our package and install (locally) our dependencies.

<div class="input">
  MY_PROJECT_NAME/pyspark_src/
</div>
```
tree
.
├── Dockerfile
├── pyspark_recom_engine
│   ├── __init__.py
│   └── jobs
├── requirements.txt
├── setup.py
└── template.sh
```
Here the directory `pyspark_recom_engine` will be where the logic of our package will live. In order for this to work, we need to set-up the following files:
<div class="input">
  MY_PROJECT_NAME/pyspark_src/Dockerfile
</div>
```
# Will extend form the spark-template that extends on itself with the spark-submit image
#FROM bde2020/spark-python-template:2.4.0-hadoop2.7
# Using an image before (the one that has the python reqs install)
FROM bde2020/spark-submit:2.4.0-hadoop2.7 

COPY template.sh /

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt /app/
#RUN pip3 install --upgrade pip
RUN cd /app \
      && pip3 install -r requirements.txt

# Copy the source code
COPY . /app

# Needed params
ENV SPARK_MASTER_NAME "spark-master"
ENV SPARK_MASTER_PORT "7077"
# Not sure if will work with this (this should be built by a parent image!)
ENV SPARK_MASTER_URL "spark://spark-master:7077"
# The location of the Job
ENV SPARK_APPLICATION_PYTHON_LOCATION app/pyspark_recom_engine/jobs/FpJob.py
# Extra (In case we need to suplement our spark job with command line args)
ENV SPARK_APPLICATION_ARGS "foo bar baz"
# Add the python egg for inter-package dependancies 
# on the --packages flag we add spark dependancies that otherwise would be built by sbt
ENV SPARK_SUBMIT_ARGS="--packages org.mongodb.spark:mongo-spark-connector_2.11:2.4.0 --py-files app/dist/pyspark_recom_engine-0.1-py3.6.egg"

CMD ["/bin/bash","/template.sh","/submit.sh"]
```
Unlike our previous Dockerfiles this one is a little bit more complicated, but bear with me. At first we will be extending our image from the base BDE spark images and copying the entire source code into the container. Then we need to define the following environmental variables inside the container:
* `SPARK_MASTER_NAME`: Defines the name given to our spak-master, we could have changed this variable inside our docker image for our spark-master.
* `SPARK_MASTER_PORT`: The port inside the container from which the spark-master is being executed.
* `SPARK_MASTER_URL`: The URL to access the spark master.
* `SPARK_APPLICATION_PYTHON_LOCATION`: Sets the location of the job that we will be submitting into the spark-master
* `SPARK_APPLICATION_ARGS`: Defines a set of arguments in case we are using an argument parser inside our spark-job
* `SPARK_SUBMIT_ARGS`: The actual submit arguments that will be run by the submit bash script. Since we are going to be using mongodb in the future we are going to import the spark mongo connector. More on how `pyspark_recom_engine-0.1-py3.6.egg` gets built will follow.

That was a lot, wasn't it? Well, we aren't finished yet, we still need to define a few more files.
<div class="input">
  MY_PROJECT_NAME/pyspark_src/setup.py
</div>
```python
from setuptools import setup , find_packages

# Parse the requirements form a requirements.txt file
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

requirements = parse_requirements('requirements.txt')

setup(
    name="pyspark_recom_engine",
    version="0.1",
    author="<YOUR_NAME_HERE>",
    author_email="<YOUR_EMAIL_HERE>",
    description="Spark fp-growth recommendation engine using spark",
    url="<YOUR_URL_HERE>",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
```
We are building a python package so we need a `setup.py` file that we will use to build our project into a python egg. The `name` variable could be anything, but since we created a `pyspark_recom_engine` directory, we will name our package that way. Remember the `pyspark_recom_engine-0.1-py3.6.egg` well, this is how it gets built, the `setup.py` file generates that name using the given `version` and `name` arguments as well as the current version of python in which it was built, this is why it is always a good idea to isolate your packages inside a virtual environment. 

Finally the `template.sh` file:
<div class="input">
  MY_PROJECT_NAME/pyspark_src/template.sh
</div>
```bash
#!/bin/bash

sh /submit.sh
```
Is just a simple script that will execute the `submit.sh` script that was inherited from a base submit image.

### 1.4 Putting it all together
We are really close but not there yet... on the root of our project we need to create the following **docker-compose** file.
<div class="input">
  MY_PROJECT_NAME/docker-compose.yml
</div>
```
version: "3"

services:
  spark-mongo:
    image: mongo
    ports:
      - "27017:27017"
    networks:
      - spark-network
    command: mongod
    volumes:
      - mongodb:/data/db
      - mongodb_config:/data/configdb
  spark-master:
    build:
      context: ./spark_master/
    ports:
      - "7077:7077"
      - "8080:8080"
    networks:
      - spark-network
    depends_on:
      - spark-mongo
  spark-worker-1:
    build:
      context: ./pyspark_worker/
    ports:
      - "8081:8081"
    networks:
      - spark-network
    depends_on:
      - spark-master
      - spark-mongo
  spark-worker-2:
    build:
      context: ./pyspark_worker/
    ports:
      - "8082:8081"
    networks:
      - spark-network
    depends_on:
      - spark-master
      - spark-mongo
networks:
  spark-network:
    external:
      name: spark-network
volumes:
  mongodb:
  mongodb_config:
```
Now, if you have set-up the entire thing correctly, you can start a spark cluster with the following command `docker-compose up`. We will be using *mongo* as a way to store our data, but you could use any other db. To check if everything went correctly, you can enter the next address on your web-browser: `http://localhost:8080/` you should see a running spark-master alongside two registered workers :D. In the next blog post we will see how to submit your spark job to your recently created cluster using a `makefile` that will make our lives easier next time we would want to execute our jobs.

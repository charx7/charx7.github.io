---
type: blog-post
post_id: 3
tags: python, spark, pyspark, docker
author: Carlos Huerta 
title: Association rule mining using the parallel fp-growth algorithm using spark, docker and mongodb (2) 
date: Aug 06 2020 
---

### How to build a scalable recommendation engine ⚙️
This is a continuation of <a  target="_blank" href="https://charx7.me/post/2/">part 1</a> of the series on how to build a scalable recommendation engine.

## 2. Create and submit a job to the docker spark-cluster
By the end of part 1 we still needed to develop and submit our spark job to our cluster, so inside the `jobs` directory create a file named `FpJob.py`. At first, we are going to be using the built-in spark-ml library. In the next part, we will develop the algorithm to gain insight into how our recommendations are being built.

### 2.1 Spark job set-up
Inside our mongo container, we stored our data inside a **transactions** database and a **transactions** collection. In our case the read pyspark data-frame object will be:  
```bash
+--------------------+-------------+--------------------+
|         ProductCode|TransactionID|                 _id|
+--------------------+-------------+--------------------+
|             [44848]|         3932|[5c965c83d771ffb4...|
|      [40694, 44848]|         3935|[5c965c83d771ffb4...|
|             [28306]|         3936|[5c965c83d771ffb4...|
|             [44976]|         3938|[5c965c83d771ffb4...|
|             [43409]|         3941|[5c965c83d771ffb4...|
|             [21442]|         3943|[5c965c83d771ffb4...|
|      [25065, 32817]|         3944|[5c965c83d771ffb4...|
|             [30706]|         3945|[5c965c83d771ffb4...|
|[21442, 26749, 32...|         3946|[5c965c83d771ffb4...|
|      [21414, 43330]|         3950|[5c965c83d771ffb4...|
|             [15572]|         3952|[5c965c83d771ffb4...|
|             [41206]|         3954|[5c965c83d771ffb4...|
|[35059, 40664, 40...|         3955|[5c965c83d771ffb4...|
|      [21138, 33208]|         3957|[5c965c83d771ffb4...|
|             [24756]|         3959|[5c965c83d771ffb4...|
|             [13958]|         3961|[5c965c83d771ffb4...|
|      [28010, 41206]|         3962|[5c965c83d771ffb4...|
|[20702, 21901, 22...|         3963|[5c965c83d771ffb4...|
|             [23642]|         3964|[5c965c83d771ffb4...|
|[23370, 26825, 32...|         3967|[5c965c83d771ffb4...|
+--------------------+-------------+--------------------+
```
The column `ProductCode` contains all the product codes from bought items of a given transaction. The `TransactionID` column is the id of a given transaction, and `_id` is the internal mongodb id given on insert. We have both ids since our transactions do not natively live inside our mongo-db, but we could have only fetched them from our native db instead of building a mongo-db to store our data. This design is up to you 😀 and your company's needs.

<div class="input">
  MY_PROJECT_NAME/pyspark_src/pyspark_recom_engine/jobs/Fp_job.py
</div>
```python
from pyspark.sql import SparkSession
from pyspark.ml.fpm import FPGrowth

def main():
    # Read from the transactions database and transactions collection, this will
    # generate a Dataframe object
    print("Reading from transactions db... \n")
    transactions_data = spark_session.read \
        .format("com.mongodb.spark.sql.DefaultSource") \
        .option("database", "transactions") \
        .option("collection", "transactions") \
        .load()
    print('Our read transactions are of the type: ',type(transactions_data), '\n')

    print("The generated transactions schema is: \n")
    transactions_data.printSchema()
    print("The data fetched from the dbb is: \n")
    transactions_data.show()
    
    product_codes = transactions_data.select("ProductCode")
    fpGrowth = FPGrowth(itemsCol="ProductCode",
                        minSupport=0.0001, minConfidence=0.05)
    
    print('Fitting the model...')
    model = fpGrowth.fit(product_codes)

    # Display frequent itemsets.
    model.freqItemsets.show()

    # Display generated association rules.
    model.associationRules.show(100)

    # transform examines the input items against all the association rules and summarize the
    # consequents as prediction
    model.transform(transactions_data).show()

    # Simple test stuff to write to the db
    print("Writing to the mongodb")
    model.associationRules.write.format(
        "com.mongodb.spark.sql.DefaultSource") \
        .option("database", "transactions") \
        .option("collection", "recommendations") \
        .mode("append") \
        .save()

if __name__ == '__main__':
    # There is a bug that doesnt pass spark session objects when called from another func
    spark_session = SparkSession.builder \
        .appName("recomEngine") \
        .config("spark.mongodb.input.uri", "mongodb://spark-mongo:27017/testdb.myColl") \
        .config("spark.mongodb.output.uri", "mongodb://spark-mongo:27017/testdb.myColl") \
        .config('spark.jars.packages', "org.mongodb.spark:mongo-spark-connector_2.11:2.4.0") \
        .getOrCreate()
    spark_session.sparkContext.setLogLevel("ERROR")  # Set log level to error
    # Execute main method
    main()
```
We used mongo-db to read and write both our transactions and recommendations data, although we could have used any other database or read directly from a file; the advantage of doing it this way is that we can replace both the input and output database URLs `mongodb://spark-mongo:27017/testdb.myColl` to the URL where your data is stored.

### 2.2 Spark job submit and execution.
To submit the job to our spark cluster, we need to create another container; this container will communicate to the spark master and execute the job provided. We also need to build our python package to import all of our inner dependencies without any problems. To build and run both our docker image and our python package, we will use the automation tool `make`, which requires a `makefile` that defines a set of tasks to be executed. 

Create a `makefile` on the root of the project:

<div class="input">
  MY_PROJECT_NAME/makefile
</div>
```makefile
help:
	@echo "submit-app    - Will submit the python prebuilt app into the cluster"
	@echo "package-pyspark-app: - Will package a python egg to submit into spark"

package-pyspark-app:
	@echo "Packaging the python egg to be submitted alongside the job..."
	@(cd ./pyspark_src && python setup.py bdist_egg)

submit-app:
	@echo "Package python app -> Built Docker Image -> Run the Submit container"
	make package-pyspark-app
	@echo "Submiting app into the cluster"
	@docker build --rm -t submit-pyspark-job ./pyspark_src/
	@echo "Image built, now running the submit container" 
	@docker run --rm --name pyspark-app -e ENABLE_INIT_DAEMON=false -p 4040:4040 --network spark-network submit-pyspark-job
	@echo "Removing hanging images..."
	@docker rmi $(shell docker images -f "dangling=true" -q)
```
* The `help` command is just a reminder of the tasks we have defined.
* The `package-pyspark-app` command runs the `setup.py` script, so our package, which contains our pyspark job gets build and then gets deployed into the submit container.
* The `submit-app` command builds the docker image, runs, and connects it via the `spark-network` to the (previously) created spark-cluster.

Note: In order for the `package-pyspark-app` command to properly work, we need to have activated our virtual-environment, which contains the pyspark and other dependencies required to build the python package.

### 2.4 Model Results
The output dataframe of the mined association rules will look something like this:
```bash
+--------------------+----------+--------------------+------------------+
|          antecedent|consequent|          confidence|              lift|
+--------------------+----------+--------------------+------------------+
|             [26758]|   [26772]| 0.19786096256684493|113.28364527629235|
|             [44287]|   [39297]|              0.1125|         154.58625|
|             [44287]|   [39299]|           0.1296875|180.36800986842107|
...
+--------------------+----------+--------------------+------------------+
```
Which contains the product code of the **antecedent**, the recommendation or **consequent** product code, and two qualitative metrics, **confidence** and **lift** which tell us how *sure* we are on our recommendation. In this case, our most confident rule was: if you bought a screwdriver, the model recommends you buy a different type of screwdriver, which is pretty logical. 
Finally, this table is saved into the mongo database and can then be used as a lookup table to check for recommendations on our e-commerce website. 

### 2.5 To put it in a nutshell
Once we have all the architecture set-up it is not that hard to create and submit different spark jobs, to summarize: to submit the ml-lib fp-growth pyspark job we have to do the following:
* Initialize the spark cluster via `docker-compose` using the `docker-compose up` command.
* In the root of our project using the make tool run the `make submit-app` which will build our custom pyspark job and submit it using a custom docker submit image.

In the third part, we are going to take a look into the insights of the **parallel fp-growth** algorithm and implement it ourselves from scratch using only spark core functions.

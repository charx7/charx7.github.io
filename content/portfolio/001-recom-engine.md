---
type: portfolio-post
portfolio_id: 1
tags: spark, python, docker, airflow
author: Carlos Huerta 
title: Product Recommendation Engine
summary: People who also bought X also bought Y... product(s) recommendations for agglobal.com
image_name: market-basket.jpg
date: Aug 21 2020
---
# Summary
I built a products recommendation engine for the e-commerce website agglobal.com a large hardware store vendor in Honduras. The project was done using spark, mongo, docker and python.  First implemented the parallel FP-growth algorithm and then migrated to pyspark.ml library.

# Motivation
After core selling features have been tested and implemented every e-commerce should invest on product recommendations, especially if your catalogue consists of **thousands of products** which **can be very difficult to navigate** and display to the interested customers.  That was the case for agglobal.com whose catalogue contains more than 8000 products.  A recommendations engine can be a useful way to **link** the interested (but sometimes very busy **customer**) with the products they are looking for, even if they do not know the specifics of your products. By using data from previous transactions of physical retail stores, we mined and detected association rules that helped display these recommendations in the product page.

# Challenges
The input data (transactions) consists of millions of rows, so preprocessing to get the desired input to minimize computation time was necessary. Additionally building and deploying the infrastructure which can handle this volume of data was not an easy task. 

# Solutions
By using `docker` as a way to test and deploy the necessary infrastructure; we managed to build a platform-independent microservice oriented architecture that was easy to maintain and deploy locally and eventually in a cloud provider. And by choosing `spark` as our computations engine, we managed to solve for both present and future big-data workloads that agglobal will continue to use for its future projects. 

<div style="text-align: center;">
  <img src="/static/images/docker-spark.png"
      alt=""
      style="text-align: center; margin-right: 10px;
      width: 100%; max-width: 50rem;" />
  </br>
</div>

# Results
Astounding results were found after model development; the mined association rules managed to infer a lot of relevant recommendations such as: if you are buying a hammer, why not purchase some nails? It also managed to find some not so apparent suggestions like (parts) product replacements. A human making product recommendations by hand would have needed months if not years to go through the entire catalogue and suggest relevant items.

All the code is available at the gh repository [Here](https://github.com/charx7/Scalable-Computing-recom-engine).
<div style="text-align: center;">
  <img src="/static/images/recom-example.png"
      alt=""
      style="text-align: center; margin-right: 10px;
      width: 100%; max-width: 50rem;" />
  </br>
</div>

* **Want to try it for yourself?** Go to [agglobal](https://www.agglobal.com) and try it with the product code `035858` (Warning: Spanish)
* **Interested?** Contact me if you would like to implement something similar in your website.

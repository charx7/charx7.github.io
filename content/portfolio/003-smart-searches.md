---
type: portfolio-post
portfolio_id: 3
tags: python, elastic-search, kibana, GCP, airflow
author: Carlos Huerta 
title: Smart Searches
summary: From hummer to hammer e-commerce smart full-text searches ranking and beyond
image_name: search.jpg
date: Aug 24 2020
---
# Summary
We implemented and deployed to GCP services an `Elasticsearch` a full-text real-time smart search engine and `Kibana` for analytics and monitoring, reducing the back-end API server load and improving query response time and relevancy of the results. Additionally, we set-up an Apache `Airflow` workflows service in the back-end server to automate various maintenance tasks. 

# Motivation  

> Every e-commerce has faced the challenge of **query performance** and **relevancy** of the displayed search results. What would your query output be if given a customer query like 'construction materials' if none of your products (or product categories) is exactly named like it?

**Agglobal** faced this same challenge as the past search results were given using a full-text search on just the name of the products, so relevant information contained in other characteristics like product descriptions and product characteristics were not taken into account when producing query outputs. Even though **Agglobal** initial strategy to run a full-text search with raw-SQL on via an API was sufficient, as the amount of traffic and products increased, directly smashing the DB was not such a good idea anymore. This is were Elasticsearch provided a great alternative to 'understand' customer queries better and handle increasingly complex index searches.  

# Challenges
The main challenge we faced when implementing these features; was to keep the newly created Elasticsearch index up to date. Because **product availability** is an essential component when displaying search results, we needed to figure a way to **continually update** product availability without having to maintain a real-time mirror products database.  
The next challenge we faced was the design of the **scoring function** of our retrieved products. The main idea was to keep product name as the most significant field when searching through our data, but also take into account product descriptions, characteristics, availability, profitability and if the product was a recent addition to the catalogue.  

# Solutions
A deployment of apache airflow provided us with the best solution when it came to workflow management as a **constant update** of our Elasticsearch index is now periodic and automatic.  Additionally, by implementing **Airflow** in the back-end, we successfully **automated tasks** that previously were manually handled. 
Several iterations of the most efficient query and scoring function were (and are) continuously being tested. As of right now, the best-found solution utilizes bm-25 (best-matching) similarity score using NLP on our text features using fuzziness to correct for minor spelling mistakes as a base score and then boosts each record using profitability. Then it uses exponential decay the final ranking based on the popularity ranking of our products to give a small boost to already popular products.

# Overview
<div style="text-align: center;">
  <img src="/static/images/ES-workflow.png"
      alt=""
      style="text-align: center; margin-right: 10px;
      width: 100%; max-width: 50rem;" />
  </br>
</div>

# Results
Our initial results are very promising, as queries which previously reported zero results are now effectively outputting the correct products. Some examples:

* **Query('lamparaa colgante')** which tranlates into 'hangingg lamps' (misspelling intended) previously output zero results. Now outputs the following products: 'roof hanging lamps', 'industrial lamps' and some replacement parts like 'photocells'.

* **Query('puntas desarmador')** which is a replacement part of a screwdriver now outputs 'several screwdrivers' and 'screwdriver bits'. An important thing to notice is that the 'screwdriver bits' product was named: 'PUNTAS DES.' in which 'DES.' is an abbreviation of the product 'desarmador' that means screwdriver. 

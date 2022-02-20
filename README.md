# Data-driven-attribution-thesis

Here is the practical step by step on how to use the code and queries in Cypher in this repository to buld a rule based and data-driven attribution models. 

## Step 1. Extracting the data

In order to build an attribution model, first we need data. In my case I have extracted the data from the database the company using SQL query, that can be found in [sql_queries/data_collection_chapter3_sql.md](sql_queries/data_collection_chapter3_sql.md)
The data had the following format: 
![Screenshot 2022-02-20 at 19 25 19](https://user-images.githubusercontent.com/33038445/154858093-352380cd-94b6-4e4c-acd4-351a3feecfbc.png)

After extraction, I applied a cohort analysis to the users that had an active session on the website on the chosen day, to have a sophisticated, and complete user journey with 1 or 2 weeks timeframe.
And lastly I export the data in a csv format, to be able to use in the next step.  

## Step 2. Building rule-based data base with Neo4j. 
Here several steps need to be done as well. 

### 2.1 Importing data to Neo4j database. 

First we need to import the data from the table (relational format) to the nodes and relationshiop format of the graph database. Full query can be found in [cypher_queries_neo4j/data_import_cypher.md](cypher_queries_neo4j/data_import_cypher.md) 

* create constrains 
* load nodes for chosen entities, i.e. user and touchpoint (device and touchpoint in my case) 
* create a relationship between them
 
This will create nodes and relationship between nodes, for all the created entities from the csv file

 ![Screenshot 2022-02-20 at 19 53 33](https://user-images.githubusercontent.com/33038445/154859175-2670947d-7d20-43ac-acc6-7e0fa57177bb.png)

### 2.2 Last-touch attribution model.

Now let's finally build a last-touch attribution model with Neo4j. Full query can be found in [cypher_queries_neo4j/last_and_first_touch_attribution.md](cypher_queries_neo4j/last_and_first_touch_attribution.md)

Basically in the query we do the following steps: 
* sort the touchpoints by timestamp in chronologocal order - from the ones that happened forst to the ones that happened last
* create a collection of those timestamps  
* create a relationship to each Touchpoint node, that is the last in the collection of timestamps. 

We do similar data manipulation, but taking the first timestap from the copllection, instead of the last on for first-touch attribution model. As a result we find out which of the timestamp was the last one in the user journey, and we can see it with the relationship in the Neo4j interface: 
![Screenshot 2022-02-20 at 20 03 28](https://user-images.githubusercontent.com/33038445/154859643-983d6c3b-14b5-4e80-9db7-2839f97962f5.png)

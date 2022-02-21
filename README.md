# Using Cypher query language and Neo4j graph database for building first-, last-touch, and linear attribution models 

Here is the practical step by step on how to use the code and queries in Cypher in this repository to buld a rule based first/last-touch and linear attribution models, using Neo4j graph database. 

## Step 1. Extracting the data

In order to build an attribution model, first we need data. In my case I have extracted the data from the database of my company using SQL query, that can be found in [sql_queries/data_collection_chapter3_sql.md](sql_queries/data_collection_chapter3_sql.md)
The data had the following format: 
![Screenshot 2022-02-20 at 19 25 19](https://user-images.githubusercontent.com/33038445/154858093-352380cd-94b6-4e4c-acd4-351a3feecfbc.png)

After extraction, I applied a cohort analysis to the users that had an active session on the website on the chosen day, to have a sophisticated, and complete user journey within 1 or 2 weeks timeframe.
And lastly I export the data in a csv format, to be able to use in the next step.  

## Step 2. Building rule-based data base using Cypher and Neo4j. 
Here several steps need to be done as well. 

### 2.1 Importing data to Neo4j database. 

First we need to import the data from the table(relational format) stored in csv file to the nodes and relationshiop format of the graph database. Full query can be found in [cypher_queries_neo4j/data_import_cypher.md](cypher_queries_neo4j/data_import_cypher.md) 

* create constrains 
* load nodes for chosen entities, i.e. user and touchpoint (device and touchpoint in my case) 
* create a relationship between them
 
This will create nodes and relationship between nodes, for all the created entities from the csv file

 ![Screenshot 2022-02-20 at 19 53 33](https://user-images.githubusercontent.com/33038445/154859175-2670947d-7d20-43ac-acc6-7e0fa57177bb.png)


### 2.2 Last-touch attribution model.

> Last-touch attribution model is a singe-touch attribution model, and  assigns all the creadit of the attributiom to the last touchpoint of the user journey. 


Now let's finally build a last-touch attribution model with Neo4j. Full query can be found in [cypher_queries_neo4j/last_and_first_touch_attribution.md](cypher_queries_neo4j/last_and_first_touch_attribution.md)

In the query we do the following steps: 
* create the collection of timestamps
* sort them sequentially
* take the **last** timestamp from the collection: 
```Cypher 
WHERE t.timestamp = touchSequence[touchpoints-1]
```
* create a relationship with "LAST_TOUCH" name that relates to the node itself (the **last** node in the collection of timestamps):  
```Cypher 
MERGE (t)-[m:LAST_TOUCH {attributionModel:'last-touch', attributionTouchSeq: 1, attributionWeight: 1.0, numOfTouchpoints: touchpoints}]->(t)
```
Apart from the attribution model name *attributionModel*, there is extra information added to the relationship:
- *attributionTouchSeq* - the touchpoint position relative to the sequence (i.e. first, second, third touchpoint of the user journey;
- *attributionWeight* - weight of the attribution set to 1.0; 
- *numOfTouchpoints* - the number of touchpoints in the user journey.   

### 2.3 First-touch attribution model.

>First-touch attribution model is a singe-touch attribution model, and  assigns all the creadit of the attributiom to the first touchpoint of the user journey. 

To build a first touch attribution model we need to use the same query as for the last touch and change our query a bit. Full query can be found in [cypher_queries_neo4j/last_and_first_touch_attribution.md](cypher_queries_neo4j/last_and_first_touch_attribution.md)

In the query similarly to the last-touch model we do the following steps: 
* create the collection of timestamps
* sort them sequentially
* take the **first** timestamp from the collection: 
```Cypher 
WHERE t.timestamp = touchSequence[0]
```
* create a relationship with "FIRST_TOUCH" name that relates to the node itself (the **first** node in the collection of timestamps):  
```Cypher 
MERGE (t)-[m:FIRST_TOUCH {attributionModel:'first-touch', attributionTimeSeq: touchpoints, attributionWeight: 1.0, attributionTouches: touchpoints}]->(t)
```
The attribution model will be instantiated in a form of relationship that will be related to the node itself. It allows the user to have as many models as possible, and the model represents a unique trajectory of chronological touches specific to the certain device. 

As you can see on the screenshot below, now we have both first and last touch attribution models in a form of a relationship. 
 
![Screenshot 2022-02-20 at 20 03 28](https://user-images.githubusercontent.com/33038445/154859643-983d6c3b-14b5-4e80-9db7-2839f97962f5.png)


### 2.4 Linear attribution model.

>Linear attribution model is a multi-touch attribution model, and uses weighted modelling to distribute the credit among touchpoints. 

To build it in the Neo4j we need to do follwoing steps: 
* create the collection of timestamps as we did for first and last-touch models
* use Cypher list function RANGE() for generating a range of integers that represent a sequence of touchpoints
```Cypher 
WITH d, count(*) AS touchpoints, collect(t.timestamp) AS touchCollection, RANGE(count(*),1,-1) as touchpointsRange
```
* then use UNWIND() method to transforms any list back to the individual rows. Each value from the range can be used as an input value for LINEAR_TOUCH attribution relationship and for calculating the weight for each touchpoint: 
```Cypher 
WITH d, touchpoints, touchSequence[touchpoints-seq] as ts, seq, 1/toFloat(touchpoints) as linear_touch_wt
```
* create a relationship with "LINEAR_TOUCH" name that relates to the node itself (the weight of the attribution is spread through all touchpoints of the device):  
```Cypher 
MERGE (t)-[m:LINEAR_TOUCH {attributionModel:'linear-touch',
attributionTouchSeq: (touchpoints-seq+1), attributionWeight: linear_touch_wt, numOfTouchpoints: touchpoints}]->(t)
```

 Full query can be found in [cypher_queries_neo4j/linear_attribution.md](cypher_queries_neo4j/linear_attribution.md)
 Now each node that reprsent the Touchpount has a Linear attribution relationship to itself, with the attributed weight, as shown on the screenshot below: 
 
![Screenshot 2022-02-21 at 10 50 22](https://user-images.githubusercontent.com/33038445/154930451-9be4cda5-423e-402e-91d6-0d1ca59b9579.png)

## Step 3. Calculating the conversion value of attribution models using Cypher and Neo4j. 

We have built the first, last-touch and linear attribution models. However we also want to find out what conversion rate each of them bring, after all that's what attribution models are used for.

For that we can use a Cypher query for the last- and first-touch attribution models, that calculates the contribution to conversion of each marketing channel in the scope of the attribution model. That means that the maximum contribution is calculated from all touchpoints that happened only in the scope of the attribution model, i.e. in the last or first touchpoints of the user journey:  

```Cypher 
MATCH (t:Touchpoint) WITH SUM((toInteger(t.leadouts_Num))) as totalLeadouts
MATCH (t:Touchpoint)-[m:LAST_TOUCH {attributionModel: "last-touch"}]->(t:Touchpoint)
WITH totalLeadouts, m.attributionModel as model, t.mkt_channel AS channel, SUM((toInteger(t.leadouts_Num))) as leadoutsCount
RETURN model, channel, totalLeadouts, leadoutsCount, ROUND((toFloat(leadoutsCount)/totalLeadouts)*10000)/100 AS channelConv
ORDER BY leadoutsCount DESC
```

Results can be presented in a form of the chart, and one can clearly see the perfomance of the different marketing channels. It is clear that in the case of my data set, there are 3 main performers, according to all 3 attribution models: *SEO:Generic, SEM:Generic and Direct: Brand*

 ![Screenshot 2022-02-21 at 11 04 59](https://user-images.githubusercontent.com/33038445/154933148-e775e38e-0640-46cd-8469-f691fa5fa114.png)

The queries for calculation can be found in [cypher_queries_neo4j/last_and_first_touch_attribution.md](cypher_queries_neo4j/last_and_first_touch_attribution.md) for first- and last-touch, and in [cypher_queries_neo4j/linear_attribution.md](cypher_queries_neo4j/linear_attribution.md) for linear attribution model. 

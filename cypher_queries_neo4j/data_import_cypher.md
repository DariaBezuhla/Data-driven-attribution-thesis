# Practical part of the chapter 4: Attribution model implementation using graph database Neo4j.

#### Query 1: Cypher query for importing the data retrieved in a csv file, to the graph database Neo4j. 

```cypher
//integrity constraints
CREATE CONSTRAINT UniqueDevice ON (d:Device) ASSERT d.cookie_value IS UNIQUE;
CREATE INDEX FOR (t:Touchpoint) ON (t.revisit_session_id);

//load device nodes
:auto USING PERIODIC COMMIT 1000 
LOAD CSV FROM "file:///NAME.csv" AS row
WITH row[2] AS cookie_value
MERGE (d:Device {cookie_value: cookie_value})
RETURN count(d);

// load Touchpoint nodes
:auto USING PERIODIC COMMIT 1000
LOAD CSV FROM  "file:///NAME.csv" AS row
WITH row[0] AS timestamp, row[1] AS revisit_session_id, row[3] as mkt_channel, row[4] as leadouts_Num
MERGE (t:Touchpoint { revisit_session_id: revisit_session_id, mkt_channel: mkt_channel, timestamp: timestamp, leadouts: leadouts})
RETURN count(t);

// create relationship between device and touchpoint nodes
:auto USING PERIODIC COMMIT 1000 
LOAD CSV WITH HEADERS FROM "file:///NAME.csv" AS row
MATCH(d:Device {cookie_value: row.li_cookie_value})
MATCH(t:Touchpoint {revisit_session_id: row.revisit_session_id, mkt_channel: row.mkt_channel})
MERGE (d)-[rel:TOUCHED]->(t)
RETURN count(rel);
```

------

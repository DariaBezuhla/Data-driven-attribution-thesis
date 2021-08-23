# Practical part of the chapter 4: Attribution model implementation using graph database Neo4j.

#### Query 1: Cypher query for implementing last-touch attribution model.
Timeframe 01.08.21 - 07.08.21

```cypher
//sort the touchpoints by timestamp 
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WITH d, count(*) AS touchpoints, collect(t.timestamp) AS touchCollection
RETURN d.cookie_value, touchpoints, apoc.coll.sort(touchCollection) as touchSequence

//last touch attribution
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WITH d, count(*) AS touchpoints, collect(t.timestamp) AS touchCollection
CALL {
  WITH touchCollection
  RETURN apoc.coll.sort(touchCollection) as touchSequence
}
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WHERE t.timestamp = touchSequence[touchpoints-1]
MERGE (t)-[m:LAST_TOUCH {attributionModel:'last-touch', attributionTimeSeq: 1, attributionWeight: 1.0, attributionTouchpoints: touchpoints}]->(t)
```

------

#### Query 2: Cypher query for calculating the conversion value of every channel in last-touch attribution model.
```cypher
MATCH (t:Touchpoint) WITH SUM((toInteger(t.leadouts_Num))) as totalLeadouts
MATCH (t:Touchpoint)-[m:LAST_TOUCH {attributionModel: "last-touch"}]->(t:Touchpoint)
WITH totalLeadouts, m.attributionModel as model, t.mkt_channel AS channel, SUM((toInteger(t.leadouts_Num))) as leadoutsCount
RETURN model, channel, totalLeadouts, leadoutsCount, ROUND((toFloat(leadoutsCount)/totalLeadouts)*10000)/100 AS channelConv
ORDER BY leadoutsCount DESC
```

------

#### Query 3: Cypher query for implementing first-touch attribution model.
Timeframe 01.08.21 - 07.08.21
```cypher
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WITH d, count(*) AS touchpoints, collect(t.timestamp) AS touchCollection 
CALL {
  WITH touchCollection
  RETURN apoc.coll.sort(touchCollection) as touchSequence 
  }
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WHERE t.timestamp = touchSequence[0]
MERGE (t)-[m:FIRST_TIME {attributionModel:'first-touch', attributionTimeSeq: touchpoints, attributionWeight: 1.0, attributionTouches: touchpoints}]->(t)
```

------

#### Query 4: Cypher query for calculating the conversion value of every channel in first-touch attribution model.
```cypher
MATCH (t:Touchpoint) WITH SUM((toInteger(t.leadouts_Num))) as totalLeadouts
MATCH (t:Touchpoint)-[m:FIRST_TOUCH {attributionModel: "first-touch"}]->(t:Touchpoint)
WITH totalLeadouts, m.attributionModel as model, t.mkt_channel AS channel, SUM((toInteger(t.leadouts_Num))) as leadoutsCount
RETURN model, channel, totalLeadouts, leadoutsCount, ROUND((toFloat(leadoutsCount)/totalLeadouts)*10000)/100  AS channelConv
ORDER BY leadoutsCount DESC
```

------

This code is adapted from a post linked down below, from Michael Moore <br />
Title: Neo4j Use Case: Real-Time Marketing Recommendations <br />
Author: Michael Moore <br />
Date: n.d <br />
Availability: https://gist.github.com/graphadvantage/e71aa70cc30c1625d52274351174438e 
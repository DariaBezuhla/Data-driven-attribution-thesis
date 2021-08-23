# Practical part of the chapter 4: Attribution model implementation using graph database Neo4j.

#### Query 1: Cypher query for implementing linear attribution model.
Timeframe 01.08.21 - 07.08.21

```cypher
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
WITH d, count(*) AS touchpoints, collect(t.timestamp) AS touchCollection, RANGE(count(*),1,-1) as touchpointsRange
CALL {
WITH touchCollection
RETURN apoc.coll.sort(touchCollection) as touchSequence
}
UNWIND touchpointsRange as range
WITH d, touchpoints, touchSequence[touchpoints-seq] as ts, seq, 1/toFloat(touchpoints) as linear_touch_wt
MATCH (d:Device)-[r:TOUCHED]->(t:Touchpoint)
  WHERE t.timestamp = ts
MERGE (t)-[m:LINEAR_TOUCH {attributionModel:'linear-touch',
attributionTouchSeq: (touchpoints-seq+1), attributionWeight: linear_touch_wt, numOfTouchpoints: touchpoints}]->(t)
```

------

#### Query 2: Cypher query for calculating the conversion value of every channel in linear attribution model.
Timeframe 01.08.21 - 07.08.21

```cypher
MATCH (t:Touchpoint) WITH SUM((toInteger(t.leadouts_Num))) as totalLeads
MATCH (t:Touchpoint)-[m:LINEAR_TOUCH {attributionModel: "linear-touch"}]->(t:Touchpoint)
WITH totalLeads, m.attributionModel AS model, t.mkt_channel AS channel,
     SUM((toInteger(t.leadouts_Num))) as leadCount,
     ROUND(AVG(m.attributionWeight)*1000)/1000 AS avgWt
RETURN model, channel, totalLeads, leadCount, avgWt,
       ROUND((toFloat(leadCount)/totalLeads)*10000)/100 + ' %' AS freq
ORDER BY freq DESC
```

------

This code is adapted from a post linked down below, from Michael Moore <br />
Title: Neo4j Use Case: Real-Time Marketing Recommendations <br />
Author: Michael Moore <br />
Date: n.d <br />
Availability: https://gist.github.com/graphadvantage/e71aa70cc30c1625d52274351174438e 
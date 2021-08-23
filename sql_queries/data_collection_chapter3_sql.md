# Practical part of the chapter 3: Data collection and defining user path key characteristics.

#### Query 1: SQL query for the dataset of attribution model. Timeframe 01.07.21 - 07.07.21

To extract data needed for the first data set, I need to do the following operations with the data:

* used CTE (common table expression) in SQL to get data from `fact_leadins` and `fact_leadouts` tables.
* filter data by `date`, and set the time frame for the extracted entries.
* filter data by `country` and `brand`, only to have idealo website in Germany.
* calculate amount of leadouts per touchpoint.
* join two tables using `revisit_session_id identifier`.
* group by `mkt_channel`, `li_trace_timestamp`, `revisit_session_id`, `cookie_value`, `media`, to avoid duplicate entries.


```sql 
-- CTE to extract data from fact_leadins table

with leadin as
(SELECT
  trace_timestamp as li_trace_timestamp,
  revisit_session_id,
  cookie_value,
  mkt_channel
  FROM
    dl_dwh_prod.fact_leadins
  WHERE 1=1
    and date(date_utc) BETWEEN date('2021-07-01') and date('2021-07-07')
    and country LIKE 'DE'
    and brand = 'idealo'
    ),
 
-- CTE to extract data from fact_leadouts table

leadouts as
(SELECT
  revisit_session_id as lo_revisit_session_id,
  leadout_type
FROM 
 dl_dwh_prod.fact_leadouts
where 1=1
   and date(date_utc) BETWEEN date('2021-07-01') and date('2021-07-07')
   and country LIKE 'DE'
   and brand = 'idealo'
)

-- query to join the tables, group by the results and calculate leadouts number

SELECT
    li_trace_timestamp,
    revisit_session_id,
    cookie_value,
    mkt_channel,
    SUM(CASE WHEN leadout_type is not null THEN 1 ELSE 0 END) as Leadouts
  
from leadouts as lo 
inner join leadin as li on lo.lo_revisit_session_id=li.revisit_session_id
 
group by 1,2,3,4
```

------

#### Query 2: SQL query for the dataset of attribution model, using cohort analysis. Timeframe 01.07.21 - 07.07.21

* used CTE userCohort to filter out cookie values that have touchpoints in the first day (01.07.2021) of the defined dataframe.

```sql 
-- users cohort CTE

with userCohort AS 
  (SELECT DISTINCT 
         lo.cookie_value as cohort_cookie_value
    FROM dl_dwh_prod.fact_leadouts AS lo
    INNER JOIN dl_dwh_prod.fact_leadins AS li
        ON lo.cookie_value = li.cookie_value 
    WHERE 1=1
            AND date(li.date_utc) = date('2021-07-01')
            AND date(lo.date_utc) = date('2021-07-01') ),


-- CTE to extract data from fact_leadins table, and filter by cookie_value from user_cohort CTE 

leadins AS 
    (SELECT trace_timestamp AS li_trace_timestamp,
         revisit_session_id,
         cookie_value as li_cookie_value,
         mkt_channel
    FROM dl_dwh_prod.fact_leadins
  
    WHERE 1=1 
            AND date(date_utc) BETWEEN date('2021-07-01') and date('2021-07-07')
            AND country LIKE 'DE'
            AND brand = 'idealo' 
            AND cookie_value IN (SELECT cohort_cookie_value FROM userCohort) ),
 
-- CTE to extract data from fact_leadouts table, and filter by cookie_value from user_cohort CTE 

leadouts AS 
    (SELECT revisit_session_id AS lo_revisit_session_id,
         leadout_type,
         cookie_value AS lo_cookie_value
    FROM dl_dwh_prod.fact_leadouts
    WHERE 1=1
            AND date(date_utc) BETWEEN date('2021-07-01') and date('2021-07-07')
            AND country LIKE 'DE'
            AND brand = 'idealo'
            AND cookie_value IN (SELECT cohort_cookie_value FROM userCohort)  )


-- query to join the tables, group by the results and calculate leadouts number

SELECT 
        li.li_trace_timestamp,
        li.revisit_session_id,
        li.li_cookie_value,
        li.mkt_channel,
        SUM(CASE WHEN lo.leadout_type is NOT NULL THEN 1 ELSE 0 END) AS leadouts_Num
         
FROM leadouts AS lo
INNER JOIN leadins AS li
    ON lo.lo_revisit_session_id=li.revisit_session_id

GROUP BY  1,2,3,4
```

------
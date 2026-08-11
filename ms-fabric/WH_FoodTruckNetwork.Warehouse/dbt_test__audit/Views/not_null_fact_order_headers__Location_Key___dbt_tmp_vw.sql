-- Auto Generated (Do not modify) F4CFF1C73D3C9BD3ED9919C1FFB27A3BB219E8762AD1C1F55499C01BFCB35231
create view [dbt_test__audit].[not_null_fact_order_headers__Location_Key___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[fact_order_headers]
where [Location Key] is null



  ;
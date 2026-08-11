-- Auto Generated (Do not modify) 9B9AAE1F577A1D5F75DFFE1966CA2BE90387FA21F6C828D0696BC3D20928CC10
create view [dbt_test__audit].[not_null_fact_order_details__Order_Time___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[fact_order_details]
where [Order Time] is null



  ;
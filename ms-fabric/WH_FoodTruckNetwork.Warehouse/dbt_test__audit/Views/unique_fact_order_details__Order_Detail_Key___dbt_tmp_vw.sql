-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_fact_order_details__Order_Detail_Key___dbt_tmp_vw] as 
    
    
    

select
    [Order Detail Key] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[fact_order_details]
where [Order Detail Key] is not null
group by [Order Detail Key]
having count(*) > 1



  ;
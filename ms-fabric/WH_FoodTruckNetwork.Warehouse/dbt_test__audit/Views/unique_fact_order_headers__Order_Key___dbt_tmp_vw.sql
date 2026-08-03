-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_fact_order_headers__Order_Key___dbt_tmp_vw] as 
    
    
    

select
    [Order Key] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[fact_order_headers]
where [Order Key] is not null
group by [Order Key]
having count(*) > 1



  ;
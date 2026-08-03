-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_dim_customers__Customer_Key___dbt_tmp_vw] as 
    
    
    

select
    [Customer Key] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_customers]
where [Customer Key] is not null
group by [Customer Key]
having count(*) > 1



  ;
-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_dim_locations__Location_Key___dbt_tmp_vw] as 
    
    
    

select
    [Location Key] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_locations]
where [Location Key] is not null
group by [Location Key]
having count(*) > 1



  ;
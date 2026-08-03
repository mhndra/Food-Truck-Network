-- Auto Generated (Do not modify) 483228C04CACE8BC30D21F5156ECB4EF88132F46E14D34E3FE19214201C815AA
create view [dbt_test__audit].[unique_dim_order_time__Order_Time___dbt_tmp_vw] as 
    
    
    

select
    [Order Time] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_order_time]
where [Order Time] is not null
group by [Order Time]
having count(*) > 1



  ;
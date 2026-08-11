-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_dim_menu_items__Menu_Item_ID___dbt_tmp_vw] as 
    
    
    

select
    [Menu Item ID] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_menu_items]
where [Menu Item ID] is not null
group by [Menu Item ID]
having count(*) > 1



  ;
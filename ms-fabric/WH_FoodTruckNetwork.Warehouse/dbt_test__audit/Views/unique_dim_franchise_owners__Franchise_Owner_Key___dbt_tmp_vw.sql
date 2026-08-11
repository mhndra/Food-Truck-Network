-- Auto Generated (Do not modify) 1495E5C58D42C2A919B34B57FF00123678A25B05EB807504C8F550FD3155ACF3
create view [dbt_test__audit].[unique_dim_franchise_owners__Franchise_Owner_Key___dbt_tmp_vw] as 
    
    
    

select
    [Franchise Owner Key] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_franchise_owners]
where [Franchise Owner Key] is not null
group by [Franchise Owner Key]
having count(*) > 1



  ;
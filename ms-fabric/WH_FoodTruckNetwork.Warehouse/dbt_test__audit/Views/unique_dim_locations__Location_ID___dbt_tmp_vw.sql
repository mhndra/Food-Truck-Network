-- Auto Generated (Do not modify) 8A637CFB1EACAC6C244747E297DD98A3CD59B345D2E5FF49ABEC57D5866E2241
create view [dbt_test__audit].[unique_dim_locations__Location_ID___dbt_tmp_vw] as 
    
    
    

select
    [Location ID] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_locations]
where [Location ID] is not null
group by [Location ID]
having count(*) > 1



  ;
-- Auto Generated (Do not modify) 8A637CFB1EACAC6C244747E297DD98A3CD59B345D2E5FF49ABEC57D5866E2241
create view [dbt_test__audit].[unique_dim_customers__Customer_ID___dbt_tmp_vw] as 
    
    
    

select
    [Customer ID] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_customers]
where [Customer ID] is not null
group by [Customer ID]
having count(*) > 1



  ;
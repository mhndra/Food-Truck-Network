-- Auto Generated (Do not modify) 8A637CFB1EACAC6C244747E297DD98A3CD59B345D2E5FF49ABEC57D5866E2241
create view [dbt_test__audit].[unique_fact_order_headers__Order_ID___dbt_tmp_vw] as 
    
    
    

select
    [Order ID] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[fact_order_headers]
where [Order ID] is not null
group by [Order ID]
having count(*) > 1



  ;
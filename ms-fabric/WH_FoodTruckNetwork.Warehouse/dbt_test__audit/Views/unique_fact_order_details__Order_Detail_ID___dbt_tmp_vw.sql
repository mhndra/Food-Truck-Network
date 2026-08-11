-- Auto Generated (Do not modify) 8A637CFB1EACAC6C244747E297DD98A3CD59B345D2E5FF49ABEC57D5866E2241
create view [dbt_test__audit].[unique_fact_order_details__Order_Detail_ID___dbt_tmp_vw] as 
    
    
    

select
    [Order Detail ID] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[fact_order_details]
where [Order Detail ID] is not null
group by [Order Detail ID]
having count(*) > 1



  ;
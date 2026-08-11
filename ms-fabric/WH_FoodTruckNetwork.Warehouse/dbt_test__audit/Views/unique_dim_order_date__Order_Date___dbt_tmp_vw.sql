-- Auto Generated (Do not modify) C73F0633953F06D139D15BE3A66C509D9559076EC4405F9DED819764318027CC
create view [dbt_test__audit].[unique_dim_order_date__Order_Date___dbt_tmp_vw] as 
    
    
    

select
    [Order Date] as unique_field,
    count(*) as n_records

from [WH_FoodTruckNetwork].[gold].[dim_order_date]
where [Order Date] is not null
group by [Order Date]
having count(*) > 1



  ;
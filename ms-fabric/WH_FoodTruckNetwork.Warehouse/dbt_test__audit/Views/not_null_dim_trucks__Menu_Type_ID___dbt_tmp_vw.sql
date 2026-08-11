-- Auto Generated (Do not modify) 0804C56F85EDBE62A74BA74F0B873C15C5846119EBA11A77BE20306DABF3A361
create view [dbt_test__audit].[not_null_dim_trucks__Menu_Type_ID___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_trucks]
where [Menu Type ID] is null



  ;
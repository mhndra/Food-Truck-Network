-- Auto Generated (Do not modify) 0254721233CDDBF1C89A69FF7CFB27A28BAC6AD786A8F8AA860FAB1F6DD2DD44
create view [dbt_test__audit].[not_null_dim_order_date__Year___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_order_date]
where [Year] is null



  ;
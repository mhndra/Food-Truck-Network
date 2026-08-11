-- Auto Generated (Do not modify) 76FE00D98C2B47FD0CD0F7D0CA689137C7354DC13964CB419393C0E5FDD6BA35
create view [dbt_test__audit].[not_null_dim_customers__Phone_Number___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_customers]
where [Phone Number] is null



  ;
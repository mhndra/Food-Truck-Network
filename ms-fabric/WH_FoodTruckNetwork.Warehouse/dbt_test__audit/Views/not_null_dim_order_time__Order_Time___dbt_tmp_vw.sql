-- Auto Generated (Do not modify) EC50018DCF2EC4673766135D9B4ABADA87D6340AE32D1708D6BC0C3FD119582B
create view [dbt_test__audit].[not_null_dim_order_time__Order_Time___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_order_time]
where [Order Time] is null



  ;
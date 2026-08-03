-- Auto Generated (Do not modify) 20F0C1FCE1F34743028107A8C353770FBB6F9E3101D0176AA7908BD7A49B965E
create view [dbt_test__audit].[not_null_dim_locations__Loaded_at_UTC___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_locations]
where [Loaded at (UTC)] is null



  ;
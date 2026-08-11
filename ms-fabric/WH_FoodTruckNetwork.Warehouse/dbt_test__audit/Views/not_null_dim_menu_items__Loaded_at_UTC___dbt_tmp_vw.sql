-- Auto Generated (Do not modify) 17AEC3E7905F2D3098366C253C1316D9E0FEF27D2D04BFD30112AC0C97FD84FB
create view [dbt_test__audit].[not_null_dim_menu_items__Loaded_at_UTC___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_menu_items]
where [Loaded at (UTC)] is null



  ;
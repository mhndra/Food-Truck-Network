-- Auto Generated (Do not modify) 30692ED2664DB17457766A0782505793E7142486FB6BC493D16473356D0BDDD0
create view [dbt_test__audit].[not_null_dim_franchise_owners__Franchise_City_Grouped___dbt_tmp_vw] as 
    
    
    



select *
from [WH_FoodTruckNetwork].[gold].[dim_franchise_owners]
where [Franchise City Grouped] is null



  ;
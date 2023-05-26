########################################################################################################################
# File name: Prepare_Parcels.py
# Author: Mike Gough
# Date created: 05/02/2023
# Python Version: 3.x (ArcGIS Pro)/(Should work in 2.7 (ArcGIS Desktop))
# Description:
# Prepares parcels for the Requirements and Exemptions Script.
# Performs the following tasks:
# 1. Projects the statewide parcels dataset and deletes parcels with duplicate geometries.
# 2. Adds and calculates additional fields needed but not provided (e.g., a unique id).
# 3. Calculates the zip code for each parcel.
# 4. Cleans up fields and field names.
# 5. Separates the state-wide parcels dataset into individual county datasets.

# Total Runtime: ~10.5 hrs

########################################################################################################################

import arcpy
import os
import datetime

arcpy.env.overwriteOutput = True

start_script = datetime.datetime.now()
print("Start Script: " + str(start_script))

# Input Parameters:
statewide_parcels_source_fc = r"\\loxodonta\gis\Source_Data\planningCadastre\state\CA\SiteCheck_Parcels_2023\SiteCheck_Parcels.gdb\Statewide_Parcels"
zip_codes_source_fc = r"\\loxodonta\gis\Source_Data\boundaries\state\CA\Zip_Code_Boundaries\California_Zip_Codes\cfd6f01a-9af0-4ebc-ab36-4d380d185c12.gdb\California_Zip_Codes"
mpo_source_fc = r"\\loxodonta\gis\Source_Data\boundaries\state\CA\MPO_Boundaries\Metropolitan Planning Organization (MPO), California\data\commondata\metopolitan_planning_organization_mpo\MPO_2013.shp"
# Justin's project version of specific plans
specific_plan_source_fc = r"\\loxodonta\gis\Projects\CEQA_Site_Check_Version_2_0_2023\Workspaces\CEQA_Site_Check_Version_2_0_2023_justin_heyerdahl\Data\IntermediateData.gdb\NAD83_Projected\req2_6_specificplan_coverage"
zoning_source_fc = r"\\loxodonta\gis\Source_Data\planningCadastre\state\CA\Zoning\From_Mark_Hedlund_OPR\20230522\export.gdb\Lat_long\CaliforniaZoning"
tmp_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Scratch\Scratch.gdb"
input_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb"

test_parcels = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Test_Parcels\Test_Parcels.gdb\ALAMEDA_Parcels"

# Field Names:
cbi_parcel_id_field = "cbi_parcel_id_fips_apn_oid"
zoning_field = "ucd_description" # The field in the zoning dataset that contains the zoning designation.

# Output Parameters:
output_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Prepared_By_County.gdb"
statewide_parcels_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_Proj_No_Dups"
statewide_parcels_input_fc_with_zip = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip"
statewide_parcels_input_fc_with_zip_mpo = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO"
statewide_parcels_input_fc_with_zip_mpo_sp = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP"
statewide_parcels_input_fc_with_zip_mpo_sp_zoning = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP_Zoning"
zip_codes_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\California_Zip_Codes_Projected"

output_crs = arcpy.SpatialReference(3310)  # NAD_1983_California_Teale_Albers


def project_and_delete_dups():
    """ Function to project the state-wide parcels dataset provided by OPR and delete parcels with duplicate
    geometry. ~1hr"""

    print("\nProjecting and Deleting Duplicate Parcels...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nProjecting...")

    input_crs = arcpy.Describe(zoning_source_fc).SpatialReference
    datum = input_crs.gcs.name
    if datum == "GCS_North_American_1983":
        datum_transformation = "WGS_1984_(ITRF00)_To_NAD_1983"
    else:
        datum_transformation = ""

    arcpy.Project_management(
        in_dataset=statewide_parcels_source_fc,
        out_dataset=statewide_parcels_input_fc,
        out_coor_system=output_crs,
        transform_method=datum_transformation,
        in_coor_system=input_crs,
        preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    end = datetime.datetime.now()
    print("End: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))

    print("\nDeleting Identical...")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    arcpy.DeleteIdentical_management(statewide_parcels_input_fc, "SHAPE")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def add_and_calculate_fields():
    """ Function to add and calculate fields to the prepared state-wide parcels dataset. ~8hrs"""

    print("\nAdding and calculating fields...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    fields = [field.name.lower() for field in arcpy.ListFields(statewide_parcels_input_fc)]

    print("\nID Field...")  # Note: the values in fips_apn are not unique even with duplicates removed.

    if cbi_parcel_id_field not in fields:
        arcpy.AddField_management(statewide_parcels_input_fc, cbi_parcel_id_field, "TEXT")

    with arcpy.da.UpdateCursor(statewide_parcels_input_fc, ["fips_apn", "OBJECTID", cbi_parcel_id_field]) as uc:
        for row in uc:
            if row[0]:
                unique_id = "_".join([row[0], str(row[1])])
            else:
                unique_id = "_".join(["no_fips_apn_", str(row[1])])
            row[2] = unique_id
            uc.updateRow(row)

    print("\nState Field...")

    cbi_state_field = "state_name"
    if cbi_state_field not in fields:
        arcpy.AddField_management(statewide_parcels_input_fc, cbi_state_field, "TEXT")
    arcpy.CalculateField_management(statewide_parcels_input_fc, cbi_state_field, "\"California\"")

    print("\nLatitude Field...")

    cbi_lat_field = "latitude"
    if cbi_lat_field not in fields:
        arcpy.AddField_management(statewide_parcels_input_fc, cbi_lat_field, "DOUBLE")
    arcpy.CalculateGeometryAttributes_management(statewide_parcels_input_fc, [[cbi_lat_field, "CENTROID_Y"]], "", "", "", "DD")

    print("\nLongitude Field...")

    cbi_lon_field = "longitude"
    if cbi_lon_field not in fields:
        arcpy.AddField_management(statewide_parcels_input_fc, cbi_lon_field, "DOUBLE")
    arcpy.CalculateGeometryAttributes_management(statewide_parcels_input_fc, [[cbi_lon_field, "CENTROID_X"]], "", "", "", "DD")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def calc_zip_codes():
    """ Function to join the zip codes to the prepared state-wide parcels dataset (spatial join that takes the zip
    code coinciding with the centroid of the parcel). Duration: ~1 hour """

    print("\nCalculating zip codes...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nProjecting zip codes...")

    arcpy.Project_management(
        in_dataset=zip_codes_source_fc,
        out_dataset=zip_codes_input_fc,
        out_coor_system="PROJCS['NAD_1983_California_Teale_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',-4000000.0],PARAMETER['Central_Meridian',-120.0],PARAMETER['Standard_Parallel_1',34.0],PARAMETER['Standard_Parallel_2',40.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
        transform_method="WGS_1984_(ITRF00)_To_NAD_1983",
        in_coor_system="PROJCS['WGS_1984_California_Teale_Albers_FtUS',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',-4000000.0],PARAMETER['Central_Meridian',-120.0],PARAMETER['Standard_Parallel_1',34.0],PARAMETER['Standard_Parallel_2',40.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]]",
        preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    print("\nPerforming a spatial join with parcels and zip codes...")

    arcpy.SpatialJoin_analysis(statewide_parcels_input_fc, zip_codes_input_fc, statewide_parcels_input_fc_with_zip,
                               "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               'fips "fips" true true false 8 Text 0 0,First,#,Statewide_Parcels,fips,0,8;county_name "county_name" true true false 32 Text 0 0,First,#,Statewide_Parcels,county_name,0,32;fips_apn "fips_apn" true true false 30 Text 0 0,First,#,Statewide_Parcels,fips_apn,0,30;apn "apn" true true false 20 Text 0 0,First,#,Statewide_Parcels,apn,0,20;apn_d "apn_d" true true false 17 Text 0 0,First,#,Statewide_Parcels,apn_d,0,17;s_city "s_city" true true false 50 Text 0 0,First,#,Statewide_Parcels,s_city,0,50;s_addr_d "s_addr_d" true true false 52 Text 0 0,First,#,Statewide_Parcels,s_addr_d,0,52;cbi_parcel_id_fips_apn_oid "cbi_parcel_id_fips_apn_oid" true true false 255 Text 0 0,First,#,Statewide_Parcels,cbi_parcel_id_fips_apn_oid,0,255;state_name "state_name" true true false 255 Text 0 0,First,#,Statewide_Parcels,state_name,0,255;latitude "latitude" true true false 8 Double 0 0,First,#,Statewide_Parcels,latitude,-1,-1;longitude "longitude" true true false 8 Double 0 0,First,#,Statewide_Parcels,longitude,-1,-1;zip_code "Zip Code" true true false 10 Text 0 0,First,#,California_Zip_Codes_Projected,ZIP_CODE,0,10',
                               "HAVE_THEIR_CENTER_IN", None, '')

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def join_mpo_name(input_fc):
    """ Joins the MPO Name from the MPO boundary that a parcel falls within. """

    print(" Joining MPO name to parcels...")

    output_fc = statewide_parcels_input_fc_with_zip_mpo

    start = datetime.datetime.now()
    print("Start: " + str(start))

    arcpy.SpatialJoin_analysis(
        target_features=input_fc,
        join_features=mpo_source_fc,
        out_feature_class=output_fc, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL",
        field_mapping="",
        match_option="HAVE_THEIR_CENTER_IN", search_radius="", distance_field_name="")

    # Doesn't work when only changing case.
    arcpy.AlterField_management(output_fc,"MPO", "mpo")
    arcpy.AlterField_management(output_fc,"Label_MPO", "label_mpo")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def join_specific_plan_name(input_fc):
    """ Joins the Specific Plan Name from the specific plan boundary that a parcel falls within. """

    print(" Joining Specific Plan name to parcels...")

    output_fc = statewide_parcels_input_fc_with_zip_mpo_sp

    start = datetime.datetime.now()
    print("Start: " + str(start))

    arcpy.MakeFeatureLayer_management(
        in_features=specific_plan_source_fc,
        out_layer="specific_plan_layer", where_clause="", workspace="",
        field_info="OBJECTID OBJECTID VISIBLE NONE;Shape Shape HIDDEN NONE;MPO_Code MPO_Code HIDDEN NONE;MPO_Name MPO_Name HIDDEN NONE;SP_Name SP_Name VISIBLE NONE;County_Name County_Name HIDDEN NONE;City_Name City_Name HIDDEN NONE;Type Type HIDDEN NONE;Acres Acres HIDDEN NONE;Source_Date Source_Date HIDDEN NONE;Source_Data Source_Data HIDDEN NONE;YrSP_Adopted YrSP_Adopted HIDDEN NONE;YrSP_LastUP YrSP_LastUP HIDDEN NONE;Website Website HIDDEN NONE;SiteCheck SiteCheck HIDDEN NONE;QUERY QUERY HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;Shape_Area Shape_Area HIDDEN NONE")

    arcpy.SpatialJoin_analysis(target_features=input_fc, join_features="specific_plan_layer", out_feature_class=output_fc, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping="", match_option="HAVE_THEIR_CENTER_IN", search_radius="", distance_field_name="")

    arcpy.AlterField_management(output_fc,"SP_Name", "Specific_Plan")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def join_zoning_designations(input_fc, threshold):
    """ Joins the Zoning Designation to each parcel based on the % coverage threshold. """

    print("Performing Zoning Data Calculations...")

    separate_fields = False  # indicates whether zoning designation and % cover should go in separate fields or not.

    start = datetime.datetime.now()
    print("Start: " + str(start))

    zoning_projected = input_gdb + os.sep + "California_Zoning_Projected"

    if not arcpy.Exists(zoning_projected):
        print("Projecting zoning data....")

        input_crs = arcpy.Describe(zoning_source_fc).SpatialReference
        datum = input_crs.gcs.name
        if datum == "GCS_North_American_1983":
            datum_transformation = "WGS_1984_(ITRF00)_To_NAD_1983"
        else:
            datum_transformation = ""

        arcpy.Project_management(
            in_dataset=zoning_source_fc,
            out_dataset=zoning_projected,
            out_coor_system=output_crs,
            transform_method=datum_transformation,
            in_coor_system=input_crs,
            preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")
    else:
        print("Zoning data has already been projected.")

    tabulate_intersection_table_name = "Tabulate_Zoning_Intersection"
    tabulate_intersection_table = tmp_gdb + os.sep + tabulate_intersection_table_name

    if not arcpy.Exists(tabulate_intersection_table):
        print("Tabulating Intersection (% zoning designation within each parcel)...")
        arcpy.TabulateIntersection_analysis(
            in_zone_features=input_fc,
            zone_fields=cbi_parcel_id_field,
            in_class_features=zoning_projected,
            out_table=tabulate_intersection_table,
            class_fields=zoning_field, sum_fields="", xy_tolerance="-1 Unknown", out_units="UNKNOWN")
    else:
        print("Tabulation table already exists.")

    # Note: Creating a query table of records > threshold and joining to input fc took took too long.
    print("Creating a dictionary of parcel_id: {zoning_designation='', percent_cover = ''} where pecent_cover is > " + str(threshold))
    zoning_dict = {}
    with arcpy.da.SearchCursor(tabulate_intersection_table, [cbi_parcel_id_field, zoning_field, "PERCENTAGE"]) as sc:
        for row in sc:
            parcel_id = row[0]
            zoning_designation = row[1]
            percent_cover = round(row[2], 1)
            if percent_cover >= threshold:
                if parcel_id not in zoning_dict:
                    zoning_dict[parcel_id] = {}
                zoning_dict[parcel_id][zoning_designation] = percent_cover

    # Delete and add fields each run in case zoning data changes (don't want residual values).
    print("Adding Zoning_Designation field...")
    arcpy.DeleteField_management(input_fc, "Zoning_Designation")
    arcpy.AddField_management(input_fc, "Zoning_Designation", "TEXT")

    print("Adding Percent_Cover field...")
    arcpy.DeleteField_management(input_fc, "Zoning_Percent_Cover")
    if separate_fields:
        arcpy.AddField_management(input_fc, "Zoning_Percent_Cover", "TEXT")

    print("Getting zoning designation and percent cover values for each parcel...")
    if separate_fields:
        fields_to_calc = [cbi_parcel_id_field, "Zoning_Designation", "Zoning_Percent_Cover"]
    else:
        fields_to_calc = [cbi_parcel_id_field, "Zoning_Designation"]

    with arcpy.da.UpdateCursor(input_fc, fields_to_calc) as uc:
        for row in uc:
            parcel_id = row[0]
            if parcel_id in zoning_dict:
                print(zoning_dict[parcel_id])
                zoning_designations = []
                percentages = []
                if separate_fields:
                    for k,v in zoning_dict[parcel_id].items():
                        zoning_designations.append(k)
                        percentages.append(str(v))
                    # Set the Zoning Designations and Percent Cover
                    print(zoning_designations)
                    print(percentages)
                    row[1] = ",".join(zoning_designations)
                    row[2] = ",".join(percentages)
                else:
                    print(zoning_dict[parcel_id])
                    row[1] = str(zoning_dict[parcel_id])
                uc.updateRow(row)

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def clean_up_fields(input_fc, fields_to_delete=None, fields_to_remove_alias=None):
    """ Function to delete extraneous fields and remove aliases from the state-wide dataset. ~8hrs """

    print("\nCleaning up fields...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    if fields_to_delete:
        print("\nDeleting Extraneous fields...")

        for field in fields_to_delete:
            print(field)
            arcpy.DeleteField_management(input_fc, field)

    if fields_to_remove_alias:
        print("\nRemoving field aliases...")

        for field in fields_to_remove_alias:
            arcpy.AlterField_management(statewide_parcels_input_fc_with_zip, field, "", "", "", "", "", "CLEAR_ALIAS")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def separate_into_counties(input_fc):
    """ Function to separate state-wide parcels dataset into separate parcel datasets for each county. ~1.5hrs"""

    print("\nSeparating parcels by county...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nGathering a list of county names...")

    county_name_list = []
    with arcpy.da.SearchCursor(input_fc, ["county_name"]) as sc:
        for row in sc:
            county_name = row[0]
            if county_name not in county_name_list:
                county_name_list.append(county_name)

    print("\nCreating separate parcel datasets for each county...")

    for county_name in county_name_list:
        print(county_name)
        output_county_name = county_name.replace(" County", "").replace(" ", "").upper() + "_Parcels"
        output_county_parcels_fc = output_gdb + os.sep + output_county_name
        expression = "county_name = '" + county_name + "'"
        arcpy.Select_analysis(input_fc, output_county_parcels_fc, expression)

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))

#project_and_delete_dups()
#add_and_calculate_fields()
#calc_zip_codes()
#join_mpo_name(input_fc=statewide_parcels_input_fc_with_zip)
#join_specific_plan_name(input_fc=statewide_parcels_input_fc_with_zip_mpo)
join_zoning_designations(input_fc=test_parcels, threshold=10)

#clean_up_fields(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp, ["Shape_Length_1", "Shape_Area_1", "Join_Count", "TARGET_FID", "Join_Count_1", "TARGET_FID_1"])
#separate_into_counties(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp)

end_script = datetime.datetime.now()
print("\nEnd Script: " + str(end_script))

duration = end_script - start_script
print("Total Duration: " + str(duration))

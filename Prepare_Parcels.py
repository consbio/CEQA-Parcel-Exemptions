########################################################################################################################
# File name: Prepare_Parcels.py
# Author: Mike Gough
# Date created: 05/02/2023
# Python Version: 3.x (ArcGIS Pro)/(Should work in 2.7 (ArcGIS Desktop))
# Description:
# Prepares parcels for the Requirements and Exemptions Script.
# Performs the following tasks:
# 1. Projects the statewide parcels dataset and deletes parcels with duplicate geometries.
# 2. Explodes multi-part features into single-part features.
# 3. Adds and calculates additional fields needed but not provided (e.g., a unique id).
# 4. Calculates the zip code for each parcel, mpo, specific plan, and zoning designation(s).
# 5. Cleans up fields and field names.
# 6. Separates the state-wide parcels dataset into individual county datasets.

# Total Runtime: ~18 hrs

########################################################################################################################

import arcpy
import os
import datetime
import json
import csv

arcpy.env.overwriteOutput = True

appdata_dir = os.environ.get("APPDATA")
favorites_dir = appdata_dir + "\Esri\ArcGISPro\Favorites"

start_script = datetime.datetime.now()
print("Start Script: " + str(start_script))

# Input Parameters:
statewide_parcels_source_fc = r"\\loxodonta\gis\Source_Data\planningCadastre\state\CA\SiteCheck_Parcels_2023\SiteCheck_Parcels.gdb\Statewide_Parcels"
zip_codes_source_fc = r"\\loxodonta\gis\Source_Data\boundaries\state\CA\Zip_Code_Boundaries\California_Zip_Codes\cfd6f01a-9af0-4ebc-ab36-4d380d185c12.gdb\California_Zip_Codes"
mpo_source_fc = r"\\loxodonta\gis\Source_Data\boundaries\state\CA\MPO_Boundaries\Metropolitan Planning Organization (MPO), California\data\commondata\metopolitan_planning_organization_mpo\MPO_2013.shp"
zoning_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Zoning\Zoning.gdb\california_zoning_opr_20230921_prepared"
zip_codes_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\California_Zip_Codes_Projected"
census_block_source_fc = r"\\loxodonta\gis\Source_Data\society\state\CA\Census\2022\tl_2022_06_tabblock20\tl_2022_06_tabblock20.shp"

# Justin's ucd_zoning lookup:
code_to_ucd_zoning_lookup = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\CAZoning_Lookup.csv"

# Justin's most recent version of specific plans (01/16/2024):
specific_plan_source_fc = favorites_dir + r"\CBI Intermediate.sde\cbiintermediate.justin_heyerdahl.req2_6_SpecificPlan_Coverage_20240116"

tmp_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Scratch\Scratch.gdb"
input_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb"

#test_parcels = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Test_Parcels\Test_Parcels.gdb\ALAMEDA_Parcels_Explode_Subset_3"
#test_parcels = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Test_Parcels\Test_Parcels.gdb\ALAMEDA_Parcels_Explode_Zoning_Field_Description"
test_parcels_with_zoning = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Test_Zoning\Test_Parcels.gdb\Twelve_Parcels_With_Zoning"

# Field Names:
cbi_parcel_id_field = "cbi_parcel_id_fips_apn_oid"
#zoning_field = "ucd_description"  # The field in the zoning dataset that contains the zoning designation.
#zoning_field = "description"  # The field in the zoning dataset that contains the zoning designation.
zoning_field = "Code"  # Mark instructed us to use this field on 08/28/2023
specific_plan_field = "sp_name"

# Output Parameters:
output_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Prepared_By_County.gdb"
statewide_parcels_input_fc_multipart = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_Proj_No_Dups_Multipart"
statewide_parcels_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_Proj_No_Dups_Singlepart"
statewide_parcels_input_fc_with_zip = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip"
statewide_parcels_input_fc_with_zip_mpo = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO"
statewide_parcels_input_fc_with_zip_mpo_sp = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP"
#statewide_parcels_input_fc_with_zip_mpo_sp_zoning = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP_Zoning"
statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP_Zoning_Block"

# Custom, out of order, runs:
statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block_update_sp = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip_MPO_SP_Zoning_Block_Update_SP"

output_crs = arcpy.SpatialReference("NAD_1983_California_Teale_Albers")

def project_and_delete_dups():
    """ Function to project the state-wide parcels dataset provided by OPR and delete parcels with duplicate
    geometry. ~1hr"""

    print("\nProjecting and Deleting Duplicate Parcels...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nProjecting...")

    input_crs = arcpy.Describe(statewide_parcels_source_fc).SpatialReference
    datum = input_crs.gcs.name
    if datum == "GCS_North_American_1983":
        datum_transformation = "WGS_1984_(ITRF00)_To_NAD_1983"
    else:
        datum_transformation = ""

    arcpy.Project_management(
        in_dataset=statewide_parcels_source_fc,
        out_dataset=statewide_parcels_input_fc_multipart,
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


def explode():
    """ Function to explode multi-part features in the parcels dataset into single part features. """

    print("\nConverting Multpart to Singlpart...\n")

    arcpy.MultipartToSinglepart_management(statewide_parcels_input_fc_multipart, statewide_parcels_input_fc)


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


def join_specific_plan_name(input_fc, output_fc=statewide_parcels_input_fc_with_zip_mpo_sp):
    """ Joins the Specific Plan Name from the specific plan boundary that a parcel falls within. """

    print("Deleting Specific Plan Field...")
    arcpy.DeleteField_management(input_fc, "Specific_Plan")

    print("Joining Specific Plan name to parcels...")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    sp_fields_to_keep = ["OBJECTID", specific_plan_field]
    field_info_string = ""
    fields = [field.name for field in arcpy.ListFields(specific_plan_source_fc)]
    for field in fields:
        if field in sp_fields_to_keep:
            substr = field + " " + field + " VISIBLE NONE;"
        else:
            substr = field + " " + field + " HIDDEN NONE;"

        field_info_string += substr

    print(field_info_string)

    arcpy.MakeFeatureLayer_management(
        in_features=specific_plan_source_fc,
        out_layer="specific_plan_layer", where_clause="", workspace="",
        #field_info="OBJECTID OBJECTID VISIBLE NONE;Shape Shape HIDDEN NONE;MPO_Code MPO_Code HIDDEN NONE;MPO_Name MPO_Name HIDDEN NONE;SP_Name SP_Name VISIBLE NONE;County_Name County_Name HIDDEN NONE;City_Name City_Name HIDDEN NONE;Type Type HIDDEN NONE;Acres Acres HIDDEN NONE;Source_Date Source_Date HIDDEN NONE;Source_Data Source_Data HIDDEN NONE;YrSP_Adopted YrSP_Adopted HIDDEN NONE;YrSP_LastUP YrSP_LastUP HIDDEN NONE;Website Website HIDDEN NONE;SiteCheck SiteCheck HIDDEN NONE;QUERY QUERY HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;Shape_Area Shape_Area HIDDEN NONE")
        field_info=field_info_string)

    print("Spatial Join")
    arcpy.SpatialJoin_analysis(target_features=input_fc, join_features="specific_plan_layer", out_feature_class=output_fc, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping="", match_option="HAVE_THEIR_CENTER_IN", search_radius="", distance_field_name="")

    print("Alter Field")
    arcpy.AlterField_management(output_fc,"SP_Name", "Specific_Plan")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def join_zoning_designations(input_fc, threshold):
    """ Joins the Zoning Designation to each parcel based on the % coverage threshold. ~6 days 14 hours"""

    print("Performing Zoning Data Calculations...")
    fields = [field.name for field in arcpy.ListFields(input_fc)]

    separate_fields = False  # indicates whether zoning designation and % cover should go in separate fields or not.

    start = datetime.datetime.now()
    print("Start: " + str(start))

    #print("Repairing Geometry...")
    # Repairing geometry on the parcels data did not eliminate the topology error (ERROR 160196: Invalid Topology).
    # The problem may be with the zoning data though. Repair geometry was performed on the zoning data
    # in the Prepare_Zoning.py script on 08/18/2023 @ 7:20am
    #arcpy.RepairGeometry_management(input_fc)

    tabulate_intersection_table_name = "Tabulate_Zoning_Intersection"
    tabulate_intersection_table = tmp_gdb + os.sep + tabulate_intersection_table_name

    print("Tabulating Intersection (% zoning designation within each parcel)...")
    arcpy.TabulateIntersection_analysis(
        in_zone_features=input_fc,
        zone_fields=cbi_parcel_id_field,
        in_class_features=zoning_input_fc,
        out_table=tabulate_intersection_table,
        class_fields=zoning_field, sum_fields="", xy_tolerance="")
    # Note: Creating a query table of records > threshold and joining to input fc took took too long.
    # ~2.5 hours for the remaining code.
    print("Creating a dictionary of parcel_id: {zoning_designation='', percent_cover = ''} where percent_cover is >= " + str(threshold))
    zoning_dict = {}
    with arcpy.da.SearchCursor(tabulate_intersection_table, [cbi_parcel_id_field, zoning_field, "PERCENTAGE"]) as sc:
        for row in sc:
            parcel_id = row[0]
            zoning_designation = row[1]
            percent_cover = round(row[2], 1)
            if percent_cover >= threshold:
                if parcel_id not in zoning_dict:
                    zoning_dict[parcel_id] = {}
                    zoning_dict[parcel_id]["zoning_designations"] = {}
                    zoning_dict[parcel_id]["count"] = 0
                zoning_dict[parcel_id]["zoning_designations"][zoning_designation] = percent_cover
                zoning_dict[parcel_id]["count"] += 1

    # Delete and add fields each run in case zoning data changes (don't want residual values).
    print("Deleting and Adding Zoning Designation fields...")

    print("Zoning_Designation...")
    if "Zoning_Designation" in fields:
        arcpy.DeleteField_management(input_fc, "Zoning_Designation")
    arcpy.AddField_management(input_fc, "Zoning_Designation", "TEXT", field_length=500)

    print("Zoning_Designation_Count...")
    if "Zoning_Designation_Count" in fields:
        arcpy.DeleteField_management(input_fc, "Zoning_Designation_Count")
    arcpy.AddField_management(input_fc, "Zoning_Designation_Count", "SHORT")
    arcpy.CalculateField_management(input_fc, "Zoning_Designation_Count", 0)

    print("Percent_Cover...")
    arcpy.DeleteField_management(input_fc, "Zoning_Percent_Cover")
    if separate_fields:
        arcpy.AddField_management(input_fc, "Zoning_Percent_Cover", "TEXT")

    if separate_fields:
        fields_to_calc = [cbi_parcel_id_field, "Zoning_Designation", "Zoning_Percent_Cover"]
    else:
        fields_to_calc = [cbi_parcel_id_field, "Zoning_Designation", "Zoning_Designation_Count"]

    count = 0
    print("Running update cursor to add zoning designations from dictionary to to parcels data...")
    with arcpy.da.UpdateCursor(input_fc, fields_to_calc) as uc:
        for row in uc:
            print(count)
            row[2] = 0  # Initialize the zoning designation count to 0
            parcel_id = row[0]
            if parcel_id in zoning_dict:
                #print(zoning_dict[parcel_id])
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
                    print(parcel_id + ": " + str(zoning_dict[parcel_id]))
                    row[1] = json.dumps(zoning_dict[parcel_id]["zoning_designations"])
                    row[2] = json.dumps(zoning_dict[parcel_id]["count"])
                uc.updateRow(row)
            count += 1

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def join_census_block(input_fc):
    """ Joins the CENSUS Block Name from the TIGER CENSUS Blocks that a parcel falls within. ~1 hour """

    print("Joining CENSUS Block name to parcels...")

    output_fc = statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block

    start = datetime.datetime.now()
    print("Start: " + str(start))

    arcpy.SpatialJoin_analysis(
        target_features=input_fc,
        join_features=census_block_source_fc,
        out_feature_class=output_fc,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping=r'fips "fips" true true false 8 Text 0 0,First,#,' + input_fc + ',fips,0,8;county_name "county_name" true true false 32 Text 0 0,First,#,' + input_fc + ',county_name,0,32;fips_apn "fips_apn" true true false 30 Text 0 0,First,#,' + input_fc + ',fips_apn,0,30;apn "apn" true true false 20 Text 0 0,First,#,' + input_fc + ',apn,0,20;apn_d "apn_d" true true false 17 Text 0 0,First,#,' + input_fc + ',apn_d,0,17;s_city "s_city" true true false 50 Text 0 0,First,#,' + input_fc + ',s_city,0,50;s_addr_d "s_addr_d" true true false 52 Text 0 0,First,#,' + input_fc + ',s_addr_d,0,52;cbi_parcel_id_fips_apn_oid "cbi_parcel_id_fips_apn_oid" true true false 255 Text 0 0,First,#,' + input_fc + ',cbi_parcel_id_fips_apn_oid,0,255;state_name "state_name" true true false 255 Text 0 0,First,#,' + input_fc + ',state_name,0,255;latitude "latitude" true true false 8 Double 0 0,First,#,' + input_fc + ',latitude,-1,-1;longitude "longitude" true true false 8 Double 0 0,First,#,' + input_fc + ',longitude,-1,-1;zip_code "Zip Code" true true false 10 Text 0 0,First,#,' + input_fc + ',zip_code,0,10;MPO "MPO" true true false 55 Text 0 0,First,#,' + input_fc + ',MPO,0,55;Label_MPO "Label_MPO" true true false 10 Text 0 0,First,#,' + input_fc + ',Label_MPO,0,10;Specific_Plan "Specific Plan Name" true true false 255 Text 0 0,First,#,' + input_fc + ',Specific_Plan,0,255;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,' + input_fc + ',Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,' + input_fc + ',Shape_Area,-1,-1;Zoning_Designation "Zoning_Designation" true true false 500 Text 0 0,First,#,' + input_fc + ',Zoning_Designation,0,500;Zoning_Designation_Count "Zoning_Designation_Count" true true false 2 Short 0 0,First,#,' + input_fc + ',Zoning_Designation_Count,-1,-1;NAME20 "NAME20" true true false 10 Text 0 0,First,#,' + census_block_source_fc + ',NAME20,0,10',
        match_option="HAVE_THEIR_CENTER_IN",
        search_radius=None,
        distance_field_name=""
    )

    arcpy.AlterField_management(output_fc,"NAME20", "Census_Block")

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


def add_zoning_description(input_fc):

    zoning_lookup_dict = {}
    with open(code_to_ucd_zoning_lookup, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            code = row["Code"]
            ucd_description = row["ucd_description"]
            zoning_lookup_dict[code] = ucd_description

    arcpy.AddField_management(input_fc, "Zoning_Designation_UCD_Desc", "Text","","", 1000)

    with arcpy.da.UpdateCursor(input_fc, ["Zoning_Designation", "Zoning_Designation_UCD_Desc"]) as uc:
        for row in uc:
            code_and_ucd_desc_dict = {}
            code_dict = json.loads(row[0])
            for code, percent in code_dict.items():
                ucd_description = zoning_lookup_dict[code]
                code_and_ucd_desc_dict[code] = [percent, ucd_description]
            row[1] = json.dumps(code_and_ucd_desc_dict)
            uc.updateRow(row)


#project_and_delete_dups()
#explode()
#add_and_calculate_fields()
#calc_zip_codes()
#join_mpo_name(input_fc=statewide_parcels_input_fc_with_zip)
#join_specific_plan_name(input_fc=statewide_parcels_input_fc_with_zip_mpo)
#join_zoning_designations(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block, threshold=20)
#join_census_block(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp)

# Not used...
#add_zoning_description(input_fc=test_parcels_with_zoning)

# Custom, out of order, runs:
#join_specific_plan_name(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block, output_fc=statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block_update_sp)
##

clean_up_fields(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block_update_sp, fields_to_delete=["Shape_Length_1", "Shape_Area_1", "Join_Count", "TARGET_FID", "Join_Count_1", "Join_Count_12", "TARGET_FID_1", "TARGET_FID_12"])

separate_into_counties(input_fc=statewide_parcels_input_fc_with_zip_mpo_sp_zoning_block_update_sp)

end_script = datetime.datetime.now()
print("\nEnd Script: " + str(end_script))

duration = end_script - start_script
print("Total Duration: " + str(duration))

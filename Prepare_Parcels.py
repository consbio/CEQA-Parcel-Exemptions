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

# Output Parameters:
output_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Prepared_By_County.gdb"
statewide_parcels_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_Proj_No_Dups"
statewide_parcels_input_fc_with_zip = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb\Statewide_Parcels_With_Zip"
zip_codes_input_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\California_Zip_Codes_Projected"


def project_and_delete_dups():
    """ Function to project the state-wide parcels dataset provided by OPR and delete parcels with duplicate
    geometry. ~1hr"""

    print("\nProjecting and Deleting Duplicate Parcels...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nProjecting...")

    arcpy.Project_management(
        in_dataset=statewide_parcels_source_fc,
        out_dataset=statewide_parcels_input_fc,
        out_coor_system="PROJCS['NAD_1983_California_Teale_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',-4000000.0],PARAMETER['Central_Meridian',-120.0],PARAMETER['Standard_Parallel_1',34.0],PARAMETER['Standard_Parallel_2',40.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
        transform_method="WGS_1984_(ITRF00)_To_NAD_1983",
        in_coor_system="PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
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

    cbi_parcel_id_field = "cbi_parcel_id_fips_apn_oid"
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


def clean_up_fields():
    """ Function to delete extraneous fields and remove aliases from the state-wide dataset. ~8hrs """

    print("\nCleaning up fields...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nDeleting Extraneous fields...")

    fields_to_delete = ["Join_Count", "TARGET_FID"]
    for field in fields_to_delete:
        print(field)
        arcpy.DeleteField_management(statewide_parcels_input_fc_with_zip, field)

    print("\nRemoving field aliases...")

    fields_to_remove_alias = ["zip_code"]
    for field in fields_to_remove_alias:
        arcpy.AlterField_management(statewide_parcels_input_fc_with_zip, field, "", "", "", "", "", "CLEAR_ALIAS")

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


def separate_into_counties():
    """ Function to separate state-wide parcels dataset into separate parcel datasets for each county. ~1.5hrs"""

    print("\nSeparating parcels by county...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    print("\nGathering a list of county names...")

    county_name_list = []
    with arcpy.da.SearchCursor(statewide_parcels_input_fc_with_zip, ["county_name"]) as sc:
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
        arcpy.Select_analysis(statewide_parcels_input_fc_with_zip, output_county_parcels_fc, expression)

    end = datetime.datetime.now()
    print("\nEnd: " + str(end))
    duration = end - start
    print("Duration: " + str(duration))


end_script = datetime.datetime.now()
print("\nEnd Script: " + str(end_script))

duration = end_script - start_script
print("Total Duration: " + str(duration))

project_and_delete_dups()
add_and_calculate_fields()
calc_zip_codes()
clean_up_fields()
separate_into_counties()

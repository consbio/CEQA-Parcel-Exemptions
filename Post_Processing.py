########################################################################################################################
# Script: Post Processing
# Author: Mike Gough
# Date created: 05/09/2023
# Python Version: 3.x (ArcGIS Pro)/(Should work in 2.7 (ArcGIS Desktop))
# Description: This script performs post processing on the parcels data and the CEQA requirements & exemptions tables.
########################################################################################################################

import arcpy
import datetime

parcels_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb"

arcpy.env.workspace = parcels_gdb
fc_list = arcpy.ListFeatureClasses()
table_list = arcpy.ListTables()

data_list = fc_list + table_list


def rename_fields():
    """ Renames fields based on from/to mapping in the field_changes list """

    print("\nRenaming Fields...\n")

    start = datetime.datetime.now()
    print("Start: " + str(start))


    field_changes = [
        ["fips", "FIPS_CODE"],
        ["county_name", "COUNTYNAME"],
        ["fips_apn", "PARCEL_FIPS_APN"],
        ["apn", "PARCEL_APN"],
        ["apn_d", "PARCEL_APN_D"],
        ["s_city", "SITE_CITY"],
        ["s_addr_d", "SITE_ADDR"],
        ["cbi_parcel_id_fips_apn_oid", "PARCEL_ID"],
        ["state_name", "SITE_STATE"],
        ["zip_code", "SITE_ZIP"],
    ]

    for fc_or_table in data_list:
        print(fc_or_table)
        from_field_list = [field.name for field in arcpy.ListFields(fc_or_table)]
        for field_change in field_changes:
            print(field_change)
            from_field = field_change[0]
            if from_field in from_field_list:
                to_field = field_change[1]
                arcpy.AlterField_management(fc_or_table, from_field, to_field)

rename_fields()


########################################################################################################################
# File name: Prepare_Parcels.py
# Author: Mike Gough
# Date created: 05/02/2023
# Python Version: 2.7
# Description:
# Prepares parcels for the Requirements and Exemptions Script.
# Performs the following tasks:
# Projects all of the parcels data for the state of California and deletes parcels with duplicate geometries
########################################################################################################################

import arcpy
import glob
import os
import datetime
import uuid

start_script = datetime.datetime.now()
print("Start Script: " + str(start_script))

parcels_dir = r"\\loxodonta\gis\Source_Data\planningCadastre\state\CA\SiteCheck_Parcels_2023"
intermediate_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Projected_Delete_Identical.gdb"
output_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels\Parcels_Prepared.gdb"

def project_and_delete_dups():
    gdb_list = glob.glob(parcels_dir + os.sep + "*.gdb")
    print("Geodatabase List: " + str(gdb_list))

    for gdb in gdb_list:
        arcpy.env.workspace = gdb
        parcels_fc = arcpy.ListFeatureClasses("Statewide_Parcels")[0]
        print(parcels_fc)
        output_parcels_fc = intermediate_gdb + os.sep + parcels_fc

        print("\nProjecting...")

        start = datetime.datetime.now()
        print("Start: " + str(start))

        arcpy.Project_management(parcels_fc, output_parcels_fc, "PROJCS['NAD_1983_California_Teale_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',-4000000.0],PARAMETER['Central_Meridian',-120.0],PARAMETER['Standard_Parallel_1',34.0],PARAMETER['Standard_Parallel_2',40.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

        end = datetime.datetime.now()
        print("End: " + str(end))

        duration = end - start
        print("Duration: " + str(duration))

        print("\nDeleting Identical...")

        start = datetime.datetime.now()
        print("Start: " + str(start))

        arcpy.DeleteIdentical_management(output_parcels_fc, "SHAPE")

        end = datetime.datetime.now()
        print("End: " + str(end))

        duration = end-start
        print("Duration: " + str(duration))

def add_and_calculate_fields():

    print("\nAdding and calculating fields...")

    start = datetime.datetime.now()
    print("Start: " + str(start))

    arcpy.env.workspace = intermediate_gdb
    input_parcels_fc_list = arcpy.ListFeatureClasses()

    for input_parcels_fc in input_parcels_fc_list:

        fields = [field.name.lower() for field in arcpy.ListFields(input_parcels_fc)]

        print("\nID Field...")

        # Note: the values in fips_apn are not unique even with duplicates removed.

        cbi_parcel_id_field = "cbi_parcel_id_fips_apn_oid"
        if "parcel_id" not in fields and cbi_parcel_id_field not in fields:
            arcpy.AddField_management(input_parcels_fc, cbi_parcel_id_field, "TEXT")
            with arcpy.da.UpdateCursor(input_parcels_fc, ["fips_apn", "OBJECTID",  cbi_parcel_id_field]) as uc:
                for row in uc:
                    unique_id = "_".join([row[0], str(row[1])])
                    row[2] = unique_id
                    uc.updateRow(row)

        print("\nState Field...")

        cbi_state_field = "state_name"
        if "statename" not in fields and cbi_state_field not in fields:
            arcpy.AddField_management(input_parcels_fc, cbi_state_field, "TEXT")
            arcpy.CalculateField_management(input_parcels_fc, cbi_state_field, "\"California\"")

        print("\nLatitude Field...")

        cbi_lat_field = "latitude"
        if "lat" not in fields and cbi_lat_field not in fields:
            arcpy.AddField_management(input_parcels_fc, cbi_lat_field, "DOUBLE")
            arcpy.CalculateGeometryAttributes_management(input_parcels_fc, [[cbi_lat_field, "CENTROID_Y"]], "", "","", "DD")

        print("\nLongitude Field...")

        cbi_lon_field = "longitude"
        if "lon" not in fields and cbi_lon_field not in fields:
            arcpy.AddField_management(input_parcels_fc, cbi_lon_field, "DOUBLE")
            arcpy.CalculateGeometryAttributes_management(input_parcels_fc, [[cbi_lon_field, "CENTROID_X"]], "", "","", "DD")


    start = datetime.datetime.now()
    print("Start: " + str(start))


#project_and_delete_dups()
add_and_calculate_fields()


end_script = datetime.datetime.now()
print("End Script: " + str(end_script))

duration = end_script - start_script
print("Total Duration: " + str(duration))

########################################################################################################################
# File name: Prepare_Zoning.py
# Author: Mike Gough
# Date created: 08/10/2023
# Python Version: 3.x (ArcGIS Pro)/(Should work in 2.7 (ArcGIS Desktop))
# Description:
# Prepares zoning data for inclusion in the parcels dataset.
# Performs the following tasks:
#
# 1. Merge
# 2. Project
# 3. Repair Geometry
# Total Runtime: ~20mins + x for repair geometry.

########################################################################################################################
import arcpy
import os

input_gdb = r"\\loxodonta\GIS\Source_Data\planningCadastre\state\CA\Zoning\From_Mark_Hedlund_OPR\20230809\Zoning2023_8_9\Official.gdb\zoning"
tmp_gdb = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Zoning\Scratch\Scratch.gdb"
output_fc = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Zoning\Zoning.gdb\california_zoning_opr_20230828_prepared"
output_crs = arcpy.SpatialReference("NAD_1983_California_Teale_Albers")

arcpy.env.workspace = input_gdb

input_fc_list = arcpy.ListFeatureClasses()

print("Input Zoning Feature Classes: " + str(input_fc_list))

merged_zoning_fc = os.path.join(tmp_gdb, "california_zoning_merge")


def merge():
    print("Merge input zoning datasets")
    arcpy.Merge_management(input_fc_list, merged_zoning_fc)


input_crs = arcpy.Describe(merged_zoning_fc).spatialReference


def project():
    if input_crs.name != output_crs:
        print("Input CRS " + input_crs.name)
        print("Project to " + output_crs.name)
        datum = input_crs.gcs.name
        if datum == "GCS_North_American_1983":
            datum_transformation = "WGS_1984_(ITRF00)_To_NAD_1983"
        else:
            datum_transformation = ""
        arcpy.Project_management(merged_zoning_fc, output_fc, output_crs, datum_transformation)
    else:
        arcpy.CopyFeatures_management(merged_zoning_fc, output_fc)


def repair_geometry():
    arcpy.RepairGeometry_management(output_fc)


merge()
project()
repair_geometry()

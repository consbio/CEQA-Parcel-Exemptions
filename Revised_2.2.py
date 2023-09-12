########################################################################################################################
# Script: Revised 2.2 Calculation
# Author: Mike Gough
# Date Updated: 09/12/2023
# Python Version: 3.x (ArcGIS Pro)/(Should work in 2.7 (ArcGIS Desktop))
# Creates the input dataset used for calculating Requirement 2.2 (Urban Area PRC 21094.5) which represents all areas
# that qualify for Requirement 2.2.
# On 09/12/2023 this script was updated to use the most recent output from Requirement 2.1:
#https://databasin.org/datasets/d62d45a7048e44919f024e2fcbb62572/
########################################################################################################################

import arcpy

scratch_ws = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Scratch\Scratch.gdb"

# CEQA version 1.0 2021
#urbanized_area_prc_21071_input = r"P:\Projects3\CEQA_Site_Check_Version_1_0_2021_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urbanized_area_prc_21071_v1_0"
#urban_area_prc_21094_5_output = r"P:\Projects3\CEQA_Site_Check_Version_1_0_2021_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urban_area_prc_21094_5_v1_0"

# CEQA version 2.0 2021
urbanized_area_prc_21071_input = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urbanized_area_prc_21071_v2_0"
urban_area_prc_21094_5_output = r"P:\Projects3\CEQA_Site_Check_Version_2_0_2023_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urban_area_prc_21094_5_v2_0"

arcpy.CopyFeatures_management(urbanized_area_prc_21071_input, urban_area_prc_21094_5_output)
arcpy.AddField_management(urban_area_prc_21094_5_output, "urban_area_prc_21094_5", "SHORT")

urban_area_prc_21094_5_output_layer = arcpy.MakeFeatureLayer_management(urban_area_prc_21094_5_output)
expression = "community_type = 'Incorporated City' or urbanized_area_prc_21071 = 1"

arcpy.SelectLayerByAttribute_management(urban_area_prc_21094_5_output_layer, "NEW_SELECTION", expression)
arcpy.CalculateField_management(urban_area_prc_21094_5_output_layer, "urban_area_prc_21094_5", 1)
arcpy.SelectLayerByAttribute_management(urban_area_prc_21094_5_output_layer, "SWITCH_SELECTION")
arcpy.CalculateField_management(urban_area_prc_21094_5_output_layer, "urban_area_prc_21094_5", 0)


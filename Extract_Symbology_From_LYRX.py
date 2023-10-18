########################################################################################################################
# File name: Extract_Symbology_From_LYRX.py
# Author: Mike Gough
# Date created: 10/17/2023
# Description:
# Extracts HSV colors from an LYRX file and converts them to RGB values
# The conversion between HSV to RGB is done using colorsys with the input values modified based on information
# gathered from a post on stackoverflow:
# https://stackoverflow.com/questions/24852345/hsv-to-rgb-color-conversion
########################################################################################################################

import json
import colorsys
input_lyrx = r"\\loxodonta\gis\Source_Data\planningCadastre\state\CA\Zoning\From_Mark_Hedlund_OPR\20230809\symbols3.lyrx"

with open(input_lyrx, 'r') as lyrx:
    lyrx_dict = json.load(lyrx)

renderer = lyrx_dict["layerDefinitions"][0]["renderer"]

field = renderer["fields"][0]
print("Field: " + field)

lyrx_classes = renderer["groups"][0]["classes"]


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


for lyrx_class in lyrx_classes:
    label = lyrx_class["label"]
    hsv = lyrx_class["symbol"]["symbol"]["symbolLayers"][1]["color"]["values"]
    rgb = hsv2rgb(hsv[0]/360.0, hsv[1]/100.0, hsv[2]/100.0)
    print(label + ": " + str(rgb))


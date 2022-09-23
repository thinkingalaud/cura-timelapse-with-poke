from ..Script import Script

from UM.Application import Application # To get the current printer's settings.
from UM.Logger import Logger

from typing import List, Tuple

class TimelapseWithPoke(Script):
    def __init__(self) -> None:
        super().__init__()

    def getSettingDataString(self) -> str:
        return """{
            "name": "Timelapse with Poke",
            "key": "TimelapseWithPoke",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "pause_length":
                {
                    "label": "Pause length",
                    "description": "How long to wait (in ms) after camera was triggered.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms"
                },
                "park_print_head":
                {
                    "label": "Park Print Head",
                    "description": "Park the print head out of the way. Assumes absolute positioning.",
                    "type": "bool",
                    "default_value": true
                },
                "head_park_x":
                {
                    "label": "Park Print Head X",
                    "description": "What X location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "enabled": "park_print_head"
                },
                "head_park_y":
                {
                    "label": "Park Print Head Y",
                    "description": "What Y location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190,
                    "enabled": "park_print_head"
                },
                "park_feed_rate":
                {
                    "label": "Park Feed Rate",
                    "description": "How fast does the head move to the park coordinates.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 9000,
                    "enabled": "park_print_head"
                },
                "retract":
                {
                    "label": "Retraction Distance",
                    "description": "Filament retraction distance for camera trigger.",
                    "unit": "mm",
                    "type": "int",
                    "default_value": 0
                },
                "zhop":
                {
                    "label": "Z-Hop Height When Parking",
                    "description": "Z-hop length before parking",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "poke_distance":
                {
                    "label": "Poke Distance",
                    "description": "Distance in the x direction to poke trigger button.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                }
            }
        }"""

    def execute(self, data: List[str]) -> List[str]:
        """Inserts the commands.

        :param data: List of layers.
        :return: New list of layers.
        """
        feed_rate = self.getSettingValueByKey("park_feed_rate")
        park_print_head = self.getSettingValueByKey("park_print_head")
        x_park = self.getSettingValueByKey("head_park_x")
        y_park = self.getSettingValueByKey("head_park_y")
        pause_length = self.getSettingValueByKey("pause_length")
        retract = int(self.getSettingValueByKey("retract"))
        zhop = self.getSettingValueByKey("zhop")
        poke_distance = self.getSettingValueByKey("poke_distance")
        gcode_to_append = ''
        last_x = 0
        last_y = 0
        last_z = 0

        if park_print_head:
            gcode_to_append += self.putValue(G=1, F=feed_rate, X=x_park, Y=y_park) + " ;Park print head\n"
        gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"
        gcode_to_append += self.putValue(G=1, X=x_park + poke_distance) + " ;Poke\n"
        gcode_to_append += self.putValue(G=1, X=x_park) + " ;Unpoke\n"
        gcode_to_append += self.putValue(G=4, P=pause_length) + " ;Wait for camera\n"

        for idx, layer in enumerate(data):
            for line in layer.split("\n"):
                if self.getValue(line, "G") in {0, 1, 2, 3}:  # Track X,Y,Z location.
                    last_x = self.getValue(line, "X", last_x)
                    last_y = self.getValue(line, "Y", last_y)
                    last_z = self.getValue(line, "Z", last_z)
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    layer += ";TimeLapseWithPoke Begin\n"
                    if retract != 0: # Retract the filament so no stringing happens
                        layer += self.putValue(M=83) + " ;Extrude Relative\n"
                        layer += self.putValue(G=1, E=-retract, F=3000) + " ;Retract filament\n"
                        layer += self.putValue(M=82) + " ;Extrude Absolute\n"
                        layer += self.putValue(M=400) + " ;Wait for moves to finish\n" # Wait to fully retract before hopping

                    if zhop != 0:
                        layer += self.putValue(G=1, Z=last_z+zhop, F=3000) + " ;Z-Hop\n"

                    layer += gcode_to_append

                    if zhop != 0:
                        layer += self.putValue(G=0, X=last_x, Y=last_y, Z=last_z) + ";Restore position \n"
                    else:
                        layer += self.putValue(G=0, X=last_x, Y=last_y) + ";Restore position \n"

                    if retract != 0:
                        layer += self.putValue(M=400) + " ;Wait for moves to finish\n"
                        layer += self.putValue(M=83) + " ;Extrude Relative\n"
                        layer += self.putValue(G=1, E=retract, F=3000) + " ;Retract filament\n"
                        layer += self.putValue(M=82) + " ;Extrude Absolute\n"

                    layer += ";TimeLapseWithPoke End\n"

                    data[idx] = layer
                    break
        return data


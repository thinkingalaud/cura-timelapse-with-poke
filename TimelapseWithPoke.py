from ..Script import Script

from UM.Application import Application # To get the current printer's settings.
from UM.Logger import Logger

from typing import List, Tuple

class PauseAtHeight(Script):
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
                "head_park_x":
                {
                    "label": "Park Print Head X",
                    "description": "What X location does the head move to when pausing.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190,
                },
                "head_park_y":
                {
                    "label": "Park Print Head Y",
                    "description": "What Y location does the head move to when pausing.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190,
                },
                "head_move_z":
                {
                    "label": "Head Move Z",
                    "description": "The Height of Z-axis retraction before parking.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5.0,
                },
                "poke_distance_x":
                {
                    "label": "Poke Distance",
                    "description": "The distance in the X direction to poke.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": "1.0",
                },
                "pause_time":
                {
                    "label": "Pause Time",
                    "description": "Amount of time to wait for the picture to be taken.",
                    "unit": "ms",
                    "type": "int",
                    "default_value": "1000",
                },
                "retraction_amount":
                {
                    "label": "Retraction",
                    "description": "How much filament must be retracted at pause.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                },
                "retraction_speed":
                {
                    "label": "Retraction Speed",
                    "description": "How fast to retract the filament.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 25,
                },
            }
        }"""

    def initialize(self) -> None:
        super().initialize()

        global_container_stack = Application.getInstance().getGlobalContainerStack()
        if global_container_stack is None or self._instance is None:
            return

    def getLastXY(self, layer: str) -> Tuple[float, float]:
        """Get the last X and Y values for a layer."""
        lines = layer.split("\n")
        for line in reversed(lines):
            if line.startswith(("G0", "G1", "G2", "G3")):
                if self.getValue(line, "X") is not None and self.getValue(line, "Y") is not None:
                    x = self.getValue(line, "X")
                    y = self.getValue(line, "Y")
                    return x, y
        return 0, 0

    def getLastF(self, layer: str) -> Tuple[float, float]:
        """Get the last F values for a layer."""
        lines = layer.split("\n")
        for line in reversed(lines):
            if line.startswith(("G0", "G1", "G2", "G3")):
                if self.getValue(line, "F") is not None:
                    return self.getValue(line, "F")
        return 0

    def execute(self, data: List[str]) -> List[str]:
        """Inserts the commands.

        :param data: List of layers.
        :return: New list of layers.
        """
        retraction_amount = self.getSettingValueByKey("retraction_amount")
        retraction_speed = self.getSettingValueByKey("retraction_speed")
        park_x = self.getSettingValueByKey("head_park_x")
        park_y = self.getSettingValueByKey("head_park_y")
        move_z = self.getSettingValueByKey("head_move_z")
        poke_distance_x = self.getSettingValueByKey("poke_distance_x")
        pause_time = self.getSettingValueByKey("pause_time")
        layers_started = False

        for index, layer in enumerate(data):
            lines = layer.split("\n")

            if not layers_started:
                for line in lines:
                    # First positive layer reached. Need to do this since sometimes the rafts are generated with negative layer numbers
                    if ";LAYER:0" in line:
                        layers_started = True
                        break 

            if not layers_started:
                continue

            x, y = getLastXY(layer)
            f = getLastF(layer)

            append_gcode = []
            append_gcode += ";TYPE:CUSTOM"
            append_gcode += ";added code by post processing"
            append_gcode += ";script: TimelapseWithPoke.py"

            append_gcode += self.putValue(G=91) + " ; relative mode"
            append_gcode += self.putValue(G=1, E=-retraction_amount, F=retraction_speed * 60) + " ; retract"
            append_gcode += self.putValue(G=0, Z=move_z, F=300)
            append_gcode += self.putValue(G=90) + " ; absolute mode"
            append_gcode += self.putValue(G=0, X=park_x, Y=park_y, F=10000)
            append_gcode += self.putValue(G=0, X=park_x + poke_distance_x, F=1000) + " ; poke"
            append_gcode += self.putValue(G=0, X=park_x, F=1000) + " ; unpoke"
            append_gcode += self.putValue(G=4, P=pause_time) + " ; wait for picture to be taken"
            append_gcode += self.putValue(G=0, X=x, Y=y, F=10000) + " ; restore x, y"
            append_gcode += self.putValue(G=91) + " ; relative mode"
            append_gcode += self.putValue(G=1, E=retraction_amount - 1, F=retraction_speed * 60) + " ; restore filament"
            append_gcode += self.putValue(G=0, Z=-move_z, F=300) + " ; restore z"
            append_gcode += self.putValue(G=90) + " ; absolute mode"
            append_gcode += self.putValue(G=0, F=f) + " ; reset feedrate"

            layer += "\n".join(append_gcode)

            # Override the data of this layer with the modified data
            data[index] = layer
        return data


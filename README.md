# cura-timelapse-with-poke

An [Ultimaker Cura](https://ultimaker.com/software/ultimaker-cura) script to take timelapse photos by poking a button using the print head.


## Background
The Anycubic Kobra doesn't have any support for the M240 gcode (trigger camera). In order to create timelapses where the head is parked out of the way, a custom script must be used. Inspired by this [Youtube video](https://www.youtube.com/watch?v=NawlHlLH4Zg), you can mount a remote for your camera (in my case, a GoPro) and use the print head to poke the button to take a photo.

Remote holder: https://www.thingiverse.com/thing:5527432

Finger: https://www.thingiverse.com/thing:5527450

TODO: create a video showcasing the entire setup

## Installation
Copy the TimelapseWithPoke.py file to your scripts configuration folder (Help -> Show Configuration Folder -> scripts/) and restart Cura.

I would highly recommend that you manually test the desired location of the print head as well the poke distance using something like [Pronterface](https://www.pronterface.com/) to send adhoc gcode commands for your printer.

## Caveats
Tested with Anycubic Kobra firmware v2.7.9 and Cura v5.1.0

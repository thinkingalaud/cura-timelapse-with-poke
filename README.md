# cura-timelapse-with-poke

An [Ultimaker Cura](https://ultimaker.com/software/ultimaker-cura) script to take timelapse photos by poking a button using the print head.


## Background
The Anycubic Kobra doesn't have any support for the M240 gcode (trigger camera). In order to create timelapses where the head is parked out of the way, a custom script must be used. Inspired by this [Youtube video](https://www.youtube.com/watch?v=NawlHlLH4Zg), you can mount a remote for your camera and use the print head to poke the button to take a photo.

Remote holder: https://www.printables.com/model/282413-gopro-remote-holder-for-anycubic-kobra
Insert for Canon BR-E1 remote: https://www.printables.com/model/337344-canon-br-e1-remote-holder-insert

Finger: https://www.printables.com/model/282412-remote-presser-finger

TODO: create a video showcasing the entire setup

## Installation
Copy the TimelapseWithPoke.py file to your scripts configuration folder (Help -> Show Configuration Folder -> scripts/) and restart Cura.

I would highly recommend that you manually test the desired location of the print head as well the poke distance using something like [Pronterface](https://www.pronterface.com/) to send adhoc gcode commands for your printer.

## Caveats
Tested with Anycubic Kobra firmware v2.7.9 and Cura v5.1.0

Be careful with the poke distance and print head park location - if there's too much resistance, it can cause shifts in your print because the belt/print head can't move to the correct location, but the printer will think that it did.

# Maya cg Shelf

## Hash Renamer

Allows to rename multiple selected nodes to a name plus number.

+ The number will be placed where ever a hash character (#) is placed in the entered name.
+ Multiple consecutive hashes will result in a number of this length with leading zeros.
  + name_#_geo >> name_1_geo, name_2_geo...
  + name_##_geo >> name_01_geo, name_02_geo...
+ If there is no hash character in the given name the numbers will be added to the end and will be of length three.
+ Right clicking the text input field shows a menu with the previous entered names. 

## Add Group

Adds a transform node above the selected objects.

+ The transform will match the pivot position and orientation of the selected object.
+ The name will be the name of the object with a postfix of "_grp".

## Add Shape

With two objects selected a click on Add Shape will add the shape of the first selected object to the second selected object. The position of the shape will not be altered.

## Joint Tool

This is the Maya joint tool placed there for convenience.

## Split Joints Tool

Splits all selected joints into a number of sub segments. The tool will try to determine the twist axis (the axis pointing to the first child joint). Unclear twist axis orientations may result in strange results.

## IK Handle Tool

This is the Maya IK handle creation tool placed the for convenience.

## Stretchy IK Setup

With a Rotate-Plane-Solver IK handle selected this tool lets you quickly setup a stretchy IK.

+ The "Create" button will only be enabled when all necessary prerequisits are met.
+ For setting up a stretchy IK without a lock feature the prerequisit is a selected IK (RP) handle only.
+ With "Add Lock Feature" checked you also need to select an existing pole vector object. 

# Houdini Tool - Save and Update tools
## Descriptions
A Houdini tool to save a selection of nodes to a tool, and/or to update and existing tool.
The tool works by saving a selection of nodes as python code and adding that code to a given tool's script.

This tool was developped within the ![MenhirFX studio](https://menhirfx.com/fr).

## How To
### Save a node selection
To save a node selection to a tool on a shelf, an empty tool with a set name needs to exist on a shelf, at least one of the selected nodes needs to have a parm with the tool name and the shelf name. A convenience script is included with this tool to quickly add two parms: 'shelf_name' and 'preset_name'.

![01](https://user-images.githubusercontent.com/72398192/186459524-6317f639-0763-401a-902f-c5523fa5b87d.PNG)

The parms should be filled with the name of the tool, and the name of the shelf containing the tool. 

![02](https://user-images.githubusercontent.com/72398192/186460755-7d6442e2-38fe-4ab1-83c2-9511093144c3.PNG)

 The parms can be hidden by the 'Hide/Unhide parms' script, but this is optional.

After the parms are set, all is left is to select the nodes to save, and use the 'Update Presets' tool. The node will be saved as Python Code in the tool's script, and can now be recreated easily.

### Update an existing tool
To update and existing tool the process is similar. At least one of the nodes selected needs to have both 'shelf_name' and 'preset_name' parms filled out with the right info, and the tool that need to be updated needs to exist.
If those conditions are met, then all that is needed is to select all the nodes, and use 'Update Preset'.


## Install
To install this tool, you can either use the shelf file by copying it to your usual Houdini shelf location, or you can use the python code directly in a Houdini Python editor.

## Contact
To Use this tool please contact MenhirFX at contact@menhirfx.com

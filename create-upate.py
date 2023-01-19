import hou
import os
from datetime import datetime
import shutil

'''
Authors: 
    Elise Vidal
    email: evidal@artfx.fr

    Angele Sionneau
    email: asionneau@artfx.fr

date: december 2022

[Tools Updater]
This script allows to save and update node groups in a tool. 
When an update is run, a backup of the entire shelf is made.
_______________________________________
[Updater de tools]
Ce script permet la sauvegarde et la mise à jour de groupes de node dans un tool. 
Lorsque d'une mise à jour est effectuée, un backup du shelf entier est effectué.
'''

def get_tool_data():
    '''Returns a dict with all relevant information about the tool to update'''
    nodes = hou.selectedNodes()

    # verify if nodes are selected
    if nodes == ():
        hou.ui.displayMessage("Please select a node to update")
        return None
        
    # get tool's infos
    text = "Please write the name of the tool you want to create or modify and the name of its shelf."
    infos = hou.ui.readMultiInput(text, ["shelf", "tool"])
    if infos[1][0] == "" or infos[1][1] =="":
        hou.ui.displayMessage("You need to specify a shelf name and a tool name")
        return None
    
    # verify if the tool exist
    tools_infos = verify_tool(infos)
    
    # set datas
    data = {}
    data['nodes'] = nodes
    data['shelf'] = tools_infos.get("shelf")
    data["shelf_path"] = data.get("shelf").filePath()
    data["tool"] = tools_infos.get("tool")
    data['menu_op_type'] = data.get('tool').toolMenuOpType(hou.paneTabType.NetworkEditor)
    data['menu_locations'] = data.get('tool').toolMenuLocations()
    return data

def verify_tool(infos):
    '''
    Verify if the shelf name and the tool name specified exist.
    If not, the shelf and the tool are created.
    Return a dict with the shelf object and the tool object.
    '''
    # set path
    shelf_name = infos[1][0]
    path = hou.houdiniPath("HOUDINI_TOOLBAR_PATH")
    for p in path:
        if "Documents" in p:
            path = p
            break
    path = path + "/" + shelf_name + ".shelf"
    
    # if shelf doesn't exist, create the shelf
    shelf = None
    try:
        shelf = hou.shelves.shelves()[shelf_name]
    except KeyError:
        shelf = hou.shelves.newShelf(file_path=path, name=shelf_name, label=shelf_name)
    
    # if the tool doesn't exist, create the tool
    tool_name = infos[1][1]
    tools = shelf.tools()
    tool_to_update = None
    for t in tools:
        if t.name() == tool_name:
            tool_to_update = t    
    try:
        assert tool_to_update is not None
    except AssertionError:
        tool_to_update = hou.shelves.newTool(file_path=path, name=tool_name, label=tool_name)
        list = []
        for t in tools:
            list.append(t)
        list.append(tool_to_update)
        tup = tuple(list)
        shelf.setTools(tup)
    
    # return the shelf and the tool
    return {"shelf" : shelf, "tool" : tool_to_update}
    
def back_up_shelf(shelf, shelf_path):
    '''Copies the current shelf to a backup location on disk.'''
    shelf_file_name = os.path.basename(shelf_path)
    new_shelf_name = datetime.now().strftime('%d-%m-%y_%H-%M')+"_"+shelf_file_name
    shelf_dir = os.path.dirname(shelf_path)
    backup_dir = shelf_dir + '/.old'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup = backup_dir+ "/" +new_shelf_name
    shutil.copy(shelf_path, backup)
   
def update_tool(data):
    '''
    Sets the tool script to be the selected nodes as python code.
    If multiple nodes are selected they will be collapsed into a subnet, and the subnet script will be added to
    the tool. A script is added to the tool to automatically delete the parent subnet if it exists.
    The prescript makes sure the nodes match the current network pane.
    '''
    # Get relevant data
    nodes = data.get('nodes')
    shelf_path = data.get('shelf_path')
    tool = data.get('tool')
    menu_op_type = data.get('menu_op_type')
    menu_locations = data.get('menu_locations')
    node_type = None

    # Check if more than one node, and if True collapse then into subnet
    if len(nodes) > 1:
        parent = nodes[0].parent()
        node_type = nodes[0].type().name()
        subnet = parent.collapseIntoSubnet(nodes)
        node = subnet
    else:
        node = nodes[0]
        node_type = node.type().name()
    
    # Script to be appended at the beginning of the tool script
    # Checks if node type is child of pane type
    pre_script = """
import sys
import toolutils

pane = toolutils.activePane(kwargs)
if not isinstance(pane, hou.NetworkEditor):
    pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    if pane is None:
       hou.ui.displayMessage(
               'Cannot create node: cannot find any network pane')
       sys.exit(0)
else:
    pane_node = pane.pwd()


pane_node = pane.pwd()
child_type = pane_node.childTypeCategory().nodeTypes()

if '{}' not in child_type:
   hou.ui.displayMessage(
           'Cannot create node: incompatible pane network type')
   sys.exit(0)

hou_parent = pane.pwd()

if locals().get('hou_parent') is None:
    hou_parent = hou.node('/mat')""".format(node_type)
    
    # Get node as code
    node_as_code = node.asCode(brief=True, recurse=True)
    # code to be appended at the end of tool script: removes subnet
    extract_node = """nodes = hou_node.extractAndDelete()
for n in nodes:
        n.moveToGoodPosition()
nodes[-1].destroy()"""
    
     # Combine all script to make final tool script
    if len(nodes) > 1:
        script = pre_script + node_as_code + extract_node
    else:
        script = pre_script + node_as_code
    
    # Set tool script, pane type and menu location
    tool.setData(script=script)
    tool.setFilePath(shelf_path)
    tool.setToolMenuOpType(hou.paneTabType.NetworkEditor, menu_op_type)
    tool.setToolLocations(menu_locations)
    
    # Delete subnet if created
    if len(nodes) > 1:
        nodes = subnet.extractAndDelete()
        nodes[-1].destroy()




# program
data = get_tool_data()
if data is not None:
    back_up_shelf(data.get('shelf'), data.get('shelf_path'))
    update_tool(data)

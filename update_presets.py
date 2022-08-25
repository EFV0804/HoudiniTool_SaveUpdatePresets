import hou
import os
import shutil
import logging
from datetime import datetime

'''
Author: Elise Vidal
email: evidal@artfx.fr
date: 04/07/2022

Preset Updater
This scripts is used to update custom tools from the MenhirFX shelves, based on the changes brought to a selected node.
IMPORTANT: For this script to work the preset node needs two custom parameters: preset_name, and shelf_name.
These can be added through the Parameter Interface or with Add Parm Script
preset_name = string, should be the same as the name of the tool on the shelf
shelf_name = string, should be the name of the shelf holding the tool that needs to be updated
_______________________

Updater de Presets
Ce script sert a faciliter la mise a jour des presets des shelf MenhirFX, base sur les changement applique un node selectionne.
IMPORTANT: Pour que ce script marche le node de preset a besoin de deux parametres: preset_name, et shelf_name.
Ces parametres peuvent etre ajoutes via le Parameter Interface du node ou avec le Add Parm script
preset_name = string, doit etre le meme que le nom du tool qui correspond, sur la shelf
shelf_name = string, doit etre le meme que le nom de la shelf qui contient le tool a mettre a  jour
'''
logger = logging.getLogger("PRESET UPDATE")


def get_selected_nodes():
    '''Returns a list of selected nodes. Throws error if no node selected.'''
    nodes = hou.selectedNodes()
    try:
        node = nodes[0]
        return nodes
    except IndexError:
        logger.error('Please select a node to update')

def get_preset_info(nodes):
    '''
    Returns the info about the preset that will be updated. This information is retrieved 
    from the parms 'preset_name', 'shelf_name' on the selected nodes.
    Info is appended to date dict
    '''
    preset_info = {'preset_name' : None,
                    'shelf_name' : None
                    }
    for node in nodes:
        parms = node.parms()
        for parm in parms:
            if parm.name() == 'preset_name':
                preset_info['preset_name'] = parm.evalAsString()
            elif parm.name() == 'shelf_name':
                preset_info['shelf_name'] = parm.evalAsString()
    try:
        assert preset_info['shelf_name'] is not None
    except AssertionError:
        logger.error("Selected node not connected to a preset. Make sure it has a 'preset_name' parm")
            
        
    try:
        assert preset_info['shelf_name'] is not None
    except AssertionError:
        logger.error("Selected node not connected to a preset. Make sure it has a 'shelf_name' parm")
        
        
    return preset_info
            
def get_tool_to_update(preset_info, shelf):
    '''
    Return the hou.Tool object that will be updated using the given hou.Shelf
    '''
    update_tool = None

    #get tool to update
    tools = shelf.tools()
    for tool in tools:
        if tool.name() == preset_info['preset_name']:
            update_tool = tool
    try:
        assert update_tool is not None
    except AssertionError:
        logger.error("Selected node's preset name doesn't match with any of the {} shelf tools".format(shelf_name))
        
    return update_tool
   
def get_shelf(shelf_name):
    '''Returns the hou.Shelf object corresponding to the given name.'''
    shelf = None
    try:
        shelf = hou.shelves.shelves()[shelf_name]
        return shelf
    except KeyError:
        logger.error("'{}' is not a valid shelf name or shelf doesn't exist".format(shelf_name)) 
    return None
    
def back_up_shelf(shelf, shelf_path):
    '''Copies the current shelf to a backup location on disk.'''
    logger.info('creating backup of shelf {} '.format(shelf.name()))
    shelf_file_name = os.path.basename(shelf_path)
    new_shelf_name = datetime.now().strftime('%d-%m-%y_%H-%M')+'_' + shelf_file_name
    shelf_dir = os.path.dirname(shelf_path)
    if not os.path.exists(shelf_dir+'/old'):
        os.makedirs(shelf_dir+'/old')
    backup_dir = shelf_dir + '/old/'
    backup = backup_dir + new_shelf_name
    shutil.copy(shelf_path, backup)

def update_tool(data):
    '''
    Sets the tool script to be the selected nodes as python code.
    If multiple nodes are selected they will be collapsed into a subnet, and the subnet script will be added to
    the tool. A script is added to the tool to automatically delete the parent subnet if it exists.
    The prescript makes sure the nodes match the current network pane.
    '''
    # Get relevant data
    nodes = data['nodes']
    shelf_path = data['shelf_path']
    tool = data['tool']
    menu_op_type = data['menu_op_type']
    menu_locations = data['menu_locations']
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
    node_asCode = node.asCode(brief=True, recurse=True)
    
    # code to be appended at the end of tool script: removes subnet
    extract_nodes = "hou_node.extractAndDelete()"

    # Add parm 'preset_name', 'shelf_name' to nodes
    post_script = """
parms = []
parms.append(hou_node.parm('shelf_name'))
parms.append(hou_node.parm('preset_name'))
for parm in parms:
    if parm.isHidden() == True:
        parm.hide(False)
    else:
        parm.hide(True)
    """

    # Combine all script to make final tool script
    if len(nodes) > 1:
        script = pre_script + node_asCode + extract_nodes
    else:
        script = pre_script + node_asCode

    # Set tool script, logo, pane type and menu location
    tool.setData(script=script, icon='R:/Houdini/Houdini_otls/master/Menhir/menhirfx_logo_inbox128.png')
    tool.setFilePath(shelf_path)
    tool.setToolMenuOpType(hou.paneTabType.NetworkEditor, menu_op_type)
    tool.setToolLocations(menu_locations)
    
    # Delete subnet if created
    if len(nodes) > 1:
        subnet.extractAndDelete()

    logger.info('Tool updated')
    
def get_tool_info():
    '''Returns a dict with all relevant information about the tool to update'''
    data = {
        'nodes' : None,
        'tool' : None,
        'shelf' : None,
        'shelf_path' : None,
        'menu_op_type' : None,
        'menu_locations' : None
    }
    data['nodes'] = get_selected_nodes()
    preset_info = get_preset_info(data['nodes'])
    data['shelf'] = get_shelf(preset_info['shelf_name'])
    data['shelf_path'] = data['shelf'].filePath()
    data['tool'] = get_tool_to_update(preset_info, data['shelf'])
    data['menu_op_type'] = data['tool'].toolMenuOpType(hou.paneTabType.NetworkEditor)
    data['menu_locations'] = data['tool'].toolMenuLocations()
    return data
  
    
def run():
    '''Runs the updating process'''
    data = get_tool_info()
    back_up_shelf(data['shelf'], data['shelf_path'])
    update_tool(data)
    
run()

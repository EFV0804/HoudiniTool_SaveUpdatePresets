'''Hides/Unhides the parms 'shelf_name' and 'preset_name' '''
nodes = hou.selectedNodes()

for node in nodes:
    parms = []
    parms.append(node.parm('shelf_name'))
    parms.append(node.parm('preset_name'))
    for parm in parms:
        if parm.isHidden() == True:
            parm.hide(False)
        else:
            parm.hide(True)
'''Add 'shelf_name' and 'preset_name' to the selected nodes'''
nodes = hou.selectedNodes()

for node in nodes:
    node.addSpareParmTuple(hou.StringParmTemplate('preset_name', 'Preset Name', 1))
    node.addSpareParmTuple(hou.StringParmTemplate('shelf_name', 'Shelf Name', 1))
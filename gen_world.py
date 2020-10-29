import xml.etree.ElementTree as ET
import numpy as np
from hexagon import generate_maze
import xml.dom.minidom

wall_count = 0

def add_include_object(parent, uri_name, name=None, pose=None):
    include = ET.SubElement(parent, 'include')
    uri = ET.SubElement(include, 'uri')
    uri.text = f"model://{uri_name}"
    if name:
        name_xml = ET.SubElement(include, 'name')
        name_xml.text = name
    if pose:
        pose_xml = ET.SubElement(include, 'pose')
        pose_xml.text = pose    

def add_tankbot(parent):
    model = ET.SubElement(parent, 'model')
    model.set('name', 'tankbot0')
    pose_xml = ET.SubElement(model, 'pose')
    pose_xml.text = "-20 0 0 0 0 0"    
    add_include_object(model, "tankbot")
    plugin_xml = ET.SubElement(model, 'plugin')
    plugin_xml.set('name', "tankbot_control")
    plugin_xml.set('filename', "libtank_control_plugin.so")

def add_wall(parent,x,y,z=0, r1=0, r2=0, r3=0):
    pose = " ".join(str(x) for x in [x,y,z,r1,r2,r3])
    global wall_count
    add_include_object(parent, "brick_box_3x1x3", f"wall{wall_count}", pose)
    wall_count += 1

def write_xml_file(xml_data, file_name):
    # mydata = str(ET.tostring(xml_data))[2:-1]
    xml_string = xml.dom.minidom.parseString(ET.tostring(xml_data)).toprettyxml()
    with open(file_name, "w") as f:
        f.write(xml_string)

def setup_world(parent):
    world = ET.SubElement(parent, 'world')
    world.set('name', 'default')

    add_include_object(world, 'sun')
    add_include_object(world, 'ground_plane')
    add_include_object(world, 'checkerboard_plane', 'goal', '0 0 0.01 0 0 0')
    add_tankbot(world)

    return world

direction_to_position = {
    "_":(90,0),
    "/":(-45,1),
    "\\":(45,1)
}

def add_hexagon_maze_walls(parent):

    rows = generate_maze()

    for i,row in enumerate(rows, -len(rows)//2):
        for j, val in enumerate(row, -len(rows)//2):
            if val in direction_to_position and (i or j):
                angle, shift = direction_to_position[val]
                add_wall(parent, i*2-shift, j*2, r3=np.radians(angle))

if __name__ == "__main__":
    sdf = ET.Element('sdf')
    sdf.set('version', '1.5')
    world = setup_world(sdf)

    add_hexagon_maze_walls(world)
    write_xml_file(sdf, "hexagon_world.world")
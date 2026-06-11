import bpy
import math
import os
from mathutils import Vector
from math import sin, cos, pi

OUT_ROOT = "/root/3d/assets/wizard_clothing_v1"
os.makedirs(OUT_ROOT, exist_ok=True)

# ---------- basic setup ----------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def mat(name, color, roughness=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    return m

PURPLE = None
PURPLE_DARK = None
PURPLE_LIGHT = None
GOLD = None
BROWN = None
BROWN_DARK = None
CREAM = None
CHROMA = None


def make_materials():
    global PURPLE, PURPLE_DARK, PURPLE_LIGHT, GOLD, BROWN, BROWN_DARK, CREAM, CHROMA
    PURPLE = mat('flat warm wizard purple', (0.36, 0.22, 0.58, 1))
    PURPLE_DARK = mat('flat dark wizard purple', (0.22, 0.13, 0.36, 1))
    PURPLE_LIGHT = mat('flat soft purple highlight', (0.50, 0.34, 0.72, 1))
    GOLD = mat('flat soft gold', (0.95, 0.68, 0.24, 1))
    BROWN = mat('flat warm leather brown', (0.45, 0.25, 0.14, 1))
    BROWN_DARK = mat('flat dark leather edge', (0.25, 0.14, 0.08, 1))
    CREAM = mat('flat warm cream mannequin', (0.86, 0.72, 0.52, 1))
    CHROMA = mat('chroma green background', (0.333, 0.8, 0.266, 1))


def assign(obj, material):
    obj.data.materials.append(material)
    return obj


def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def add_cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel > 0:
        mod = obj.modifiers.new('tiny rounded toy bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        mod.affect = 'EDGES'
        bpy.ops.object.shade_flat()
    return shade_flat(obj)


def add_cyl(name, loc, radius, depth, material, vertices=10, rotation=(0,0,0), scale=(1,1,1), bevel=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel:
        mod = obj.modifiers.new('small bevel', 'BEVEL')
        mod.width = 0.035
        mod.segments = 1
    return shade_flat(obj)


def add_cone(name, loc, r1, r2, depth, material, vertices=10, rotation=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    return shade_flat(obj)


def add_uv_sphere(name, loc, radius, material, segments=10, rings=5, scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    return shade_flat(obj)


def star_mesh(name, loc, radius_outer, radius_inner, material, thickness=0.025, points=5):
    verts = []
    faces = []
    for z in [-thickness/2, thickness/2]:
        for i in range(points*2):
            r = radius_outer if i % 2 == 0 else radius_inner
            a = pi/2 + i*pi/points
            verts.append((loc[0] + r*cos(a), loc[1] + z, loc[2] + r*sin(a)))
    faces.append(tuple(range(points*2)))
    faces.append(tuple(range(points*2, points*4)))
    for i in range(points*2):
        faces.append((i, (i+1)%(points*2), (i+1)%(points*2)+points*2, i+points*2))
    mesh = bpy.data.meshes.new(name+'Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, material)
    return shade_flat(obj)


def crescent_mesh(name, loc, radius_outer, radius_inner, material, thickness=0.025):
    # simple flat crescent in XZ plane, thickness on Y
    verts_front = []
    verts_back = []
    # outer arc left-to-right
    for i in range(18):
        a = math.radians(105 + i * 250/17)
        verts_front.append((loc[0] + radius_outer*cos(a), loc[1]-thickness/2, loc[2] + radius_outer*sin(a)))
    # inner arc back toward start, shifted right/up to create crescent bite
    for i in range(18):
        a = math.radians(355 - i * 250/17)
        verts_front.append((loc[0] + 0.12 + radius_inner*cos(a), loc[1]-thickness/2, loc[2] + 0.03 + radius_inner*sin(a)))
    verts_back = [(x, loc[1]+thickness/2, z) for x,_,z in verts_front]
    verts = verts_front + verts_back
    n = len(verts_front)
    faces = [tuple(range(n)), tuple(range(n,2*n))]
    for i in range(n):
        faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
    mesh = bpy.data.meshes.new(name+'Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, material)
    return shade_flat(obj)


def setup_camera(target=(0,0,0.6), distance=5.2, height=2.4):
    bpy.ops.object.light_add(type='AREA', location=(0, -3.5, 4.5))
    light = bpy.context.object
    light.name = 'large soft neutral light'
    light.data.energy = 420
    light.data.size = 5.0
    bpy.ops.object.camera_add(location=(3.2, -5.0, height), rotation=(math.radians(62), 0, math.radians(35)))
    cam = bpy.context.object
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
    cam.data.lens = 60
    bpy.context.scene.camera = cam
    # simple green floor + back wall for chroma approval; not exported
    add_cube('flat chroma base plane', (0,0,-0.055), (5.2,5.2,0.04), CHROMA, bevel=0)
    add_cube('flat chroma background wall', (0,2.05,1.75), (5.2,0.04,3.6), CHROMA, bevel=0)


def render_asset(asset_name, camera_target, height=2.4):
    setup_camera(target=camera_target, height=height)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.taa_render_samples = 32
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 1200
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'Medium High Contrast'
    bpy.context.scene.world.color = (0.333, 0.8, 0.266)
    out_dir = os.path.join(OUT_ROOT, asset_name)
    os.makedirs(out_dir, exist_ok=True)
    bpy.context.scene.render.filepath = os.path.join(out_dir, 'perspective.png')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, 'source.blend'))
    bpy.ops.render.render(write_still=True)
    # export glb without camera/light/green plane
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and not obj.name.startswith('flat chroma'):
            obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, 'model.glb'), use_selection=True, export_format='GLB')

# ---------- mesh helpers ----------
def bent_hat_body():
    # faceted cone with curved drooping tip, wide base, not realistic
    rings = [
        (0.00, 0.62, 0.00),
        (0.38, 0.50, 0.03),
        (0.78, 0.38, 0.08),
        (1.14, 0.27, 0.18),
        (1.42, 0.18, 0.34),
        (1.58, 0.10, 0.48),
    ]
    verts=[]; faces=[]; seg=9
    for z,r,offx in rings:
        for i in range(seg):
            a=2*pi*i/seg
            verts.append((offx + r*cos(a), r*0.72*sin(a), z))
    for j in range(len(rings)-1):
        for i in range(seg):
            faces.append((j*seg+i, j*seg+(i+1)%seg, (j+1)*seg+(i+1)%seg, (j+1)*seg+i))
    faces.append(tuple(range(seg-1,-1,-1)))
    faces.append(tuple(range((len(rings)-1)*seg, len(rings)*seg)))
    mesh=bpy.data.meshes.new('wizardHatBodyMesh')
    mesh.from_pydata(verts, [], faces); mesh.update()
    obj=bpy.data.objects.new('single-piece bent wizard hat cone', mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, PURPLE)
    return shade_flat(obj)


def create_wizard_hat():
    clear_scene(); make_materials()
    add_cyl('wide floppy low-poly brim', (0,0,0.10), 0.98, 0.14, PURPLE, vertices=12, scale=(1.18,0.86,1), bevel=True)
    add_cyl('dark lower brim shadow', (0,0,0.02), 0.98, 0.055, PURPLE_DARK, vertices=12, scale=(1.14,0.82,1))
    bent_hat_body()
    add_cyl('simple warm leather hat band', (0,0,0.34), 0.64, 0.17, BROWN, vertices=12, scale=(1.04,0.76,1), bevel=True)
    crescent_mesh('soft gold crescent charm on hat band', (-0.18,-0.63,0.42), 0.22, 0.16, GOLD, thickness=0.035)
    star_mesh('small simple gold star on hat band', (0.30,-0.65,0.48), 0.105, 0.048, GOLD, thickness=0.035)
    render_asset('wizard_hat', camera_target=(0.1,0,0.75), height=2.1)


def create_wizard_robe():
    clear_scene(); make_materials()
    # mannequin bits only for approval silhouette
    add_uv_sphere('simple warm cream round head placeholder', (0,0,1.82), 0.29, CREAM, segments=10, rings=5, scale=(0.92,0.92,1.08))
    add_cone('soft trapezoid purple robe body', (0,0,0.78), 0.66, 0.43, 1.30, PURPLE, vertices=10, scale=(0.92,0.70,1))
    add_cone('dark inner front robe split left', (-0.13,-0.49,0.32), 0.05, 0.02, 0.45, PURPLE_DARK, vertices=4, rotation=(0,0,math.radians(16)), scale=(0.8,0.35,1))
    add_cone('dark inner front robe split right', (0.13,-0.49,0.32), 0.05, 0.02, 0.45, PURPLE_DARK, vertices=4, rotation=(0,0,math.radians(-16)), scale=(0.8,0.35,1))
    add_cyl('thick cozy shoulder collar', (0,-0.01,1.36), 0.55, 0.20, PURPLE_LIGHT, vertices=10, scale=(1.12,0.78,1), bevel=True)
    add_cube('front collar left flap', (-0.22,-0.43,1.25), (0.42,0.12,0.18), PURPLE_LIGHT, bevel=0.025)
    bpy.context.object.rotation_euler[2] = math.radians(-18)
    add_cube('front collar right flap', (0.22,-0.43,1.25), (0.42,0.12,0.18), PURPLE_LIGHT, bevel=0.025)
    bpy.context.object.rotation_euler[2] = math.radians(18)
    add_cyl('warm leather belt around robe', (0,0,0.77), 0.58, 0.13, BROWN, vertices=10, scale=(1.02,0.72,1), bevel=True)
    add_cube('simple square gold belt buckle', (0,-0.53,0.78), (0.20,0.055,0.20), GOLD, bevel=0.018)
    add_cube('buckle hole purple', (0,-0.565,0.78), (0.105,0.035,0.095), PURPLE_DARK, bevel=0.01)
    # sleeves and hands
    add_cyl('left chunky short sleeve', (-0.58,-0.03,0.90), 0.17, 0.70, PURPLE, vertices=8, rotation=(0,math.radians(18),0), scale=(0.86,0.86,1))
    add_cyl('right chunky short sleeve', (0.58,-0.03,0.90), 0.17, 0.70, PURPLE, vertices=8, rotation=(0,math.radians(-18),0), scale=(0.86,0.86,1))
    add_uv_sphere('left simple hand placeholder', (-0.78,-0.02,0.50), 0.10, CREAM, segments=8, rings=4, scale=(0.85,0.85,0.95))
    add_uv_sphere('right simple hand placeholder', (0.78,-0.02,0.50), 0.10, CREAM, segments=8, rings=4, scale=(0.85,0.85,0.95))
    # trims
    add_cyl('simple gold lower robe trim', (0,0,0.16), 0.64, 0.055, GOLD, vertices=10, scale=(0.94,0.70,1))
    add_cyl('left sleeve gold cuff', (-0.75,-0.03,0.56), 0.17, 0.055, GOLD, vertices=8, rotation=(0,math.radians(18),0), scale=(0.86,0.86,1))
    add_cyl('right sleeve gold cuff', (0.75,-0.03,0.56), 0.17, 0.055, GOLD, vertices=8, rotation=(0,math.radians(-18),0), scale=(0.86,0.86,1))
    crescent_mesh('simple gold moon charm on robe', (0,-0.55,1.03), 0.16, 0.115, GOLD, thickness=0.035)
    star_mesh('tiny diamond clasp on collar', (0,-0.56,1.30), 0.12, 0.06, GOLD, thickness=0.035, points=4)
    add_cube('small brown side pouch', (0.52,-0.48,0.55), (0.22,0.12,0.30), BROWN, bevel=0.025)
    render_asset('wizard_robe', camera_target=(0,0,0.95), height=2.45)


def create_wizard_boots():
    clear_scene(); make_materials()
    for side,x in [('left',-0.32),('right',0.32)]:
        add_cyl(f'{side} boot leg tube', (x,0,0.62), 0.25, 0.72, BROWN, vertices=8, scale=(0.90,0.82,1), bevel=True)
        add_cyl(f'{side} chunky folded cuff', (x,0,1.02), 0.30, 0.20, BROWN, vertices=8, scale=(0.98,0.86,1), bevel=True)
        add_cyl(f'{side} dark boot opening', (x,0,1.14), 0.22, 0.025, BROWN_DARK, vertices=8, scale=(0.98,0.84,1))
        add_cube(f'{side} rounded boot foot', (x,-0.18,0.20), (0.48,0.72,0.32), BROWN, bevel=0.045)
        add_cube(f'{side} darker simple sole', (x,-0.19,0.045), (0.54,0.80,0.11), BROWN_DARK, bevel=0.025)
        add_cube(f'{side} cute squared toe cap', (x,-0.54,0.24), (0.50,0.28,0.28), BROWN, bevel=0.04)
    render_asset('wizard_boots', camera_target=(0,0,0.55), height=1.65)


def create_wizard_satchel():
    clear_scene(); make_materials()
    add_cube('rounded square leather bag body', (0,0,0.48), (0.86,0.44,0.78), BROWN, bevel=0.055)
    add_cyl('rolled top cylinder flap hinge', (0,-0.02,0.90), 0.23, 0.88, BROWN, vertices=10, rotation=(0,math.radians(90),0), scale=(0.92,0.92,1), bevel=True)
    add_cube('front flap soft trapezoid block', (0,-0.27,0.59), (0.72,0.12,0.50), BROWN, bevel=0.045)
    add_cube('lower gold chevron trim', (0,-0.35,0.32), (0.38,0.055,0.08), GOLD, bevel=0.015)
    bpy.context.object.rotation_euler[2] = math.radians(0)
    star_mesh('simple gold star charm on satchel flap', (0,-0.35,0.62), 0.13, 0.06, GOLD, thickness=0.035)
    # handle as blocky arch made of cylinders/cubes
    add_cyl('left leather strap side', (-0.42,0.02,1.15), 0.055, 0.88, BROWN_DARK, vertices=8, rotation=(math.radians(18),0,0), scale=(0.9,0.9,1))
    add_cyl('right leather strap side', (0.42,0.02,1.15), 0.055, 0.88, BROWN_DARK, vertices=8, rotation=(math.radians(-18),0,0), scale=(0.9,0.9,1))
    add_cube('blocky leather strap top', (0,0.04,1.58), (0.80,0.11,0.12), BROWN_DARK, bevel=0.025)
    # buckle on side/back visible
    add_cube('small gold side buckle outer', (0.48,-0.18,0.93), (0.16,0.055,0.20), GOLD, bevel=0.014)
    add_cube('small side buckle hole', (0.48,-0.215,0.93), (0.085,0.035,0.105), BROWN_DARK, bevel=0.008)
    # potion charm
    add_cyl('gold ring holding potion', (0.66,-0.12,0.66), 0.055, 0.12, GOLD, vertices=8, rotation=(math.radians(90),0,0))
    add_cyl('tiny potion gold cap', (0.78,-0.12,0.58), 0.09, 0.10, GOLD, vertices=8)
    add_cyl('purple potion gem body', (0.78,-0.12,0.40), 0.13, 0.26, PURPLE, vertices=8, scale=(0.82,0.82,1))
    add_cone('purple potion point bottom', (0.78,-0.12,0.22), 0.11, 0.03, 0.18, PURPLE_LIGHT, vertices=8)
    render_asset('wizard_satchel', camera_target=(0.08,0,0.80), height=2.1)


if __name__ == '__main__':
    create_wizard_hat()
    create_wizard_robe()
    create_wizard_boots()
    create_wizard_satchel()

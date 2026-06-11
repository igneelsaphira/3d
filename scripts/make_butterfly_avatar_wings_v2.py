import bpy, math, os
from math import sin, cos, pi, radians
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont

ROOT = '/root/3d/assets/cozy_reference_assets_v1/butterfly_avatar_wings_v2'
os.makedirs(ROOT, exist_ok=True)

M = {}

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    M.clear()


def mat(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.9
    M[name] = m
    return m


def materials():
    mat('skin', (0.96, 0.76, 0.52, 1))
    mat('body_red', (0.86, 0.16, 0.13, 1))
    mat('wing_orange', (1.0, 0.49, 0.14, 1))
    mat('wing_border', (0.045, 0.045, 0.055, 1))
    mat('white_spot', (0.96, 0.96, 0.90, 1))
    mat('chroma', (0.333, 0.8, 0.266, 1))


def assign(obj, material):
    obj.data.materials.append(M[material])
    return obj


def flat(obj):
    if hasattr(obj.data, 'polygons'):
        for p in obj.data.polygons:
            p.use_smooth = False
    return obj


def cyl(name, loc, radius, depth, material, vertices=10, rot=(0,0,0), scale=(1,1,1), bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel:
        mod = obj.modifiers.new('simple toy bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return flat(obj)


def sphere(name, loc, radius, material, seg=10, rings=5, scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    return flat(obj)


def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel:
        mod = obj.modifiers.new('simple toy bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return flat(obj)


def panel_mesh(name, points_xz, material, thickness=0.035, y=0.0):
    # Flat polygon panel in XZ, with a tiny thickness along Y.
    verts = [(x, y-thickness/2, z) for x,z in points_xz] + [(x, y+thickness/2, z) for x,z in points_xz]
    n = len(points_xz)
    faces = [tuple(range(n)), tuple(range(n, 2*n))]
    for i in range(n):
        faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
    mesh = bpy.data.meshes.new(name + 'Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, material)
    return flat(obj)


def oval_dot(name, loc, scale):
    # Low-poly flattened spot sitting slightly in front of the black border.
    return sphere(name, loc, 0.075, 'white_spot', seg=8, rings=4, scale=scale)


def make_character():
    clear(); materials()

    # Base avatar is intentionally unchanged: round head, small ears, simple red body.
    cyl('rounded red capsule body', (0,0,0.72), 0.32, 1.05, 'body_red', vertices=10, scale=(0.9,0.86,1), bevel=0.035)
    sphere('large round head', (0,-0.015,1.45), 0.43, 'skin', seg=10, rings=5, scale=(1.05,1.0,1.02))
    sphere('left simple ear', (-0.42,-0.02,1.45), 0.10, 'skin', seg=8, rings=4, scale=(0.82,0.70,1.0))
    sphere('right simple ear', (0.42,-0.02,1.45), 0.10, 'skin', seg=8, rings=4, scale=(0.82,0.70,1.0))
    sphere('left black oval eye', (-0.14,-0.385,1.50), 0.057, 'wing_border', seg=8, rings=4, scale=(0.65,0.34,1.25))
    sphere('right black oval eye', (0.14,-0.385,1.50), 0.057, 'wing_border', seg=8, rings=4, scale=(0.65,0.34,1.25))

    # Wing v2: closer to the reference silhouette.
    # Conserves two-piece-per-side structure: large upper lobe + smaller lower lobe, joined at body/back.
    for label, sgn in [('left', -1), ('right', 1)]:
        # Upper wing: broad, rounded, tilted up/out. Root starts behind shoulders, outer tip rounded.
        upper_outer_pts = [
            (0.02, 1.20), (0.18, 1.43), (0.44, 1.58), (0.76, 1.56),
            (0.98, 1.38), (1.03, 1.13), (0.90, 0.92), (0.58, 0.88),
            (0.25, 0.99)
        ]
        upper_inner_pts = [
            (0.14, 1.19), (0.27, 1.38), (0.49, 1.48), (0.72, 1.46),
            (0.86, 1.31), (0.88, 1.13), (0.75, 1.00), (0.52, 0.97),
            (0.27, 1.06)
        ]
        # Lower wing: smaller rounded teardrop, down/out but still attached to the same base.
        lower_outer_pts = [
            (0.02, 0.78), (0.26, 0.94), (0.62, 0.88), (0.83, 0.68),
            (0.82, 0.43), (0.58, 0.25), (0.30, 0.28), (0.11, 0.47)
        ]
        lower_inner_pts = [
            (0.13, 0.76), (0.31, 0.86), (0.56, 0.81), (0.69, 0.66),
            (0.68, 0.49), (0.52, 0.37), (0.32, 0.39), (0.19, 0.52)
        ]

        # Mirror using object scale, keeping base and proportions identical per side.
        uo = panel_mesh('v2 black upper wing ' + label, upper_outer_pts, 'wing_border', thickness=0.045, y=0.16)
        uo.scale.x = sgn
        ui = panel_mesh('v2 orange upper wing ' + label, upper_inner_pts, 'wing_orange', thickness=0.050, y=0.105)
        ui.scale.x = sgn
        # Duplicate the simple orange panels on the back face too, so BACK view keeps the reference's orange wings
        # instead of turning into a flat black silhouette.
        ui_back = panel_mesh('v2 rear orange upper wing ' + label, upper_inner_pts, 'wing_orange', thickness=0.030, y=0.210)
        ui_back.scale.x = sgn
        lo = panel_mesh('v2 black lower wing ' + label, lower_outer_pts, 'wing_border', thickness=0.045, y=0.17)
        lo.scale.x = sgn
        li = panel_mesh('v2 orange lower wing ' + label, lower_inner_pts, 'wing_orange', thickness=0.050, y=0.105)
        li.scale.x = sgn
        li_back = panel_mesh('v2 rear orange lower wing ' + label, lower_inner_pts, 'wing_orange', thickness=0.030, y=0.210)
        li_back.scale.x = sgn

        # Large simplified veins: not new decorative objects, just the reference's black segmentation simplified.
        vein_specs = [
            ((sgn*0.34, 0.075, 1.20), (0.070, 0.045, 0.58), -36*sgn),
            ((sgn*0.55, 0.075, 1.20), (0.065, 0.045, 0.48), -15*sgn),
            ((sgn*0.43, 0.075, 0.68), (0.060, 0.045, 0.38), 33*sgn),
        ]
        for i,(loc,sc,rot_z) in enumerate(vein_specs):
            v = cube(f'v2 simple black wing vein {label} {i}', loc, sc, 'wing_border', bevel=0.008)
            v.rotation_euler[1] = radians(rot_z)

        # Spots remain only on outer black border, fewer/larger so they read in mobile thumbnails.
        for i,(x,z,rx,rz) in enumerate([
            (0.86,1.40,0.85,0.62), (0.98,1.18,0.78,0.58), (0.83,0.98,0.72,0.55),
            (0.70,0.60,0.72,0.55), (0.56,0.34,0.70,0.54)
        ]):
            oval_dot(f'v2 clean border spot {label} {i}', (sgn*x, 0.055, z), (rx,0.32,rz))

    # Back joint visible in reference; simple black connector where wings attach.
    sphere('simple black back wing joint', (0,0.19,0.95), 0.15, 'wing_border', seg=8, rings=4, scale=(0.92,0.70,1.05))


def add_preview_environment():
    # Floor only: a fixed back wall blocks the BACK camera in multi-view renders.
    # The world color remains chroma green, so all angles stay readable.
    cube('chroma floor', (0,0,-0.08), (5.2,5.2,0.04), 'chroma')
    bpy.ops.object.light_add(type='AREA', location=(0,-3.7,4.2))
    light = bpy.context.object
    light.name = 'large soft preview light'
    light.data.energy = 430
    light.data.size = 5.0
    bpy.ops.object.light_add(type='AREA', location=(0,3.7,3.6))
    back_light = bpy.context.object
    back_light.name = 'soft back view fill light'
    back_light.data.energy = 220
    back_light.data.size = 5.0


def set_camera(view):
    targets = {
        'front': ((0,-4.6,1.08), (0,0,1.02), 62),
        'side': ((4.6,0,1.08), (0,0,1.02), 62),
        'back': ((0,4.6,1.08), (0,0,1.02), 62),
        'perspective': ((3.0,-4.6,2.25), (0,0,1.02), 58),
    }
    loc, target, lens = targets[view]
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
    cam.data.lens = lens
    bpy.context.scene.camera = cam


def setup_render():
    engine_ids = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engine_ids else 'BLENDER_EEVEE'
    if hasattr(bpy.context.scene, 'eevee'):
        bpy.context.scene.eevee.taa_render_samples = 32
    bpy.context.scene.render.resolution_x = 1000
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.world.color = (0.333,0.8,0.266)


def render_views():
    setup_render()
    add_preview_environment()
    views = ['front','side','back','perspective']
    for view in views:
        # remove old cameras only
        for obj in list(bpy.context.scene.objects):
            if obj.type == 'CAMERA':
                bpy.data.objects.remove(obj, do_unlink=True)
        set_camera(view)
        bpy.context.scene.render.filepath = os.path.join(ROOT, f'{view}.png')
        bpy.ops.render.render(write_still=True)

    # Save source after cameras/env for editable inspection; export runtime meshes without env/camera/light.
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'source.blend'))
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and not obj.name.startswith('chroma'):
            obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT, 'model.glb'), use_selection=True, export_format='GLB')


def make_contact_sheet():
    labels = [('front','FRONT'),('side','SIDE'),('back','BACK'),('perspective','PERSPECTIVE')]
    cell = 520; gap = 22; top = 95
    w = cell*2 + gap*3
    h = top + cell*2 + gap*2 + 20
    sheet = Image.new('RGB', (w,h), (50,190,42))
    d = ImageDraw.Draw(sheet)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    title_font = ImageFont.truetype(font_path, 42)
    label_font = ImageFont.truetype(font_path, 30)
    title = 'Butterfly Avatar Wings v2 - multi-view'
    tw = d.textlength(title, font=title_font)
    d.text(((w-tw)/2, 28), title, fill='white', font=title_font)
    positions = [(gap,top), (gap*2+cell,top), (gap,top+cell+gap), (gap*2+cell,top+cell+gap)]
    for (name,label),(x,y) in zip(labels,positions):
        img = Image.open(os.path.join(ROOT, f'{name}.png')).convert('RGB').resize((cell,cell))
        d.rounded_rectangle([x-4,y-4,x+cell+4,y+cell+4], radius=22, outline=(255,235,160), width=7)
        sheet.paste(img,(x,y))
        d.rounded_rectangle([x+110,y+12,x+cell-110,y+56], radius=15, fill=(56,55,70), outline=(255,220,120), width=2)
        lw = d.textlength(label, font=label_font)
        d.text((x+cell/2-lw/2,y+18), label, fill='white', font=label_font)
    sheet.save(os.path.join(ROOT, 'contact_sheet.png'))


if __name__ == '__main__':
    make_character()
    render_views()
    make_contact_sheet()

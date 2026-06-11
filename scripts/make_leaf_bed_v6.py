import bpy
import math
import zipfile
from pathlib import Path
from mathutils import Vector

OUT_DIR = Path('/root/leaf_bed_v6')
OUT_DIR.mkdir(exist_ok=True)
OUT_BLEND = OUT_DIR / 'leaf_bed_v6_model.blend'
OUT_GLB = OUT_DIR / 'leaf_bed_v6_model.glb'
CONTACT = OUT_DIR / 'leaf_bed_v6_contact_sheet.png'
ZIP_PATH = Path('/root/leaf_bed_v6_assets.zip')
CHROMA = '#55cc44'

PALETTE = {
    'bg': CHROMA,
    'cream': '#F3E8D0',
    'cream_shadow': '#E5D1A8',
    'pillow': '#F0E2C3',
    'wood': '#B77A45',
    'wood_light': '#D29A5E',
    'wood_dark': '#8E5B34',
    'leaf': '#3F7C24',
    'leaf_edge': '#4D8C2B',
    'leaf_shadow': '#477F29',
    'leaf_vein': '#7FA849',
}

# ---------------- helpers ----------------
def hex_rgba(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)

def clean():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
clean()

def make_mat(name, color, roughness=0.92):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = hex_rgba(color)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = hex_rgba(color)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = 0
    return mat
M = {name: make_mat(name, color) for name, color in PALETTE.items()}

def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass
    obj.select_set(False)

def cube(name, loc, scale, mat, bevel=0.0, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        be = obj.modifiers.new('soft_round_bevel', 'BEVEL')
        be.width = bevel
        be.segments = 1
        be.profile = 0.55
        apply_modifiers(obj)
    return obj

def cyl(name, loc, radius, depth, mat, vertices=8, rot=(0,0,0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        be = obj.modifiers.new('cap_soft_bevel', 'BEVEL')
        be.width = bevel
        be.segments = 1
        apply_modifiers(obj)
    return obj

def mesh_obj(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# ---------------- compact cute bed base ----------------
# Slightly smaller and lower than v3; warmer rounded wood, shorter legs.
cube('compact_rounded_wood_base', (0, 0.00, 0.20), (1.24, 1.58, 0.16), M['wood'], 0.055)
cube('soft_front_rail', (0, -0.82, 0.39), (1.34, 0.13, 0.22), M['wood_light'], 0.05)
cube('left_rounded_rail', (-0.66, -0.02, 0.40), (0.12, 1.52, 0.22), M['wood'], 0.045)
cube('right_rounded_rail', (0.66, -0.02, 0.40), (0.12, 1.52, 0.22), M['wood'], 0.045)
# Clean warm mattress, visible only as tidy border under leaf.
cube('clean_warm_cream_mattress', (0, -0.04, 0.50), (1.06, 1.38, 0.17), M['cream'], 0.08)
cube('single_soft_mattress_front_band', (0, -0.70, 0.48), (0.92, 0.030, 0.06), M['cream_shadow'], 0.01)

# Simple rounded pillow; low and clean, peeking behind blanket.
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.5, location=(0, 0.50, 0.65))
pillow = bpy.context.object
pillow.name = 'simple_rounded_cream_pillow'
pillow.scale = (0.52, 0.22, 0.12)
pillow.data.materials.append(M['pillow'])
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Shorter cute posts.
for name, x, y, h in [
    ('front_left_short_post', -0.68, -0.82, 0.50),
    ('front_right_short_post', 0.68, -0.82, 0.50),
    ('back_left_short_post', -0.68, 0.74, 0.82),
    ('back_right_short_post', 0.68, 0.74, 0.82),
]:
    cyl(name, (x, y, h/2), 0.072, h, M['wood_dark'], vertices=8, bevel=0.014)
    cyl(name + '_soft_honey_cap', (x, y, h + 0.035), 0.088, 0.07, M['wood_light'], vertices=8, bevel=0.012)

# Lower rounded headboard, toy-like.
front_y = 0.79
back_y = 0.69
outline = [
    (-0.56, 0.28), (-0.56, 0.66), (-0.44, 0.77), (-0.20, 0.84),
    (0.00, 0.865), (0.20, 0.84), (0.44, 0.77), (0.56, 0.66), (0.56, 0.28)
]
verts = [(x, front_y, z) for x, z in outline] + [(x, back_y, z) for x, z in outline]
faces = [tuple(range(len(outline))), tuple(range(len(outline), len(outline)*2))]
n = len(outline)
for i in range(n):
    faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
mesh_obj('lower_rounded_honey_headboard', verts, faces, M['wood_light'])
for i, x in enumerate([-0.30, 0, 0.30], 1):
    cube(f'headboard_subtle_inset_{i}', (x, front_y + 0.018, 0.55), (0.020, 0.020, 0.24), M['wood'], 0.004)

# ---------------- soft leaf blanket ----------------
# One organized puffy leaf: natural green, rounded rows, no broken white bits.
# 7 points per row: rounded edge -> soft shoulders -> raised center -> soft shoulders -> rounded edge.
rows = [
    # y, half_width, center_z, edge_drop
    (-0.84, 0.36, 0.555, 0.030),
    (-0.72, 0.54, 0.598, 0.032),
    (-0.52, 0.62, 0.638, 0.028),
    (-0.26, 0.64, 0.672, 0.022),
    ( 0.00, 0.59, 0.692, 0.020),
    ( 0.25, 0.45, 0.686, 0.018),
    ( 0.45, 0.25, 0.660, 0.016),
    ( 0.57, 0.07, 0.635, 0.010),
]
verts = []
for y, hw, cz, drop in rows:
    verts.extend([
        (-hw, y, cz - drop),
        (-hw*0.72, y, cz - drop*0.35),
        (-hw*0.34, y, cz + 0.018),
        (0.0, y, cz + 0.038),
        (hw*0.34, y, cz + 0.018),
        (hw*0.72, y, cz - drop*0.35),
        (hw, y, cz - drop),
    ])
faces = []
cols = 7
for i in range(len(rows)-1):
    a = i * cols
    b = (i+1) * cols
    for c in range(cols-1):
        faces.append((a+c, b+c, b+c+1, a+c+1))
leaf = mesh_obj('single_soft_puffy_leaf_blanket', verts, faces, M['leaf'])

# Darker soft front lip reads as blanket thickness, not a broken shard.
front_lip = [
    (-0.44, -0.76, 0.565), (0.44, -0.76, 0.565),
    (0.34, -0.89, 0.510), (-0.34, -0.89, 0.510)
]
mesh_obj('rounded_leaf_front_blanket_lip', front_lip, [(0,1,2,3)], M['leaf_edge'])
# Side thickness removed to avoid a dark stripe; the arched mesh and front lip provide clean soft volume.

# Integrated veins: 1 central + 6 side veins max, thin and low-contrast.
central = cube('integrated_thin_central_leaf_vein', (0, -0.16, 0.716), (0.016, 1.14, 0.004), M['leaf_vein'], 0.004)
# 3 pairs = 6 lateral veins, shorter, flat on the surface; no white sticks.
for i, (x, y, angle, length) in enumerate([
    (-0.095, -0.48,  32, 0.34), (0.095, -0.48, -32, 0.34),
    (-0.100, -0.22,  43, 0.38), (0.100, -0.22, -43, 0.38),
    (-0.085,  0.05,  54, 0.30), (0.085,  0.05, -54, 0.30),
], 1):
    strip = cube(f'integrated_soft_side_leaf_vein_{i}', (x, y, 0.720), (0.010, length, 0.004), M['leaf_vein'], 0.003)
    strip.rotation_euler[2] = math.radians(angle)

# ---------------- scene setup ----------------
bpy.ops.object.select_all(action='DESELECT')
mesh_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for obj in mesh_objs:
    obj.select_set(True)
    try:
        obj.visible_shadow = False
    except Exception:
        pass
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

# Soft bright preview lights.
bpy.ops.object.light_add(type='AREA', location=(-2.0, -3.0, 4.5))
key = bpy.context.object
key.name = 'large_soft_toy_light'
key.data.energy = 500
key.data.size = 6.5
try: key.data.use_shadow = False
except Exception: pass
bpy.ops.object.light_add(type='POINT', location=(2.2, 2.5, 2.4))
fill = bpy.context.object
fill.name = 'warm_fill_light'
fill.data.energy = 80
try: fill.data.use_shadow = False
except Exception: pass

def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.camera_add(location=(2.15, -2.55, 1.55))
cam = bpy.context.object
cam.name = 'render_camera'
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 1.98
bpy.context.scene.camera = cam

# Render settings.
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
try:
    bpy.context.scene.eevee.taa_render_samples = 64
except Exception:
    pass
bpy.context.scene.view_settings.view_transform = 'Standard'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.world.color = hex_rgba(CHROMA)[:3]
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512

# Save and export runtime GLB: meshes only.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objs:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format='GLB', use_selection=True, export_apply=True, export_animations=False)

# Required views.
views = {
    'FRONT': ((0, -3.0, 0.90), 1.72),
    'SIDE': ((3.0, 0.0, 0.90), 1.72),
    'BACK': ((0, 3.0, 0.90), 1.72),
    'TOP': ((0, -0.001, 4.0), 1.92),
    'PERSPECTIVE': ((2.15, -2.55, 1.55), 1.98),
}
render_paths = []
from PIL import Image, ImageDraw
bg_rgb = tuple(int(CHROMA.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
for name, (loc, scale) in views.items():
    cam.location = loc
    cam.data.ortho_scale = scale
    look_at(cam, (0, -0.04, 0.50))
    out = OUT_DIR / f'leaf_bed_v6_{name.lower()}.png'
    raw = OUT_DIR / f'_raw_{name.lower()}.png'
    bpy.context.scene.render.filepath = str(raw)
    bpy.ops.render.render(write_still=True)
    rgba = Image.open(raw).convert('RGBA')
    bg = Image.new('RGBA', rgba.size, bg_rgb + (255,))
    bg.alpha_composite(rgba)
    bg.convert('RGB').save(out)
    try: raw.unlink()
    except Exception: pass
    render_paths.append(out)

imgs = [Image.open(p).convert('RGB') for p in render_paths]
sheet = Image.new('RGB', (512*3, 512*2), bg_rgb)
positions = [(0,0), (512,0), (1024,0), (0,512), (512,512)]
labels = list(views.keys())
draw = ImageDraw.Draw(sheet)
for img, pos, lab in zip(imgs, positions, labels):
    sheet.paste(img, pos)
    draw.rounded_rectangle([pos[0]+12, pos[1]+12, pos[0]+205, pos[1]+54], radius=8, fill=bg_rgb, outline=(255,255,255), width=2)
    draw.text((pos[0]+24, pos[1]+25), lab, fill=(255,255,255))
sheet.save(CONTACT)

# Stats.
depsgraph = bpy.context.evaluated_depsgraph_get()
tris = 0
for obj in mesh_objs:
    eo = obj.evaluated_get(depsgraph)
    me = eo.to_mesh()
    tris += sum(len(poly.vertices)-2 for poly in me.polygons)
    eo.to_mesh_clear()

# Package.
with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in [OUT_BLEND, OUT_GLB, CONTACT, *render_paths]:
        z.write(p, arcname=p.name)

print('CREATED', OUT_BLEND, OUT_GLB)
for p in render_paths:
    print('RENDER', p)
print('CONTACT', CONTACT)
print('ZIP', ZIP_PATH)
print('MESH_OBJECTS', len(mesh_objs))
print('TRIANGLES_APPROX', tris)
print('MATERIALS', len([m for m in bpy.data.materials if m.users > 0]))
print('GLB_BYTES', OUT_GLB.stat().st_size)
print('ZIP_BYTES', ZIP_PATH.stat().st_size)

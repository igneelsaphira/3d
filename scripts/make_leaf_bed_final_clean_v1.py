import bpy
import math
import zipfile
from pathlib import Path
from mathutils import Vector

OUT_DIR = Path('/root/leaf_bed_final_clean_v1')
OUT_DIR.mkdir(exist_ok=True)
OUT_BLEND = OUT_DIR / 'leaf_bed_final_clean_v1_model.blend'
OUT_GLB = OUT_DIR / 'leaf_bed_final_clean_v1_model.glb'
CONTACT = OUT_DIR / 'leaf_bed_final_clean_v1_contact_sheet.png'
ZIP_PATH = Path('/root/leaf_bed_final_clean_v1_assets.zip')
CHROMA = '#55cc44'

PALETTE = {
    'bg': CHROMA,
    'cream': '#F3E8D0',
    'cream_shadow': '#E5D1A8',
    'pillow': '#F0E2C3',
    'wood': '#B77A45',
    'wood_light': '#D29A5E',
    'wood_dark': '#8E5B34',
    'leaf': '#4D8C2B',
    'leaf_edge': '#5F9934',
    'leaf_shadow': '#3F7C24',
    'leaf_vein': '#6FA241',
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
cube('soft_front_rail', (0, -0.82, 0.315), (1.34, 0.13, 0.12), M['wood_light'], 0.045)
cube('left_rounded_rail', (-0.66, -0.02, 0.35), (0.12, 1.52, 0.16), M['wood'], 0.045)
cube('right_rounded_rail', (0.66, -0.02, 0.35), (0.12, 1.52, 0.16), M['wood'], 0.045)
# Clean warm mattress, visible only as tidy border under leaf.
cube('clean_warm_cream_mattress', (0, -0.04, 0.392), (1.06, 1.38, 0.17), M['cream'], 0.08)
cube('single_soft_mattress_front_band', (0, -0.70, 0.372), (0.92, 0.030, 0.050), M['cream_shadow'], 0.01)

# Simple rounded pillow; low and clean, peeking behind blanket.
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.5, location=(0, 0.50, 0.548))
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
    # Drape correction: the blanket leaf rests close to the mattress top, with only
    # a soft raised midrib. The front becomes a gentle leaf tip falling over the
    # mattress edge instead of a cut flap or a floating slab.
    (-0.955, 0.12, 0.512, 0.006),  # pointed soft tail below/over front mattress edge
    (-0.850, 0.41, 0.510, 0.014),  # first supported row, low and close to mattress
    (-0.700, 0.59, 0.540, 0.020),
    (-0.500, 0.650, 0.572, 0.024),
    (-0.265, 0.665, 0.594, 0.024),
    (-0.035, 0.610, 0.604, 0.022),
    ( 0.145, 0.455, 0.592, 0.018),
    ( 0.275, 0.230, 0.568, 0.012),
    ( 0.335, 0.060, 0.545, 0.008),  # tucked near pillow, still touching visually
]
verts = []
for y, hw, cz, drop in rows:
    verts.extend([
        (-hw, y, cz - drop),
        (-hw*0.72, y, cz - drop*0.35),
        (-hw*0.34, y, cz + 0.050),
        (0.0, y, cz + 0.085),
        (hw*0.34, y, cz + 0.050),
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

# Soft front lip reads as subtle blanket thickness, not a floating piece.
front_lip = [
    # Very subtle underside at the front: enough to read as cloth/leaf thickness,
    # but it follows the mattress edge instead of hovering over it.
    (-0.32, -0.825, 0.508), (0.32, -0.825, 0.508),
    (0.10, -0.955, 0.486), (-0.10, -0.955, 0.486)
]
mesh_obj('rounded_leaf_front_blanket_lip', front_lip, [(0,1,2,3)], M['leaf_shadow'])

# Tiny leaf-colored cover patches to remove accidental cream/white specks where the
# mattress peeks through the blanket. These are deliberately flat and low-poly: they
# behave like painted parts of the leaf, not new decorative details.
front_gap_patch = [
    # Slightly larger and raised above the cream mattress so the small white triangle
    # at the front-left edge reads as part of the leaf blanket.
    (-0.520, -0.900, 0.545),
    (-0.155, -0.925, 0.545),
    (-0.235, -0.720, 0.575),
    (-0.485, -0.745, 0.565),
]
mesh_obj('leaf_color_patch_front_left_white_speck', front_gap_patch, [(0, 1, 2, 3)], M['leaf'])
rear_gap_patch = [
    (-0.105, 0.205, 0.588),
    (0.065, 0.205, 0.588),
    (-0.015, 0.315, 0.560),
]
mesh_obj('leaf_color_patch_rear_white_speck', rear_gap_patch, [(0, 1, 2)], M['leaf'])
# Side thickness removed to avoid a dark stripe; the arched mesh and front lip provide clean soft volume.


# One very subtle integrated central vein only; no side veins yet.
central = cube('single_integrated_soft_leaf_midrib', (0, -0.22, 0.632), (0.009, 0.94, 0.003), M['leaf_vein'], 0.002)

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

# Single PERSPECTIVE render only for composition approval.
views = {
    'PERSPECTIVE': ((2.15, -2.55, 1.55), 1.98),
}
render_paths = []
from PIL import Image
bg_rgb = tuple(int(CHROMA.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
for name, (loc, scale) in views.items():
    cam.location = loc
    cam.data.ortho_scale = scale
    look_at(cam, (0, -0.08, 0.50))
    out = OUT_DIR / f'leaf_bed_final_clean_v1_{name.lower()}.png'
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

CONTACT = render_paths[0]

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
    for p in [OUT_BLEND, OUT_GLB, *render_paths]:
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

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
PROP_DIR = ROOT / "assets" / "props" / "cozy_fishing_rods"
PREVIEW_DIR = PROP_DIR / "previews"
BLEND_PATH = PROP_DIR / "wizard_rod.blend"
GLB_PATH = PROP_DIR / "wizard_rod.glb"
PREVIEW_PATH = PREVIEW_DIR / "wizard_rod.png"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_mat(name, color, roughness=0.84, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def materials():
    return {
        "blue": make_mat("wizard_deep_blue_handle", (0.17, 0.22, 0.56, 1.0), 0.86),
        "blue_dark": make_mat("wizard_midnight_blue", (0.08, 0.11, 0.32, 1.0), 0.88),
        "violet": make_mat("wizard_clean_violet_body", (0.45, 0.29, 0.78, 1.0), 0.84),
        "violet_tip": make_mat("wizard_soft_lavender_tip", (0.55, 0.41, 0.88, 1.0), 0.86),
        "gold": make_mat("wizard_soft_gold_trim", (0.94, 0.68, 0.26, 1.0), 0.74),
        "gold_light": make_mat("wizard_light_gold_highlight", (1.0, 0.82, 0.42, 1.0), 0.70),
        "cream": make_mat("wizard_warm_cream", (0.94, 0.82, 0.62, 1.0), 0.88),
        "gem": make_mat("wizard_round_violet_gem", (0.66, 0.39, 0.94, 1.0), 0.64),
        "line": make_mat("wizard_clean_fishing_line", (0.91, 0.86, 0.73, 1.0), 0.70),
        "floor": make_mat("preview_soft_green_floor", (0.35, 0.72, 0.21, 1.0), 0.9),
    }


def shade(obj, smooth=False):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if smooth:
        bpy.ops.object.shade_smooth()
    else:
        bpy.ops.object.shade_flat()
    obj.select_set(False)


def cylinder_between(name, start, end, radius, mat, vertices=12, smooth=True):
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=direction.length,
        location=start_v + direction * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    shade(obj, smooth)
    return obj


def cone_between(name, start, end, radius_start, radius_end, mat, vertices=12, smooth=True):
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius_start,
        radius2=radius_end,
        depth=direction.length,
        location=start_v + direction * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    shade(obj, smooth)
    return obj


def add_cylinder(name, location, radius, depth, mat, vertices=12, rotation=(0, 0, 0), smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.data.materials.append(mat)
    shade(obj, smooth)
    return obj


def add_sphere(name, location, scale, mat, segments=12, rings=6, rotation=(0, 0, 0), smooth=False):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=1.0,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    shade(obj, smooth)
    return obj


def add_torus(name, location, major_radius, minor_radius, mat, rotation=(0, 0, 0), major_segments=20, minor_segments=5):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=major_segments,
        minor_segments=minor_segments,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.data.materials.append(mat)
    shade(obj, False)
    return obj


def add_cube(name, location, dimensions, mat, rotation=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}Mesh"
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        bevel_mod = obj.modifiers.new(f"{name}_soft_bevel", "BEVEL")
        bevel_mod.width = bevel
        bevel_mod.segments = 1
        bevel_mod.affect = "EDGES"
        obj.modifiers.new(f"{name}_weighted_normals", "WEIGHTED_NORMAL")
    shade(obj, False)
    return obj


def add_curve(name, points, mat, bevel_depth=0.0032, resolution=2):
    curve = bpy.data.curves.new(f"{name}Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coords in zip(spline.points, points):
        point.co = (coords[0], coords[1], coords[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_crescent(name, center, outer_radius, inner_radius, mat, thickness=0.035, inner_shift=0.060, segments=18):
    cx, cy, cz = center
    outline = []
    for i in range(segments + 1):
        angle = math.radians(70 + (220 * i / segments))
        outline.append((math.cos(angle) * outer_radius, math.sin(angle) * outer_radius))
    for i in range(segments, -1, -1):
        angle = math.radians(70 + (220 * i / segments))
        outline.append((inner_shift + math.cos(angle) * inner_radius, math.sin(angle) * inner_radius))

    front = [(cx + x, cy - thickness * 0.5, cz + z) for x, z in outline]
    back = [(cx + x, cy + thickness * 0.5, cz + z) for x, z in outline]
    vertices = front + back
    count = len(outline)
    faces = [tuple(range(count)), tuple(range(count, count * 2))[::-1]]
    for i in range(count):
        nxt = (i + 1) % count
        faces.append((i, nxt, count + nxt, count + i))

    mesh = bpy.data.meshes.new(f"{name}Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    shade(obj, False)
    return obj


def make_star(name, loc, mat, radius=0.070, inner=0.034, thickness=0.018):
    cx, cy, cz = loc
    outline = []
    for i in range(10):
        angle = math.tau * i / 10 + math.pi / 2
        r = radius if i % 2 == 0 else inner
        outline.append((math.cos(angle) * r, math.sin(angle) * r))
    front = [(cx + x, cy - thickness * 0.5, cz + z) for x, z in outline]
    back = [(cx + x, cy + thickness * 0.5, cz + z) for x, z in outline]
    vertices = front + back
    count = len(outline)
    faces = [tuple(range(count)), tuple(range(count, count * 2))[::-1]]
    for i in range(count):
        nxt = (i + 1) % count
        faces.append((i, nxt, count + nxt, count + i))
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    shade(obj, False)
    return obj


def add_rod_body(mats):
    cone_between(
        "wizard_rod_midnight_flared_handle",
        (-1.45, -0.02, -0.025),
        (-1.03, 0.00, 0.000),
        0.108,
        0.058,
        mats["blue_dark"],
        12,
        True,
    )
    cone_between(
        "wizard_rod_clean_violet_body",
        (-1.03, 0.00, 0.000),
        (0.60, 0.034, 0.055),
        0.052,
        0.029,
        mats["violet"],
        14,
        True,
    )
    cone_between(
        "wizard_rod_soft_lavender_tip",
        (0.60, 0.034, 0.055),
        (1.38, 0.052, 0.077),
        0.029,
        0.014,
        mats["violet_tip"],
        12,
        True,
    )
    for index, x in enumerate([-0.96, -0.64, -0.16, 0.42, 0.94, 1.22]):
        cylinder_between(
            f"wizard_rod_thin_gold_wrap_{index + 1}",
            (x, -0.003, 0.008 + (x + 0.5) * 0.016),
            (x + 0.040, -0.002, 0.009 + (x + 0.5) * 0.016),
            0.058 if x < 0.65 else 0.039,
            mats["gold"],
            14,
            False,
        )
    add_sphere("wizard_rod_tiny_top_star_bead", (-0.52, -0.006, 0.094), (0.021, 0.016, 0.021), mats["gold_light"], 8, 4)
    make_star("wizard_rod_small_gold_body_star", (-0.49, -0.024, 0.117), mats["gold"], 0.047, 0.023, 0.012)


def add_crescent_base(mats):
    add_cylinder(
        "wizard_rod_midnight_moon_back_disk",
        (-1.46, -0.014, 0.020),
        0.105,
        0.030,
        mats["blue"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    make_crescent("wizard_rod_elegant_gold_crescent_base", (-1.48, -0.040, 0.020), 0.165, 0.128, mats["gold"], 0.040, 0.065, 20)
    add_cylinder(
        "wizard_rod_gold_rear_collar",
        (-1.22, -0.018, -0.010),
        0.100,
        0.050,
        mats["gold"],
        14,
        rotation=(0, math.radians(85), 0),
        smooth=False,
    )


def add_reel(mats):
    center = (-0.30, -0.150, -0.112)
    cylinder_between("wizard_rod_reel_gold_top_mount", (-0.36, -0.020, -0.025), (-0.32, -0.127, -0.092), 0.020, mats["gold"], 8, True)
    cylinder_between("wizard_rod_reel_blue_lower_mount", (-0.22, -0.018, -0.018), (-0.28, -0.127, -0.123), 0.017, mats["blue"], 8, True)
    add_cylinder(
        "wizard_rod_reel_outer_midnight_shell",
        center,
        0.145,
        0.058,
        mats["blue"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "wizard_rod_reel_gold_ring",
        (center[0], center[1] - 0.020, center[2]),
        0.112,
        0.030,
        mats["gold"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "wizard_rod_reel_violet_gem_button",
        (center[0], center[1] - 0.042, center[2]),
        0.066,
        0.026,
        mats["gem"],
        10,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    make_crescent("wizard_rod_tiny_reel_crescent_mark", (center[0] + 0.070, center[1] - 0.060, center[2] + 0.028), 0.040, 0.030, mats["gold_light"], 0.010, 0.014, 10)
    add_sphere("wizard_rod_reel_tiny_gold_knob", (-0.100, -0.185, -0.182), (0.030, 0.030, 0.030), mats["gold"], 8, 4)


def add_guides_and_line(mats):
    guide_specs = [
        (-0.02, -0.050, -0.074, 0.038),
        (0.54, -0.052, -0.062, 0.034),
        (1.04, -0.050, -0.046, 0.030),
    ]
    for index, (x, y, z, radius) in enumerate(guide_specs):
        add_torus(
            f"wizard_rod_small_gold_line_guide_{index + 1}",
            (x, y, z),
            radius,
            0.0055,
            mats["gold"],
            rotation=(math.radians(90), 0, 0),
            major_segments=18,
            minor_segments=4,
        )
        cylinder_between(
            f"wizard_rod_tidy_guide_mount_{index + 1}",
            (x - 0.012, -0.014, z + 0.053),
            (x, y + 0.010, z + radius * 0.55),
            0.0065,
            mats["gold"],
            6,
            True,
        )
    add_curve(
        "wizard_rod_clean_sagging_line",
        [
            (-0.02, -0.054, -0.074),
            (0.18, -0.062, -0.094),
            (0.36, -0.063, -0.100),
            (0.54, -0.055, -0.062),
            (0.72, -0.057, -0.078),
            (0.90, -0.055, -0.060),
            (1.04, -0.052, -0.046),
        ],
        mats["line"],
        0.0032,
    )
    add_curve(
        "wizard_rod_tip_drop_line",
        [
            (1.38, 0.044, 0.076),
            (1.385, 0.038, -0.120),
            (1.385, 0.034, -0.340),
        ],
        mats["line"],
        0.0032,
    )


def add_magic_charm(mats):
    top = (1.385, 0.026, -0.325)
    center = (1.385, 0.020, -0.405)
    add_sphere("wizard_rod_charm_gold_top_bead", top, (0.018, 0.014, 0.018), mats["gold_light"], 8, 4)
    make_star("wizard_rod_dangling_gold_star_charm", center, mats["gold"], 0.070, 0.034, 0.016)
    make_crescent("wizard_rod_tiny_moon_charm_accent", (1.455, 0.018, -0.405), 0.039, 0.029, mats["gold_light"], 0.012, 0.014, 10)


def add_preview_floor(mats):
    add_cube("optional_green_preview_floor", (0, 0, -0.56), (4.65, 2.20, 0.030), mats["floor"])


def setup_camera_lights():
    bpy.ops.object.light_add(type="SUN", location=(0.0, 2.0, 4.0))
    sun = bpy.context.object
    sun.name = "wizard_preview_soft_sun"
    sun.data.energy = 1.65
    sun.rotation_euler = (math.radians(45), 0.0, math.radians(34))

    bpy.ops.object.light_add(type="AREA", location=(-3.0, -3.2, 3.2))
    area = bpy.context.object
    area.name = "wizard_preview_large_fill"
    area.data.energy = 430
    area.data.size = 4.8

    bpy.ops.object.camera_add(location=(2.55, -3.95, 1.38))
    camera = bpy.context.object
    camera.name = "wizard_preview_camera"
    bpy.context.scene.camera = camera
    direction = Vector((-0.02, -0.02, -0.155)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.82


def configure_scene():
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.world.color = (0.60, 0.78, 0.62)
    try:
        bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
    if bpy.context.scene.render.engine == "BLENDER_WORKBENCH":
        bpy.context.scene.display.shading.color_type = "MATERIAL"
    if hasattr(bpy.context.scene, "eevee"):
        bpy.context.scene.eevee.taa_render_samples = 96


def build_wizard_rod():
    mats = materials()
    add_rod_body(mats)
    add_crescent_base(mats)
    add_reel(mats)
    add_guides_and_line(mats)
    add_magic_charm(mats)
    return mats


def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_apply=True, export_yup=True)
    print(f"Created {path}")


def main():
    PROP_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    clear_scene()
    mats = build_wizard_rod()
    configure_scene()
    export_glb(GLB_PATH)
    add_preview_floor(mats)
    setup_camera_lights()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.context.scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    print(f"Created {PREVIEW_PATH}")
    print(f"Created {BLEND_PATH}")


if __name__ == "__main__":
    main()

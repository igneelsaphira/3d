import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector


ROOT = Path(__file__).resolve().parents[1]
PROP_DIR = ROOT / "assets" / "props" / "cozy_fishing_rods"
PREVIEW_DIR = PROP_DIR / "previews"
BLEND_PATH = PROP_DIR / "villager_rod.blend"
GLB_PATH = PROP_DIR / "villager_rod.glb"
PREVIEW_PATH = PREVIEW_DIR / "villager_rod.png"


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
        "wood": make_mat("villager_warm_branch_wood", (0.56, 0.34, 0.16, 1.0), 0.84),
        "wood_light": make_mat("villager_cut_wood_light", (0.78, 0.52, 0.28, 1.0), 0.78),
        "wood_dark": make_mat("villager_dark_bark_shadow", (0.31, 0.18, 0.08, 1.0), 0.9),
        "cream": make_mat("villager_soft_rope_wrap", (0.88, 0.78, 0.58, 1.0), 0.88),
        "cream_shadow": make_mat("villager_rope_shadow", (0.68, 0.58, 0.42, 1.0), 0.9),
        "leaf": make_mat("villager_soft_leaf_green", (0.45, 0.65, 0.22, 1.0), 0.88),
        "leaf_light": make_mat("villager_leaf_light", (0.60, 0.78, 0.32, 1.0), 0.86),
        "leaf_dark": make_mat("villager_deep_leaf_vein", (0.24, 0.43, 0.12, 1.0), 0.9),
        "line": make_mat("villager_clean_fishing_line", (0.88, 0.82, 0.66, 1.0), 0.72),
        "lantern_frame": make_mat("villager_lantern_dark_frame", (0.16, 0.17, 0.13, 1.0), 0.84),
        "lantern_cap": make_mat("villager_lantern_warm_roof", (0.28, 0.27, 0.18, 1.0), 0.82),
        "lantern_glow": make_mat(
            "villager_lantern_warm_glow",
            (1.0, 0.75, 0.28, 1.0),
            0.55,
            emission=(1.0, 0.54, 0.12, 1.0),
            strength=1.15,
        ),
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


def add_cone(name, location, radius1, radius2, depth, mat, vertices=12, rotation=(0, 0, 0), smooth=True):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
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


def make_leaf(name, loc, mats, scale=1.0, rotation=(0, 0, 0), mat_key="leaf"):
    vertices = [
        (0.000, 0.092, 0.000),
        (-0.060, 0.034, 0.000),
        (-0.047, -0.050, 0.000),
        (0.000, -0.104, 0.000),
        (0.055, -0.045, 0.000),
        (0.063, 0.036, 0.000),
    ]
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    mesh.from_pydata([(x * scale, y * scale, z * scale) for x, y, z in vertices], [], [(0, 1, 2, 3, 4, 5)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rotation
    obj.data.materials.append(mats[mat_key])
    shade(obj, False)

    rot = Euler(rotation, "XYZ").to_matrix()
    origin = Vector(loc)
    cylinder_between(
        f"{name}_center_vein",
        origin + rot @ Vector((0.000, -0.086 * scale, 0.002 * scale)),
        origin + rot @ Vector((0.000, 0.078 * scale, 0.002 * scale)),
        0.0045 * scale,
        mats["leaf_dark"],
        6,
        True,
    )
    return obj


def add_rod_body(mats):
    # Natural branch silhouette: chunkier carved butt, warmer middle, thin twig tip.
    cone_between(
        "villager_rod_faceted_log_butt",
        (-1.52, -0.020, -0.030),
        (-1.12, -0.004, -0.002),
        0.128,
        0.072,
        mats["wood_dark"],
        9,
        True,
    )
    cone_between(
        "villager_rod_warm_branch_body",
        (-1.12, -0.004, -0.002),
        (0.56, 0.034, 0.054),
        0.060,
        0.032,
        mats["wood"],
        12,
        True,
    )
    cone_between(
        "villager_rod_slim_twig_tip",
        (0.56, 0.034, 0.054),
        (1.38, 0.052, 0.077),
        0.032,
        0.015,
        mats["wood_light"],
        10,
        True,
    )
    # Subtle bark facets/grooves.
    for index, (x, zoff, length) in enumerate([(-1.42, 0.020, 0.16), (-1.28, -0.018, 0.12), (-0.58, 0.028, 0.20), (0.12, -0.020, 0.22)]):
        cylinder_between(
            f"villager_rod_subtle_bark_groove_{index + 1}",
            (x, -0.052, zoff),
            (x + length, -0.054, zoff + 0.012),
            0.0045,
            mats["wood_dark"],
            5,
            True,
        )
    for index, x in enumerate([-0.98, -0.66, -0.12, 0.45, 0.98, 1.24]):
        cylinder_between(
            f"villager_rod_tidy_rope_wrap_{index + 1}",
            (x, -0.003, 0.008 + (x + 0.5) * 0.015),
            (x + 0.045, -0.002, 0.009 + (x + 0.5) * 0.015),
            0.064 if x < 0.65 else 0.043,
            mats["cream"],
            12,
            False,
        )
        cylinder_between(
            f"villager_rod_rope_shadow_edge_{index + 1}",
            (x + 0.046, -0.004, 0.008 + (x + 0.5) * 0.015),
            (x + 0.057, -0.004, 0.009 + (x + 0.5) * 0.015),
            0.064 if x < 0.65 else 0.043,
            mats["cream_shadow"],
            12,
            False,
        )


def add_leaf_sprout(mats):
    # Anchored sprout instead of floating leaves.
    base = Vector((-0.60, -0.006, 0.082))
    cylinder_between("villager_rod_attached_leaf_stem", base, base + Vector((0.020, 0.012, 0.135)), 0.011, mats["leaf_dark"], 7, True)
    make_leaf(
        "villager_rod_integrated_left_leaf",
        (-0.665, 0.010, 0.222),
        mats,
        0.56,
        rotation=(math.radians(62), math.radians(-10), math.radians(-34)),
        mat_key="leaf",
    )
    make_leaf(
        "villager_rod_integrated_right_leaf",
        (-0.535, 0.014, 0.225),
        mats,
        0.60,
        rotation=(math.radians(62), math.radians(10), math.radians(32)),
        mat_key="leaf_light",
    )


def add_reel(mats):
    center = (-0.30, -0.150, -0.112)
    cylinder_between("villager_rod_reel_top_branch_mount", (-0.36, -0.020, -0.025), (-0.32, -0.127, -0.092), 0.021, mats["wood_dark"], 8, True)
    cylinder_between("villager_rod_reel_lower_branch_mount", (-0.22, -0.018, -0.018), (-0.28, -0.127, -0.123), 0.018, mats["cream"], 8, True)
    add_cylinder(
        "villager_rod_reel_outer_wood_shell",
        center,
        0.145,
        0.060,
        mats["wood"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "villager_rod_reel_cut_wood_ring",
        (center[0], center[1] - 0.020, center[2]),
        0.112,
        0.030,
        mats["wood_light"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "villager_rod_reel_leaf_green_button",
        (center[0], center[1] - 0.043, center[2]),
        0.066,
        0.026,
        mats["leaf"],
        10,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    make_leaf("villager_rod_reel_leaf_emblem", (center[0], center[1] - 0.060, center[2] + 0.002), mats, 0.40, rotation=(math.radians(90), 0, 0), mat_key="leaf_light")
    add_sphere("villager_rod_reel_tiny_wood_knob", (-0.100, -0.185, -0.182), (0.031, 0.031, 0.031), mats["wood_light"], 8, 4)


def add_guides_and_line(mats):
    guide_specs = [
        (-0.02, -0.050, -0.074, 0.038),
        (0.54, -0.052, -0.062, 0.034),
        (1.04, -0.050, -0.046, 0.030),
    ]
    for index, (x, y, z, radius) in enumerate(guide_specs):
        add_torus(
            f"villager_rod_small_rope_line_guide_{index + 1}",
            (x, y, z),
            radius,
            0.0055,
            mats["cream"],
            rotation=(math.radians(90), 0, 0),
            major_segments=18,
            minor_segments=4,
        )
        cylinder_between(
            f"villager_rod_tidy_guide_mount_{index + 1}",
            (x - 0.012, -0.014, z + 0.053),
            (x, y + 0.010, z + radius * 0.55),
            0.0065,
            mats["cream"],
            6,
            True,
        )
    add_curve(
        "villager_rod_clean_sagging_line",
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
        "villager_rod_tip_drop_line",
        [
            (1.38, 0.044, 0.076),
            (1.385, 0.038, -0.115),
            (1.385, 0.034, -0.355),
        ],
        mats["line"],
        0.0032,
    )


def add_lantern_charm(mats):
    center = Vector((1.385, 0.020, -0.430))
    add_sphere("villager_rod_lantern_top_bead", (1.385, 0.026, -0.340), (0.017, 0.014, 0.017), mats["cream"], 8, 4)
    add_curve(
        "villager_rod_lantern_small_handle",
        [
            (center.x - 0.048, center.y, center.z + 0.082),
            (center.x, center.y - 0.010, center.z + 0.125),
            (center.x + 0.048, center.y, center.z + 0.082),
        ],
        mats["lantern_frame"],
        0.0045,
        3,
    )
    add_cube("villager_rod_lantern_glowing_window", center, (0.104, 0.045, 0.130), mats["lantern_glow"], bevel=0.004)
    add_cube("villager_rod_lantern_left_frame", (center.x - 0.063, center.y, center.z), (0.020, 0.056, 0.145), mats["lantern_frame"], bevel=0.003)
    add_cube("villager_rod_lantern_right_frame", (center.x + 0.063, center.y, center.z), (0.020, 0.056, 0.145), mats["lantern_frame"], bevel=0.003)
    add_cube("villager_rod_lantern_bottom_frame", (center.x, center.y, center.z - 0.078), (0.145, 0.060, 0.026), mats["lantern_frame"], bevel=0.003)
    add_cone("villager_rod_lantern_roof", (center.x, center.y, center.z + 0.088), 0.088, 0.040, 0.050, mats["lantern_cap"], 4, rotation=(0, 0, math.radians(45)), smooth=False)
    add_cube("villager_rod_lantern_top_lip", (center.x, center.y, center.z + 0.062), (0.152, 0.064, 0.020), mats["lantern_frame"], bevel=0.003)


def add_preview_floor(mats):
    add_cube("optional_green_preview_floor", (0, 0, -0.585), (4.65, 2.25, 0.030), mats["floor"])


def setup_camera_lights():
    bpy.ops.object.light_add(type="SUN", location=(0.0, 2.0, 4.0))
    sun = bpy.context.object
    sun.name = "villager_preview_soft_sun"
    sun.data.energy = 1.65
    sun.rotation_euler = (math.radians(45), 0.0, math.radians(34))

    bpy.ops.object.light_add(type="AREA", location=(-3.0, -3.2, 3.2))
    area = bpy.context.object
    area.name = "villager_preview_large_fill"
    area.data.energy = 430
    area.data.size = 4.8

    bpy.ops.object.camera_add(location=(2.55, -3.95, 1.38))
    camera = bpy.context.object
    camera.name = "villager_preview_camera"
    bpy.context.scene.camera = camera
    direction = Vector((-0.02, -0.02, -0.170)) - camera.location
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


def build_villager_rod():
    mats = materials()
    add_rod_body(mats)
    add_leaf_sprout(mats)
    add_reel(mats)
    add_guides_and_line(mats)
    add_lantern_charm(mats)
    return mats


def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_apply=True, export_yup=True)
    print(f"Created {path}")


def main():
    PROP_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    clear_scene()
    mats = build_villager_rod()
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

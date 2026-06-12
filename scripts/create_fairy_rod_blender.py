import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
PROP_DIR = ROOT / "assets" / "props" / "cozy_fishing_rods"
PREVIEW_DIR = PROP_DIR / "previews"
BLEND_PATH = PROP_DIR / "fairy_rod.blend"
GLB_PATH = PROP_DIR / "fairy_rod.glb"
PREVIEW_PATH = PREVIEW_DIR / "fairy_rod.png"


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
        "pink": make_mat("fairy_pastel_rose_body", (0.95, 0.55, 0.64, 1.0), 0.86),
        "pink_tip": make_mat("fairy_soft_rose_tip", (0.98, 0.68, 0.75, 1.0), 0.86),
        "pink_shadow": make_mat("fairy_muted_rose_handle", (0.76, 0.36, 0.46, 1.0), 0.88),
        "gold": make_mat("fairy_soft_brushed_gold", (0.93, 0.70, 0.32, 1.0), 0.74),
        "gold_light": make_mat("fairy_light_gold_highlight", (1.0, 0.82, 0.45, 1.0), 0.72),
        "cream": make_mat("fairy_warm_cream", (0.96, 0.86, 0.66, 1.0), 0.88),
        "wing": make_mat("fairy_soft_wing_ivory", (0.98, 0.91, 0.76, 1.0), 0.86),
        "wing_shadow": make_mat("fairy_wing_warm_shadow", (0.86, 0.77, 0.62, 1.0), 0.9),
        "gem": make_mat("fairy_rose_gem", (1.0, 0.43, 0.66, 1.0), 0.62),
        "line": make_mat("fairy_clean_fishing_line", (0.94, 0.88, 0.72, 1.0), 0.70),
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


def add_curve(name, points, mat, bevel_depth=0.004, resolution=2):
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


def add_rod_body(mats):
    # Slim segmented silhouette: flared handle, soft pastel body, fine tip.
    cone_between(
        "fairy_rod_flared_blush_handle",
        (-1.48, -0.02, -0.035),
        (-1.02, 0.00, 0.000),
        0.105,
        0.058,
        mats["pink_shadow"],
        12,
        True,
    )
    cone_between(
        "fairy_rod_pastel_main_body",
        (-1.02, 0.00, 0.000),
        (0.58, 0.035, 0.055),
        0.050,
        0.028,
        mats["pink"],
        14,
        True,
    )
    cone_between(
        "fairy_rod_delicate_tip",
        (0.58, 0.035, 0.055),
        (1.36, 0.052, 0.078),
        0.028,
        0.014,
        mats["pink_tip"],
        12,
        True,
    )
    cylinder_between("fairy_rod_cream_handle_collar", (-1.10, -0.003, -0.002), (-1.03, -0.001, 0.000), 0.065, mats["cream"], 14, False)
    for index, x in enumerate([-0.88, -0.48, 0.13, 0.73, 1.18]):
        cylinder_between(
            f"fairy_rod_thin_gold_wrap_{index + 1}",
            (x, -0.003, 0.010 + (x + 0.5) * 0.016),
            (x + 0.040, -0.002, 0.011 + (x + 0.5) * 0.016),
            0.055 if x < 0.65 else 0.038,
            mats["gold"],
            14,
            False,
        )
    add_sphere("fairy_rod_tiny_gold_crown_gem", (-0.56, -0.006, 0.092), (0.025, 0.018, 0.025), mats["gold_light"], 8, 4, smooth=False)


def add_handle_wings(mats):
    # Soft fan at the back, like a small cream fairy feather tail.
    for side in [-1, 1]:
        for i, (length, rise) in enumerate([(0.145, 0.010), (0.170, 0.045), (0.145, 0.080)]):
            add_sphere(
                f"fairy_rod_tail_soft_wing_{side}_{i + 1}",
                (-1.55, side * (0.030 + i * 0.028), 0.020 + rise),
                (length, 0.026, 0.044),
                mats["wing"] if i != 0 else mats["wing_shadow"],
                10,
                5,
                rotation=(0.0, math.radians(4), side * math.radians(10 + i * 8)),
                smooth=False,
            )
    cylinder_between("fairy_rod_gold_tail_collar", (-1.27, -0.020, -0.018), (-1.20, -0.016, -0.010), 0.102, mats["gold"], 14, False)


def add_reel(mats):
    # Reel sits closer to the body, with a small mount so it feels attached.
    reel_center = (-0.30, -0.155, -0.115)
    cylinder_between("fairy_rod_reel_top_mount", (-0.36, -0.020, -0.025), (-0.32, -0.130, -0.095), 0.020, mats["gold"], 8, True)
    cylinder_between("fairy_rod_reel_lower_mount", (-0.22, -0.018, -0.018), (-0.28, -0.130, -0.125), 0.017, mats["cream"], 8, True)
    add_cylinder(
        "fairy_rod_reel_outer_cream_shell",
        reel_center,
        0.142,
        0.058,
        mats["cream"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "fairy_rod_reel_gold_inner_ring",
        (reel_center[0], reel_center[1] - 0.020, reel_center[2]),
        0.105,
        0.030,
        mats["gold"],
        14,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_cylinder(
        "fairy_rod_reel_rose_gem_button",
        (reel_center[0], reel_center[1] - 0.040, reel_center[2]),
        0.061,
        0.026,
        mats["gem"],
        10,
        rotation=(math.radians(90), 0, 0),
        smooth=False,
    )
    add_sphere("fairy_rod_reel_tiny_gold_knob", (-0.105, -0.185, -0.185), (0.030, 0.030, 0.030), mats["gold"], 8, 4)

    for side in [-1, 1]:
        for i, (dx, dz, sx, sz) in enumerate([(0.112, 0.032, 0.074, 0.032), (0.154, 0.000, 0.086, 0.036), (0.118, -0.042, 0.066, 0.030)]):
            add_sphere(
                f"fairy_rod_reel_soft_wing_{side}_{i + 1}",
                (reel_center[0] + side * dx, reel_center[1] - 0.020, reel_center[2] + dz),
                (sx, 0.018, sz),
                mats["wing"] if i != 2 else mats["wing_shadow"],
                10,
                5,
                rotation=(math.radians(2), 0, side * math.radians(16 - i * 9)),
                smooth=False,
            )


def add_guides_and_line(mats):
    guide_specs = [
        (-0.02, -0.050, -0.074, 0.038),
        (0.54, -0.052, -0.062, 0.034),
        (1.04, -0.050, -0.046, 0.030),
    ]
    for index, (x, y, z, radius) in enumerate(guide_specs):
        add_torus(
            f"fairy_rod_small_gold_line_guide_{index + 1}",
            (x, y, z),
            radius,
            0.0055,
            mats["gold"],
            rotation=(math.radians(90), 0, 0),
            major_segments=18,
            minor_segments=4,
        )
        cylinder_between(
            f"fairy_rod_tidy_guide_mount_{index + 1}",
            (x - 0.012, -0.014, z + 0.053),
            (x, y + 0.010, z + radius * 0.55),
            0.0065,
            mats["gold"],
            6,
            True,
        )

    # Clean line: slight sag through guides and one straight drop from the tip.
    add_curve(
        "fairy_rod_clean_sagging_line",
        [
            (-0.02, -0.054, -0.074),
            (0.15, -0.060, -0.090),
            (0.32, -0.062, -0.103),
            (0.54, -0.055, -0.062),
            (0.70, -0.057, -0.075),
            (0.86, -0.056, -0.062),
            (1.04, -0.052, -0.046),
        ],
        mats["line"],
        0.0032,
    )
    add_curve(
        "fairy_rod_tip_drop_line",
        [
            (1.36, 0.040, 0.074),
            (1.365, 0.036, -0.108),
            (1.365, 0.034, -0.335),
        ],
        mats["line"],
        0.0032,
    )


def add_flower_charm(mats):
    center = Vector((1.365, 0.020, -0.392))
    add_sphere("fairy_rod_flower_top_bead", (1.365, 0.026, -0.322), (0.018, 0.014, 0.018), mats["gold_light"], 8, 4)
    for i in range(5):
        angle = math.tau * i / 5 + math.radians(18)
        petal_center = center + Vector((math.cos(angle) * 0.056, -0.004, math.sin(angle) * 0.056))
        add_sphere(
            f"fairy_rod_readable_flower_petal_{i + 1}",
            petal_center,
            (0.038, 0.015, 0.053),
            mats["pink_tip"] if i % 2 else mats["pink"],
            10,
            5,
            rotation=(0, math.pi / 2 - angle, 0),
            smooth=False,
        )
    add_sphere("fairy_rod_readable_flower_center", center, (0.033, 0.017, 0.033), mats["gold"], 10, 5)


def add_preview_floor():
    add_cube("optional_green_preview_floor", (0, 0, -0.56), (4.60, 2.20, 0.030), materials()["floor"])


def setup_camera_lights():
    bpy.ops.object.light_add(type="SUN", location=(0.0, 2.0, 4.0))
    sun = bpy.context.object
    sun.name = "fairy_preview_soft_sun"
    sun.data.energy = 1.65
    sun.rotation_euler = (math.radians(45), 0.0, math.radians(34))

    bpy.ops.object.light_add(type="AREA", location=(-3.0, -3.2, 3.2))
    area = bpy.context.object
    area.name = "fairy_preview_large_fill"
    area.data.energy = 430
    area.data.size = 4.8

    bpy.ops.object.camera_add(location=(2.55, -3.95, 1.38))
    camera = bpy.context.object
    camera.name = "fairy_preview_camera"
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


def build_fairy_rod():
    mats = materials()
    add_rod_body(mats)
    add_handle_wings(mats)
    add_reel(mats)
    add_guides_and_line(mats)
    add_flower_charm(mats)


def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_apply=True, export_yup=True)
    print(f"Created {path}")


def main():
    PROP_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    clear_scene()
    build_fairy_rod()
    add_preview_floor()
    setup_camera_lights()
    configure_scene()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.context.scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    print(f"Created {PREVIEW_PATH}")
    export_glb(GLB_PATH)
    print(f"Created {BLEND_PATH}")


if __name__ == "__main__":
    main()

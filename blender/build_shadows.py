"""
Procedural Blender scene generator for looping dappled foliage shadow videos
(inspired by prototype/shadows.mp4).

Usage:
  blender --background --python blender/build_shadows.py -- --preview
  blender --background --python blender/build_shadows.py -- --render
"""

import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(SCRIPT_DIR, "shadows.blend")
PREVIEW_DIR = os.path.join(SCRIPT_DIR, "previews")
FRAMES_DIR = os.path.join(SCRIPT_DIR, "frames")

TOTAL_FRAMES = 175  # 7.0s at 25 fps (matches prototype/shadows.mp4)
FPS = 25
RES_X = 1280
RES_Y = 720


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Render 3 preview frames")
    parser.add_argument("--render", action="store_true", help="Render full animation sequence")
    parser.add_argument("--samples", type=int, default=32, help="Cycles render samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for foliage layout")
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render(samples: int):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 2
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 0
    scene.cycles.transmission_bounces = 0
    scene.cycles.volume_bounces = 0
    scene.cycles.transparent_max_bounces = 2

    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0


def setup_world():
    world = bpy.data.worlds.new("ShadowWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    bg = nodes.get("Background")
    if bg:
        # Soft cool-grey ambient fill so shadows match the slate tone in shadows.mp4
        bg.inputs["Color"].default_value = (0.28, 0.31, 0.31, 1.0)
        bg.inputs["Strength"].default_value = 0.65


def create_wall():
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    wall = bpy.context.active_object
    wall.name = "Wall"
    wall.scale = (18.0, 10.5, 1.0)

    mat = bpy.data.materials.new("WallMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.88, 0.90, 0.89, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.95
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.05

    # Subtle plaster grain
    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.65

    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.02
    bump.inputs["Distance"].default_value = 0.05

    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    wall.data.materials.append(mat)
    return wall


def create_camera():
    cam_data = bpy.data.cameras.new("OrthoCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 16.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0

    cam_obj = bpy.data.objects.new("OrthoCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = (0.0, 0.0, 12.0)
    cam_obj.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.scene.camera = cam_obj
    return cam_obj


def create_sun():
    light_data = bpy.data.lights.new("SunKey", type="SUN")
    light_data.energy = 3.0
    light_data.color = (0.98, 0.99, 0.97)
    # Soft penumbra so closer leaves are sharp and distant leaves blur smoothly
    light_data.angle = math.radians(4.2)

    light_obj = bpy.data.objects.new("SunKey", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = (0.0, 0.0, 15.0)
    # Slight angle from upper-left
    light_obj.rotation_euler = (math.radians(14.0), math.radians(-16.0), 0.0)
    return light_obj


def add_leaf_to_bmesh(bm: bmesh.types.BMesh, origin: Vector, direction: Vector, length: float, width: float, tilt: float):
    """Build a pointed oval leaf (diamond-elliptical silhouette) in bmesh."""
    forward = direction.normalized()
    up = Vector((0.0, 0.0, 1.0))
    side = forward.cross(up)
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    else:
        side.normalize()

    # Slight 3D tilt so leaves vary in apparent width
    rot_m = Matrix.Rotation(tilt, 3, forward)
    side = rot_m @ side

    pts = [
        origin,
        origin + forward * (length * 0.25) + side * (width * 0.42),
        origin + forward * (length * 0.58) + side * (width * 0.50),
        origin + forward * (length * 0.85) + side * (width * 0.22),
        origin + forward * length,
        origin + forward * (length * 0.85) - side * (width * 0.22),
        origin + forward * (length * 0.58) - side * (width * 0.50),
        origin + forward * (length * 0.25) - side * (width * 0.42),
    ]
    verts = [bm.verts.new(p) for p in pts]
    bm.faces.new(verts)


def add_stem_segment(bm: bmesh.types.BMesh, p0: Vector, p1: Vector, radius: float):
    """Add a thin ribbon stem between p0 and p1."""
    d = p1 - p0
    if d.length < 1e-4:
        return
    side = d.normalized().cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    else:
        side.normalize()
    v0 = bm.verts.new(p0 - side * radius)
    v1 = bm.verts.new(p0 + side * radius)
    v2 = bm.verts.new(p1 + side * radius)
    v3 = bm.verts.new(p1 - side * radius)
    bm.faces.new((v0, v1, v2, v3))


def create_branch(
    name: str,
    location: tuple,
    base_angle: float,
    length: float,
    leaf_scale: float,
    leaf_density: int,
    sub_branches: int,
    rng: random.Random,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
):
    """Create a procedural curved twig with pinnate/clustered leaves."""
    bm = bmesh.new()

    def grow_twig(start: Vector, angle: float, twig_len: float, n_leaves: int, stem_r: float, depth: int):
        steps = max(4, n_leaves)
        prev = start
        cur_angle = angle
        curvature = rng.uniform(-0.14, 0.14)

        for i in range(1, steps + 1):
            t = i / steps
            cur_angle += curvature / steps + rng.uniform(-0.04, 0.04)
            step_len = twig_len / steps
            nxt = prev + Vector((math.cos(cur_angle) * step_len, math.sin(cur_angle) * step_len, rng.uniform(-0.04, 0.04)))
            add_stem_segment(bm, prev, nxt, stem_r * (1.0 - 0.5 * t))

            # Add opposing/alternating leaves along the twig
            for side_sign in (-1, 1):
                if rng.random() < 0.85:
                    l_angle = cur_angle + side_sign * rng.uniform(0.55, 1.05)
                    l_dir = Vector((math.cos(l_angle), math.sin(l_angle), rng.uniform(-0.15, 0.15)))
                    taper = 0.65 + 0.45 * math.sin(t * math.pi)
                    l_len = leaf_scale * taper * rng.uniform(0.8, 1.25)
                    l_wid = l_len * rng.uniform(0.42, 0.58)
                    add_leaf_to_bmesh(bm, nxt, l_dir, l_len, l_wid, rng.uniform(-0.4, 0.4))

            # Terminal leaf
            if i == steps:
                l_dir = Vector((math.cos(cur_angle), math.sin(cur_angle), 0.0))
                add_leaf_to_bmesh(bm, nxt, l_dir, leaf_scale * 0.85, leaf_scale * 0.42, 0.0)

            # Spawn sub-branch
            if depth > 0 and 0.25 < t < 0.8 and rng.random() < 0.45:
                sub_sign = rng.choice((-1, 1))
                sub_angle = cur_angle + sub_sign * rng.uniform(0.45, 0.95)
                grow_twig(
                    nxt,
                    sub_angle,
                    twig_len * rng.uniform(0.45, 0.65),
                    max(3, int(n_leaves * 0.55)),
                    stem_r * 0.7,
                    depth - 1,
                )

            prev = nxt

    grow_twig(Vector((0.0, 0.0, 0.0)), base_angle, length, leaf_density, 0.045 * leaf_scale, sub_branches)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)

    # Invisible to camera rays, still casts shadows onto the wall!
    obj.visible_camera = False
    return obj


def animate_looping_wind(obj: bpy.types.Object, rng: random.Random, amplitude_deg: float):
    """Keyframe a mathematically seamless periodic wind sway over TOTAL_FRAMES."""
    base_rot = Euler(obj.rotation_euler, "XYZ")
    phase1 = rng.uniform(0.0, math.tau)
    phase2 = rng.uniform(0.0, math.tau)
    amp_z = math.radians(amplitude_deg)
    amp_x = math.radians(amplitude_deg * 0.45)
    amp_y = math.radians(amplitude_deg * 0.35)

    # Sample every 5 frames + final seamless wrap at TOTAL_FRAMES + 1
    step = 5
    frames = list(range(1, TOTAL_FRAMES + 1, step))
    if frames[-1] != TOTAL_FRAMES + 1:
        frames.append(TOTAL_FRAMES + 1)

    for f in frames:
        t = (f - 1) / TOTAL_FRAMES  # 0.0 at frame 1, 1.0 at frame TOTAL_FRAMES + 1
        w1 = math.sin(math.tau * t + phase1)
        w2 = 0.35 * math.sin(2.0 * math.tau * t + phase2)
        sway = w1 + w2

        obj.rotation_euler = (
            base_rot.x + amp_x * sway,
            base_rot.y + amp_y * math.cos(math.tau * t + phase1),
            base_rot.z + amp_z * sway,
        )
        obj.keyframe_insert(data_path="rotation_euler", frame=f)


def build_foliage(seed: int):
    rng = random.Random(seed)
    col = bpy.data.collections.new("Foliage")
    bpy.context.scene.collection.children.link(col)

    mat = bpy.data.materials.new("LeafShadowMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.05, 0.06, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0

    # Composition inspired by prototype/shadows.mp4:
    # - Far canopy on upper-left & top-center (soft, blurred shadows)
    # - Mid-depth sweeping branches across upper-middle and lower-left
    # - Near delicate twigs entering from the right edge (sharper silhouettes)
    specs = [
        # (name, (x, y, z), angle_deg, length, leaf_scale, density, sub_branches, wind_amp)
        # Far blurred canopy (left & top)
        ("FarCanopy_1", (-9.5, 4.8, 4.8), -28, 7.5, 1.05, 8, 2, 2.2),
        ("FarCanopy_2", (-8.5, 1.2, 5.2), -10, 6.8, 1.15, 7, 2, 1.8),
        ("FarCanopy_3", (-4.5, 5.8, 4.4), -62, 6.2, 1.0, 7, 2, 2.5),
        ("FarCanopy_4", (-9.0, -2.5, 4.6), 18, 6.5, 1.1, 7, 1, 2.0),
        ("FarCanopy_5", (0.5, 6.0, 5.0), -110, 5.5, 1.0, 6, 1, 2.4),
        # Mid-depth branches (dappled middle-left & top)
        ("MidBranch_1", (-6.2, 4.2, 2.4), -38, 6.0, 0.78, 8, 1, 3.0),
        ("MidBranch_2", (-1.5, 5.0, 2.1), -78, 5.4, 0.72, 7, 1, 3.2),
        ("MidBranch_3", (-7.8, -1.8, 2.6), 24, 5.5, 0.82, 7, 1, 2.6),
        ("MidBranch_4", (3.2, 5.2, 2.3), -125, 4.8, 0.70, 6, 1, 3.4),
        # Near sharper twigs (right edge & bottom-right)
        ("NearTwig_1", (8.6, 1.8, 0.85), 165, 4.4, 0.56, 8, 1, 3.8),
        ("NearTwig_2", (8.8, -1.4, 0.70), 148, 4.8, 0.52, 8, 1, 4.2),
        ("NearTwig_3", (7.4, -4.6, 0.95), 122, 4.2, 0.58, 7, 1, 3.6),
        ("NearTwig_4", (6.8, 4.6, 1.10), -145, 3.8, 0.54, 6, 1, 3.5),
    ]

    for name, loc, ang, length, lscale, dens, subs, amp in specs:
        branch = create_branch(
            name=name,
            location=loc,
            base_angle=math.radians(ang),
            length=length,
            leaf_scale=lscale,
            leaf_density=dens,
            sub_branches=subs,
            rng=rng,
            mat=mat,
            collection=col,
        )
        animate_looping_wind(branch, rng, amplitude_deg=amp)


def render_previews():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    scene = bpy.context.scene
    for frame in (1, 88, 175):
        scene.frame_set(frame)
        out_path = os.path.join(PREVIEW_DIR, f"preview_{frame:03d}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered preview: {out_path}")


def render_animation():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = os.path.join(FRAMES_DIR, "frame_")
    bpy.ops.render.render(animation=True)
    print(f"Rendered animation frames to: {FRAMES_DIR}")


def main():
    args = parse_args()
    clear_scene()
    setup_render(samples=args.samples)
    setup_world()
    create_wall()
    create_camera()
    create_sun()
    build_foliage(seed=args.seed)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved blend file: {BLEND_PATH}")

    if args.preview:
        render_previews()
    elif args.render:
        render_animation()


if __name__ == "__main__":
    main()

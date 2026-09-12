"""
Paterson tank tumbler — internal drive.

    DRUM     a tube lying on its side, OD 270 / ID 250. A bore runs through it
             PERPENDICULAR to its axis and the tank lives in that bore, so one
             turn of the drum is one full inversion of the tank.
    TRACK    the first 34 mm (tyre width + 5) at each open end of the tube has
             square grooves cut into its INNER wall.
    BASE     one piece: a flat 10 mm connector between two uprights, each a
             rectangle with a half-cylinder on top. Four motors sit in the
             uprights and their wheels reach axially INTO the open ends of the
             drum, pressing OUTWARD against the internal grooves.

X = drum axis, Z = up.
"""

import math
import os
import numpy as np
import trimesh
from trimesh.creation import cylinder, box, extrude_polygon
from shapely.geometry import Point, Polygon as SPoly

OUT = "stl"
os.makedirs(OUT, exist_ok=True)
CQ = 192

# ------------------------------------------------------------------ tank
TANK_OD, TANK_LEN = 102.0, 303.0
HOLE_D = TANK_OD + 4.0                     # 106
SLEEVE_T = 6.0

# ------------------------------------------------------------------ drum
DRUM_OD = 270.0
DRUM_ID = 250.0                            # the cut-out cylinder
WALL = (DRUM_OD - DRUM_ID) / 2.0           # 10
DRUM_L = 198.0
WHEEL_OD, WHEEL_W = 63.0, 29.0
TRACK_W = WHEEL_W + 5.0                    # 34 deep band of grooves at each end
N_TEETH, TOOTH_W, TOOTH_D = 78, 5.0, 3.0   # cut OUTWARD from the ID
RIB_T = 5.0
RIB_L = 50.0                               # central only: motors live outboard of this
TAB_W, TAB_T, TAB_H = 34.0, 10.0, 16.0
SLOT_L, SLOT_W = 25.0, 4.0

# ------------------------------------------------------------------ base
AXIS_H = 175.0
MOT_ANGS = (45.0, 135.0, -135.0, -45.0)    # 4 per end, 90 deg apart, from TOP
N_PER_END = len(MOT_ANGS)
R_CONTACT = DRUM_ID / 2.0                  # 125, tyre bears here
R_WHEEL_C = R_CONTACT - WHEEL_OD / 2.0     # 93.5, wheel centre from drum axis
PLATE_T = 14.0
END_GAP = 3.0                              # axial clearance to the drum end face
ARCH_R = R_WHEEL_C + 31.0                  # 124.5 outer radius of the half-cylinder
BASE_T = 10.0
FOOT_HW = 130.0

# ------------------------------------------------------------------ motor 3777
MOT_L, MOT_W, MOT_H = 70.0, 22.44, 18.60
GBOX_L = 37.0
HOLE_PITCH, NOSE_OFF = 17.60, 14.00
POCK_CLR = 0.4
ZIP_W, ZIP_D = 4.0, 2.5
ADJ_D = 3.3
SHAFT_OUT = 9.3                            # shaft protrusion one side


def cyl_x(r, h, x=0.0, sections=CQ):
    m = cylinder(radius=r, height=h, sections=sections)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation([x, 0, 0])
    return m


def cyl_z(r, h, z=0.0, sections=CQ):
    m = cylinder(radius=r, height=h, sections=sections)
    m.apply_translation([0, 0, z])
    return m


def yz(a_deg, r, z0=0.0):
    """Point at angle a from TOP, radius r, about an axis at height z0."""
    a = math.radians(a_deg)
    return r * math.sin(a), z0 + r * math.cos(a)


# ===========================================================================
def make_drum():
    half = DRUM_L / 2.0
    body = cyl_x(DRUM_OD / 2.0, DRUM_L)
    body = body.difference(cyl_x(DRUM_ID / 2.0, DRUM_L + 4.0))      # a plain tube

    # tank sleeve across the full diameter, plus four ribs, trimmed to the OD
    add = [cyl_z(HOLE_D / 2.0 + SLEEVE_T, DRUM_OD + 2.0)]
    for k in range(4):
        a = math.radians(45 + 90 * k)
        rib = box(extents=[RIB_L, RIB_T, DRUM_OD + 2.0])
        rib.apply_transform(trimesh.transformations.rotation_matrix(a, [1, 0, 0]))
        add.append(rib)
    for m in add:
        body = body.union(m)
    body = body.intersection(cyl_x(DRUM_OD / 2.0, DRUM_L))
    body = body.difference(cyl_z(HOLE_D / 2.0, DRUM_OD * 1.5))

    # square grooves cut OUTWARD from the inner wall, over the end bands
    cutters = []
    for s in (-1, 1):
        xc = s * (half - TRACK_W / 2.0)
        for k in range(N_TEETH):
            a = 2 * math.pi * k / N_TEETH
            t = box(extents=[TRACK_W + 2.0, TOOTH_W, TOOTH_D * 2.0])
            t.apply_transform(trimesh.transformations.rotation_matrix(a, [1, 0, 0]))
            t.apply_translation([xc, R_CONTACT * -math.sin(a), R_CONTACT * math.cos(a)])
            cutters.append(t)
    body = body.difference(trimesh.util.concatenate(cutters))

    # strap tabs flanking each mouth of the tank bore
    ty = HOLE_D / 2.0 + SLEEVE_T + TAB_T / 2.0
    tabs, slots = [], []
    for sz in (-1, 1):
        for sy in (-1, 1):
            zc = sz * (DRUM_OD / 2.0 + TAB_H / 2.0 - 6.0)
            t = box(extents=[TAB_W, TAB_T, TAB_H])
            t.apply_translation([0, sy * ty, zc]); tabs.append(t)
            sl = box(extents=[SLOT_L, TAB_T * 4, SLOT_W])
            sl.apply_translation([0, sy * ty, zc]); slots.append(sl)
    body = body.union(trimesh.util.concatenate(tabs))
    body = body.difference(trimesh.util.concatenate(slots))
    return body


# ===========================================================================
def upright_profile():
    """Rectangle with a half-cylinder on top, centred on the drum axis."""
    rect = SPoly([(-FOOT_HW, 0), (FOOT_HW, 0), (FOOT_HW, AXIS_H), (-FOOT_HW, AXIS_H)])
    dome = Point(0, AXIS_H).buffer(ARCH_R, quad_segs=CQ // 4)
    return rect.union(dome)


def make_base():
    prof = upright_profile()
    xin = DRUM_L / 2.0 + END_GAP                      # inboard face of each plate
    parts = []
    for s in (-1, 1):
        p = extrude_polygon(prof, PLATE_T)
        p.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
        p.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
        lo = p.bounds[0]
        p.apply_translation([-lo[0], 0, -lo[2]])
        p.apply_translation([xin if s > 0 else -(xin + PLATE_T), 0, 0])
        parts.append(p)

    base = box(extents=[2 * (xin + PLATE_T), 2 * FOOT_HW * 0.66, BASE_T])
    base.apply_translation([0, 0, BASE_T / 2.0])
    part = base
    for p in parts:
        part = part.union(p)

    # per motor: a seat on the INBOARD face of each plate. The motor body and
    # the wheel both live inside the drum, so nothing passes through the plate.
    cuts = []
    for s in (-1, 1):
        xp = s * (xin + PLATE_T / 2.0)
        for a in MOT_ANGS:
            y, z = yz(a, R_WHEEL_C, AXIS_H)
            d = box(extents=[9.0, 54.0, 13.0])
            d.apply_transform(trimesh.transformations.rotation_matrix(
                -math.radians(a), [1, 0, 0]))
            d.apply_translation([s * (xin - 0.5), y, z]); cuts.append(d)
            b = cylinder(radius=ADJ_D / 2.0, height=PLATE_T * 3, sections=48)
            b.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
            b.apply_translation([xp, y, z]); cuts.append(b)
    part = part.difference(trimesh.util.concatenate(cuts))
    return part


# ===========================================================================
def make_mount():
    """Bolts to the inboard face of an upright. The motor body and its wheel
    both sit inside the drum bore; the wheel bears outward on the grooves."""
    tongue = box(extents=[8.0, 52.0, 12.0])
    shell = box(extents=[GBOX_L + 10.0, MOT_W + 10.0, MOT_H + 8.0])
    shell.apply_translation([-(GBOX_L / 2.0 + 9.0), 0, 0])
    part = tongue.union(shell)
    pocket = box(extents=[GBOX_L + POCK_CLR, MOT_W + POCK_CLR, MOT_H + POCK_CLR])
    pocket.apply_translation([-(GBOX_L / 2.0 + 9.0), 0, 2.0])
    part = part.difference(pocket)
    cuts = []
    for sx in (-1, 1):
        z = box(extents=[ZIP_W, MOT_W + 40.0, ZIP_D])
        z.apply_translation([-(GBOX_L / 2.0 + 9.0) + sx * 11.0, 0, MOT_H / 2.0 + 1.0])
        cuts.append(z)
    adj = cylinder(radius=ADJ_D / 2.0, height=60.0, sections=48)
    adj.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    cuts.append(adj)
    return part.difference(trimesh.util.concatenate(cuts))


# ===========================================================================
def main():
    P = {"drum.stl": make_drum(), "base.stl": make_base(), "motor_mount.stl": make_mount()}
    for n, m in P.items():
        m.export(os.path.join(OUT, n))

    d = P["drum.stl"].copy(); d.apply_translation([0, 0, AXIS_H])
    tank = cyl_z(TANK_OD / 2.0, TANK_LEN, AXIS_H)
    wheels = []
    half = DRUM_L / 2.0
    for s in (-1, 1):
        xc = s * (half - TRACK_W / 2.0)
        for a in MOT_ANGS:
            y, z = yz(a, R_WHEEL_C, AXIS_H)
            w = cyl_x(WHEEL_OD / 2.0, WHEEL_W, xc, sections=96)
            w.apply_translation([0, y, z]); wheels.append(w)
            mb = box(extents=[MOT_L, MOT_W, MOT_H])
            mb.apply_transform(trimesh.transformations.rotation_matrix(
                -math.radians(a), [1, 0, 0]))
            mb.apply_translation([s * (half - TRACK_W - MOT_L / 2.0), y, z])
            wheels.append(mb)
    asm = trimesh.util.concatenate([P["base.stl"], d, tank] + wheels)
    asm.export(os.path.join(OUT, "assembly.stl"))

    env = (295.0, 315.0, 315.0)
    print(f"\n{'part':16s} {'wt':>6s} {'bbox mm':>26s} {'cm3':>9s} {'~g':>7s}  fits")
    for n in list(P) + ["assembly.stl"]:
        m = trimesh.load(os.path.join(OUT, n), force="mesh")
        b = m.bounds[1] - m.bounds[0]
        q = 8 if n == "motor_mount.stl" else 1
        g = m.volume / 1000 * .35 * 1.24 * q
        ok = "-" if n.startswith("assembly") else (
            "OK" if all(b[i] <= env[i] + .01 for i in range(3)) else "OVER")
        print(f"{n:16s} {str(m.is_watertight):>6s} {b[0]:7.1f} x{b[1]:7.1f} x{b[2]:7.1f} "
              f"{m.volume/1000:9.1f} {g:7.0f}  {ok}")

    ratio = (WHEEL_OD / 2.0) / R_CONTACT
    print(f"\ndrive ratio {WHEEL_OD/2:.1f}/{R_CONTACT:.0f} = {ratio:.3f}"
          f"  ->  inversions/min: "
          f"{120*ratio:.0f} (3V) / {185*ratio:.0f} (4.5V) / {250*ratio:.0f} (6V)")
    print(f"groove pitch {math.pi*DRUM_ID/N_TEETH:.2f} mm, {N_TEETH} grooves, "
          f"{TOOTH_D:.0f} deep -> root Ø{DRUM_ID+2*TOOTH_D:.0f}, wall left "
          f"{(DRUM_OD-DRUM_ID)/2-TOOTH_D:.0f} mm")


if __name__ == "__main__":
    main()

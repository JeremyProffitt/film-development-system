"""Internal-drive tank tumbler — drawing set (4 sheets, A3 landscape)."""

import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Wedge
import trimesh

import doc_framework as D                      # reuse the sheet framework
D.STL, D.IMG = "stl", "_render"
os.makedirs(D.IMG, exist_ok=True)
D.NS = 4
from doc_framework import (new_sheet, head, body, callout, table, hdim, vdim, leader,
                  strip, load, INK, GREY, DIMC, C1, C2, C3, C4, MONO)

DRUM_OD, DRUM_ID, DRUM_L = 270.0, 250.0, 198.0
WALL = (DRUM_OD - DRUM_ID) / 2.0
TRACK_W, N_TEETH, TOOTH_W, TOOTH_D = 34.0, 78, 5.0, 3.0
HOLE_D, SLEEVE_T, RIB_L = 106.0, 6.0, 50.0
TANK_OD, TANK_LEN = 102.0, 303.0
AXIS_H, ARCH_R, PLATE_T, BASE_T, FOOT_HW = 175.0, 124.5, 14.0, 10.0, 130.0
MOT_ANGS = (45.0, 135.0, -135.0, -45.0)     # 4 per end, from top
WHEEL_OD, WHEEL_W = 63.0, 29.0
MOT_L, MOT_W, MOT_H = 70.0, 22.44, 18.60
R_CONTACT = DRUM_ID / 2.0
R_WHEEL_C = R_CONTACT - WHEEL_OD / 2.0
RATIO = (WHEEL_OD / 2.0) / R_CONTACT
RPM = {3.0: 120.0, 4.5: 185.0, 6.0: 250.0}
PITCH = math.pi * DRUM_ID / N_TEETH
QTY = {"drum.stl": 1, "base.stl": 1, "motor_mount.stl": 8}
D.QTY = QTY


def build():
    pdf = PdfPages("tumbler_drawings.pdf")

    # ------------------------------------------------ 1 overview
    fig = new_sheet(1, "Cross-axis tank tumbler — internal drive",
                    "eight wheels inside the drum, bearing outward on grooves cut into its bore")
    strip(fig, load("assembly.stl"), [0.045, 0.45, 0.91, 0.37],
          {"iso", "front", "side", "top"}, "A1", px=840)

    head(fig, 0.045, 0.405, "THE PRINCIPLE")
    body(fig, 0.045, 0.372,
         "A tube lies on its side. A bore runs through it at right\n"
         "angles and the tank lives in that bore, so one turn of the\n"
         "drum is one full inversion of the tank — the motion the\n"
         "Paterson was designed around.\n\n"
         "The first 34 mm at each open end carries square grooves on\n"
         "its INNER wall. FOUR wheels per end sit inside the bore, 90°\n"
         "apart, pressing OUTWARD against those grooves. Eight in all.")

    head(fig, 0.375, 0.405, "DRIVE")
    axd = fig.add_axes([0.375, 0.262, 0.22, 0.125]); axd.axis("off")
    table(axd, [[f"{v:.1f} V", f"{RPM[v]:.0f}", f"{RPM[v]*RATIO:.0f}"] for v in (3.0, 4.5, 6.0)],
          ["supply", "motor", "inversions/min"], [0, 0, 1, 1], fs=8.6, colcolor={2: C1})
    body(fig, 0.375, 0.248,
         f"ratio {WHEEL_OD/2:.1f} / {R_CONTACT:.0f} = {RATIO:.3f}\n"
         f"{N_TEETH} grooves at {PITCH:.2f} mm pitch\n"
         f"8 motors: 4 per end at R{R_WHEEL_C:.1f}, 90° apart\n"
         f"stall torque at the drum ≈ 2.5 N·m", fs=8.8)

    head(fig, 0.655, 0.405, "PRINT MANIFEST")
    rows, tot = D.manifest()
    axm = fig.add_axes([0.655, 0.245, 0.30, 0.142]); axm.axis("off")
    table(axm, rows, ["part", "qty", "bbox mm", "cm³", "filament", "fits"], [0, 0, 1, 1],
          fs=7.6, colw=[.22, .08, .27, .12, .17, .14])
    body(fig, 0.655, 0.232, f"total printed material ≈ {tot:.0f} g", fs=9.0)

    callout(fig, 0.045, 0.048, 0.60, 0.155, accent=C4,
            title="FOUR PER END FULLY CONSTRAINS THE DRUM",
            text="A wheel inside a bore pushes the drum OUTWARD, so the upper pair carry the\n"
                 "weight and the lower pair stop it lifting. Four at 90° trap the drum\n"
                 "radially in every direction — a proper four-jaw constraint rather than the\n"
                 "hanging sheave that two would give, and it doubles the driving contacts.")
    callout(fig, 0.655, 0.048, 0.30, 0.155, accent=C2,
            title="AXIAL CONSTRAINT",
            text="The grooves run axially, so they do\n"
                 "not locate the drum along X. The\n"
                 "wheel sits in a 34 mm band with\n"
                 "5 mm of end float against the\n"
                 "29 mm tyre — that float is the\n"
                 "constraint. Keep it.")
    pdf.savefig(fig); plt.close(fig)

    # ------------------------------------------------ 2 drum
    fig = new_sheet(2, "Drum", "×1 · a tube with grooves inside both ends")
    strip(fig, load("drum.stl"), [0.50, 0.44, 0.455, 0.375], {"iso", "front", "under"}, "D1")

    ax = fig.add_axes([0.045, 0.30, 0.43, 0.52]); ax.set_aspect("equal"); ax.axis("off")
    ro, ri, rb = DRUM_OD / 2, DRUM_ID / 2, HOLE_D / 2
    hl = DRUM_L / 2
    for sy in (-1, 1):
        ax.add_patch(Rectangle((-hl, sy * ri if sy > 0 else -ro), DRUM_L, WALL,
                               fc="#cfdceb", ec=INK, lw=1.6))
        for s in (-1, 1):
            x0 = s * hl if s > 0 else -hl
            xs = x0 - (TRACK_W if s > 0 else 0)
            for k in range(11):
                xx = xs + 2 + k * (TRACK_W - 4) / 10.0
                ax.add_patch(Rectangle((xx, sy * ri if sy > 0 else -ri - TOOTH_D),
                                       1.7, TOOTH_D, fc="white", ec=C1, lw=.6))
    ax.add_patch(Rectangle((-rb - SLEEVE_T, -ro), SLEEVE_T, 2 * ro, fc="#dce8f7", ec=INK, lw=1.1))
    ax.add_patch(Rectangle((rb, -ro), SLEEVE_T, 2 * ro, fc="#dce8f7", ec=INK, lw=1.1))
    ax.add_patch(Rectangle((-RIB_L / 2, -ro), RIB_L, 2 * ro, fc="none", ec=C3, lw=1.0, ls=(0, (5, 3))))
    ax.add_patch(Rectangle((-TANK_OD / 2, -TANK_LEN / 2), TANK_OD, TANK_LEN,
                           fc="none", ec=C4, lw=1.3, ls=(0, (6, 3))))
    ax.text(0, TANK_LEN / 2 + 26, "tank Ø102 × 303", ha="center", fontsize=8.4, family=MONO, color=C4)
    ax.plot([-hl - 30, hl + 30], [0, 0], color=INK, lw=.8, ls=(0, (12, 4, 2, 4)))
    vdim(ax, hl + 34, -ro, ro, f"Ø{DRUM_OD:.0f} O.D.", tick=hl)
    vdim(ax, -hl - 34, -ri, ri, f"Ø{DRUM_ID:.0f} bore", tick=-hl)
    hdim(ax, -ro - 26, -hl, hl, f"{DRUM_L:.0f} overall", tick=-ro)
    hdim(ax, -ro - 48, hl - TRACK_W, hl, f"{TRACK_W:.0f} track", tick=-ro - 26)
    hdim(ax, ro + 20, -rb, rb, f"Ø{HOLE_D:.0f} tank bore", tick=ro, below=False)
    leader(ax, (hl - TRACK_W / 2, ri), (hl + 4, ro + 50),
           f"{N_TEETH} square grooves\nINSIDE the bore\n{TOOTH_W:.0f} wide × {TOOTH_D:.0f} deep\n"
           f"{PITCH:.2f} pitch", col=C1)
    leader(ax, (RIB_L / 2, -70), (-hl - 40, -ro - 62), f"ribs only across\nthe central {RIB_L:.0f}",
           col=C3, ha="left")
    ax.set_xlim(-hl - 96, hl + 104); ax.set_ylim(-TANK_LEN / 2 - 66, TANK_LEN / 2 + 54)
    fig.text(0.26, 0.292, "SECTION ON THE BORE AXIS", ha="center", fontsize=9.6,
             family=MONO, fontweight="bold", color=INK)

    head(fig, 0.50, 0.405, "CONSTRUCTION")
    body(fig, 0.50, 0.372,
         f"A plain tube, Ø{DRUM_OD:.0f} outside and Ø{DRUM_ID:.0f} inside — {WALL:.0f} mm wall.\n"
         f"Grooves cut {TOOTH_D:.0f} mm outward from the bore leave {WALL-TOOTH_D:.0f} mm\n"
         "of wall at the root.\n\n"
         f"A Ø{HOLE_D+2*SLEEVE_T:.0f} sleeve carries the tank bore across the tube.\n"
         f"Four ribs tie it to the shell, but only across the central\n"
         f"{RIB_L:.0f} mm — everything outboard of that is left clear so the\n"
         "motor bodies have somewhere to live.")
    callout(fig, 0.045, 0.045, 0.43, 0.175, accent=C2,
            title="PRINT IT IN TWO HALVES",
            text="On end it is 198 tall and Ø270, which fits — but the\n"
                 "Ø106 cross-bore then prints horizontally and needs support\n"
                 "down its whole length.\n\n"
                 "Split on the plane containing both axes: each half prints\n"
                 "flat-face-down support-free, and you lay the tank in\n"
                 "rather than threading it through.")
    callout(fig, 0.50, 0.045, 0.455, 0.175, accent=C4,
            title="THE GROOVES ARE THE ONE GUESS",
            text=f"{PITCH:.2f} mm pitch assumes the tread block spacing of the\n"
                 "3766 wheel, which Adafruit does not publish. Measure a\n"
                 "real tyre before you commit to 78 of them.\n\n"
                 "If they will not index, a plain high-friction bore works\n"
                 "nearly as well — the preload is doing most of the work\n"
                 "either way.")
    pdf.savefig(fig); plt.close(fig)

    # ------------------------------------------------ 3 base + mount
    fig = new_sheet(3, "Base and motor mount", "two uprights, a flat connector, eight mounts")
    strip(fig, load("base.stl"), [0.045, 0.50, 0.44, 0.31], {"iso", "front", "side"}, "B1")
    strip(fig, load("motor_mount.stl"), [0.52, 0.50, 0.435, 0.31], {"iso", "front"}, "M1")

    ax = fig.add_axes([0.045, 0.255, 0.40, 0.24]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-FOOT_HW, 0), 2 * FOOT_HW, AXIS_H, fc="#eef3f9", ec=INK, lw=1.6))
    ax.add_patch(Wedge((0, AXIS_H), ARCH_R, 0, 180, fc="#eef3f9", ec=INK, lw=1.6))
    ax.add_patch(Circle((0, AXIS_H), DRUM_ID / 2, fc="none", ec=C3, lw=1.1, ls=(0, (6, 3))))
    ax.add_patch(Circle((0, AXIS_H), DRUM_OD / 2, fc="none", ec=C3, lw=1.1, ls=(0, (6, 3))))
    for ang in MOT_ANGS:
        a = math.radians(ang)
        y, z = R_WHEEL_C * math.sin(a), AXIS_H + R_WHEEL_C * math.cos(a)
        ax.add_patch(Circle((y, z), WHEEL_OD / 2, fc="#dce8f7", ec=C1, lw=1.3))
        ax.add_patch(Circle((y, z), 4, fc=INK, ec="none"))
    ax.plot([0, 0], [AXIS_H - 40, AXIS_H + ARCH_R + 16], color=INK, lw=.8, ls=(0, (12, 4, 2, 4)))
    hdim(ax, -28, -FOOT_HW, FOOT_HW, f"{2*FOOT_HW:.0f} foot", tick=0)
    vdim(ax, FOOT_HW + 18, 0, AXIS_H, f"{AXIS_H:.0f} axis height", tick=FOOT_HW)
    leader(ax, (0, AXIS_H + ARCH_R), (-FOOT_HW - 10, AXIS_H + 86), f"half cylinder R{ARCH_R:.0f}", ha="right")
    leader(ax, (R_WHEEL_C * math.sin(math.radians(45.0)),
                AXIS_H + R_WHEEL_C * math.cos(math.radians(45.0))),
           (FOOT_HW + 4, AXIS_H + 104),
           f"4 wheels per end\nR{R_WHEEL_C:.1f}, 90° apart", col=C1)
    ax.set_xlim(-FOOT_HW - 96, FOOT_HW + 96); ax.set_ylim(-58, AXIS_H + ARCH_R + 26)
    fig.text(0.245, 0.247, "UPRIGHT — ELEVATION", ha="center", fontsize=9.6,
             family=MONO, fontweight="bold", color=INK)

    head(fig, 0.50, 0.455, "BASE")
    body(fig, 0.50, 0.422,
         f"One piece: a flat {BASE_T:.0f} mm connector between two uprights,\n"
         f"each a rectangle with a half cylinder on top. Plates are\n"
         f"{PLATE_T:.0f} mm thick and stand {3:.0f} mm clear of the drum ends.\n\n"
         "Each upright carries FOUR motor mounts on its INBOARD face.\n"
         "Nothing passes through the plate — motor, mount and wheel\n"
         "are all inside the drum bore.\n\n"
         "ASSEMBLY: bolt all eight mounts to the uprights first, then\n"
         "lower the drum straight down over them. The bore is Ø250\n"
         "and the motor cluster spans Ø206, so it drops in clear.", fs=9.0)

    callout(fig, 0.045, 0.055, 0.91, 0.172, accent=C1,
            title="THE ONE CONSTRAINT THE BRIEF COULD NOT HAVE",
            text="The motor body is 70 mm long and the groove band is only 34 mm deep, so the motor cannot sit wholly within the band.\n"
                 "It is mounted gearbox-outward at the drum mouth with the wheel on its inboard shaft, and the body extends a further\n"
                 "70 mm INTO the drum along its axis.\n\n"
                 "That is why the ribs stop at the central 50 mm. Measured off the mesh, the bore is clear to R125 everywhere the motors\n"
                 "live, and the motor envelope reaches R103 — 22 mm of radial clearance to the rotating wall.")
    pdf.savefig(fig); plt.close(fig)

    # ------------------------------------------------ 4 BOM + views
    fig = new_sheet(4, "Bill of materials and full view set", "and what is still wrong with it")
    head(fig, 0.045, 0.845, "BOUGHT PARTS")
    bom = [["Adafruit 3777", "TT gearbox motor", "8", "four per end"],
           ["Adafruit 3766", "TT wheel Ø63 × 29", "8", "square tread blocks"],
           ["M4 × 30", "preload adjuster", "8", "+ nuts"],
           ["M4 × 16", "mount to upright", "16", "+ nuts"],
           ["Zip tie 2.5 mm", "motor retention", "16", "two per motor"],
           ["Webbing strap 25 mm", "tank retention", "2", "through the four tabs"],
           ["PSU + PWM", "6 V 10 A", "1", "8 motors in parallel"]]
    axb = fig.add_axes([0.045, 0.625, 0.44, 0.195]); axb.axis("off")
    table(axb, bom, ["part", "description", "qty", "note"], [0, 0, 1, 1],
          fs=8.4, colw=[.26, .34, .09, .31])

    head(fig, 0.52, 0.845, "REMAINING WEAKNESSES")
    body(fig, 0.52, 0.812,
         "WIRING ROTATES PAST THE MOTORS. Four motors sit inside a\n"
         "rotating tube. Their leads must exit through the open end\n"
         "without fouling the drum — route them along the upright,\n"
         "not across the mouth.\n\n"
         "THE DRUM RUNS ON EIGHT TYRES. No bearings anywhere. Silicone\n"
         "on printed plastic sheds dust and creeps; wheels are a\n"
         "consumable and preload needs re-checking.\n\n"
         "EIGHT MOTORS WILL FIGHT EACH OTHER. TT speed spread is about\n"
         "±10 %, and eight friction-coupled to one drum means the fast\n"
         "ones drive and the slow ones drag. It works, but it costs\n"
         "current and tread life. Stall current is now about 12 A.\n\n"
         "OPEN LOOP. No encoder, so the tank parks wherever it stops.\n"
         "Add a microswitch if it must stop upright for filling.", fs=9.0)

    strip(fig, load("assembly.stl"), [0.045, 0.10, 0.91, 0.44],
          {"iso", "front", "side", "top", "under", "iso-rear"}, "A2", px=700)
    pdf.savefig(fig); plt.close(fig)
    pdf.close()
    print(os.path.abspath("tumbler_drawings.pdf"))


if __name__ == "__main__":
    build()

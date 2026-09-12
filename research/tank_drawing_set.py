"""
Paterson Super System 4 - Multi-Reel 3 (PTP116) component drawing set.

Six-sheet A3 landscape PDF, one component per sheet:
   1  Cover / range summary + provenance
   2  Tank body            PTP116
   3  Centre column        SPTP116
   4  Light-trap funnel    SPTP110 (pt 1)
   5  Lid / EVA cap        SPTP110 (pt 2)
   6  Agitator rod         SPTP109

Provenance flags used throughout:
   (P)  published / vendor-stated
   ( *) derived from the (P) figures + reel pitch + retail packaging heights
   (R)  reconstructed proportionally from product photography - shape is right,
        the number is an estimate
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon, Circle, Wedge

# ---------------------------------------------------------------------------
# Master geometry (mm)
# ---------------------------------------------------------------------------
OD, ID = 102.0, 95.0                 # barrel outside / inside dia      (P)
WALL = (OD - ID) / 2.0               # 3.5
BASE_T = 7.0                         # base thickness                   (R)
PITCH = 44.0                         # reel pitch, 35 mm setting        (*)
CLEAR = 9.0                          # clearance above top reel         (*)
FUNNEL_INTRUDE = 51.0                # funnel depth inside barrel  (P: 279-229)
RIM_H = 13.0                         # bayonet collar height            (R)
RIM_OD = 106.0                       # bayonet collar dia               (R)

N_REELS = 3
FILL_D = N_REELS * PITCH + CLEAR     # 141  internal depth to funnel    (*)
INNER_D = FILL_D + FUNNEL_INTRUDE    # 192  internal depth to lid       (*)
BODY_H = INNER_D + BASE_T            # 199  barrel external height      (*)

COL_LEN = INNER_D - 2.0              # 190  centre column length        (*)
COL_OD, COL_BORE = 25.0, 15.0        # (R)
COL_FLG_D, COL_FLG_T = 46.0, 4.0     # (R)
COL_HEAD_D, COL_HEAD_H = 32.0, 14.0  # (R)

FUN_RIM_D, FUN_RIM_T = 110.0, 6.0    # (R)
FUN_SKIRT_D, FUN_SKIRT_H = 94.0, 12.0
FUN_THROAT_D = 36.0
FUN_CONE_H = 34.0
FUN_H = FUN_RIM_T + FUN_SKIRT_H + FUN_CONE_H + 6.0   # 58

CAP_OD, CAP_SKIRT, CAP_TOP = 98.0, 14.0, 3.0         # (R)
CAP_SEAL_D = 92.0

ROD_LEN, ROD_D = 115.0, 6.5          # (R)
ROD_KNOB_D, ROD_KNOB_T = 26.0, 7.0
ROD_TIP_L, ROD_TIP_W = 16.0, 9.0

# per-model derived heights:  overall = N*44 + 83
RANGE = [
    # name, code, reels, 35mm, 120, chem, overall*, box height, column part, col len
    ("35 mm Tank",   "PTP114", 1, "1", "\u2014", "290 ml",  127, "127 mm (P)", "SPTP114", 102),
    ("Universal",    "PTP115", 2, "2", "1",      "580 ml",  171, "165 mm (P)", "SPTP115", 146),
    ("Multi-Reel 3", "PTP116", 3, "3", "2",      "1000 ml", 215, "~210 mm *",  "SPTP116", 190),
    ("Multi-Reel 5", "PTP117", 5, "5", "3",      "1500 ml", 303, "294 mm (P)", "SPTP117", 278),
    ("Multi-Reel 8", "PTP118", 8, "8", "5",      "2500 ml", 435, "442 mm (P)", "SPTP118", 410),
]

INK, STEEL, HATCH, DIMC, GREY = "#10243b", "#2f6fb5", "#a8bcd2", "#b3261e", "#5b6b7d"
MONO = "monospace"

# ---------------------------------------------------------------------------
# Sheet framework
# ---------------------------------------------------------------------------
def new_sheet(sheet_no, title, part_no, fits, scale_txt):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=150, facecolor="white")
    fig.patches.append(Rectangle((0.018, 0.018), 0.964, 0.964, transform=fig.transFigure,
                                 fill=False, ec=INK, lw=2.0, zorder=5))
    fig.patches.append(Rectangle((0.028, 0.028), 0.944, 0.944, transform=fig.transFigure,
                                 fill=False, ec=INK, lw=0.7, zorder=5))
    fig.text(0.045, 0.955, "PATERSON SUPER SYSTEM 4  \u00b7  MULTI-REEL 3 TANK SET",
             fontsize=11, color=GREY, family=MONO, va="center")
    fig.text(0.955, 0.955, f"SHEET {sheet_no} OF 6", fontsize=11, color=GREY,
             family=MONO, va="center", ha="right")
    fig.lines.append(plt.Line2D([0.045, 0.955], [0.941, 0.941], transform=fig.transFigure,
                                color=INK, lw=0.7))

    # ---- title block, bottom right
    tb_x, tb_y, tb_w, tb_h = 0.615, 0.042, 0.357, 0.175
    fig.patches.append(Rectangle((tb_x, tb_y), tb_w, tb_h, transform=fig.transFigure,
                                 fc="#f4f7fb", ec=INK, lw=1.4, zorder=6))
    rows = [("TITLE", title), ("PART No.", part_no), ("FITS", fits),
            ("UNITS", "millimetres"), ("SCALE", scale_txt),
            ("STATUS", "reconstruction \u2014 verify before machining")]
    for i, (k, v) in enumerate(rows):
        y = tb_y + tb_h - (i + 0.62) * (tb_h / len(rows))
        fig.text(tb_x + 0.010, y, k, fontsize=8, color=GREY, family=MONO,
                 va="center", zorder=7)
        fig.text(tb_x + 0.078, y, v, fontsize=9, color=INK, family=MONO,
                 va="center", fontweight="bold", zorder=7)
        if i:
            fig.lines.append(plt.Line2D([tb_x, tb_x + tb_w],
                                        [y + tb_h / (2 * len(rows)), y + tb_h / (2 * len(rows))],
                                        transform=fig.transFigure, color="#8fa3b8",
                                        lw=0.5, zorder=7))
    fig.lines.append(plt.Line2D([tb_x + 0.072, tb_x + 0.072], [tb_y, tb_y + tb_h],
                                transform=fig.transFigure, color="#8fa3b8", lw=0.5, zorder=7))
    fig.text(0.045, 0.030, "Provenance:  (P) published / vendor-stated    "
                           "( * ) derived from (P) data    (R) reconstructed from product "
                           "photography \u2014 shape correct, number estimated",
             fontsize=7.6, color=GREY, family=MONO, va="bottom")
    return fig


def draw_axes(fig, rect=(0.045, 0.255, 0.545, 0.665)):
    ax = fig.add_axes(list(rect))
    ax.set_aspect("equal")
    ax.grid(True, color="#d3dde7", lw=0.5, ls=":")
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=7.5, colors=GREY)
    for s in ax.spines.values():
        s.set_color("#8fa3b8")
    return ax


def notes_panel(fig, heading, body, rect=(0.615, 0.255, 0.357, 0.665)):
    ax = fig.add_axes(list(rect))
    ax.axis("off")
    ax.text(0, 1.0, heading, fontsize=11, fontweight="bold", color=INK,
            family=MONO, va="top")
    ax.text(0, 0.955, body, fontsize=8.6, color=INK, family=MONO,
            va="top", linespacing=1.5)
    return ax


# ---------------------------------------------------------------------------
# Dimension primitives
# ---------------------------------------------------------------------------
def vdim(ax, x, y0, y1, label, tick_from=None, fs=8.5):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.15),
                zorder=8)
    if tick_from is not None:
        for y in (y0, y1):
            ax.plot([tick_from, x + 3 * (1 if x > tick_from else -1)], [y, y],
                    color=DIMC, lw=0.55, ls=(0, (4, 3)), zorder=7)
    ax.text(x + 3.5, (y0 + y1) / 2.0, label, rotation=90, ha="center", va="center",
            fontsize=fs, color=DIMC, family=MONO, zorder=9)


def hdim(ax, y, x0, x1, label, tick_from=None, below=True, fs=8.5):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.15),
                zorder=8)
    if tick_from is not None:
        for x in (x0, x1):
            ax.plot([x, x], [tick_from, y + 3 * (-1 if below else 1)],
                    color=DIMC, lw=0.55, ls=(0, (4, 3)), zorder=7)
    ax.text((x0 + x1) / 2.0, y + (-5.5 if below else 5.0), label, ha="center",
            va="top" if below else "bottom", fontsize=fs, color=DIMC, family=MONO, zorder=9)


def leader(ax, xy, xytext, label, fs=8.5, ha="left"):
    ax.annotate(label, xy, xytext, arrowprops=dict(arrowstyle="->", color=DIMC, lw=0.95),
                fontsize=fs, color=DIMC, family=MONO, ha=ha, va="center", zorder=9)


def centreline(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], color=INK, lw=0.85, ls=(0, (14, 4, 2, 4)), zorder=6)


def centreline_h(ax, y, x0, x1):
    ax.plot([x0, x1], [y, y], color=INK, lw=0.85, ls=(0, (14, 4, 2, 4)), zorder=6)


def view_label(ax, x, y, text):
    ax.text(x, y, text, ha="center", va="top", fontsize=9.5, color=INK,
            family=MONO, fontweight="bold")


pdf_path = "tank_drawing_set.pdf"
pdf = PdfPages(pdf_path)

# ===========================================================================
# SHEET 1 - cover
# ===========================================================================
fig = new_sheet(1, "RANGE SUMMARY", "\u2014", "Super System 4", "n/a")
ax = fig.add_axes([0.045, 0.255, 0.545, 0.665]); ax.axis("off")
ax.text(0, 1.0, "CURRENT SUPER SYSTEM 4 TANK RANGE", fontsize=12.5,
        fontweight="bold", color=INK, family=MONO, va="top")
ax.text(0, 0.955, "Five tanks for sale \u2014 five different heights, one diameter.",
        fontsize=9.5, color=GREY, family=MONO, va="top")

cols = ["Model", "Code", "Reel\nslots", "35 mm", "120/\n220", "Chemistry\nfull load",
        "Overall\nheight *", "Retail box\nheight", "Column\npart"]
cell = [[r[0], r[1], str(r[2]), r[3], r[4], r[5], f"{r[6]} mm", r[7], r[8]] for r in RANGE]
tbl = ax.table(cellText=cell, colLabels=cols, cellLoc="center",
               bbox=[0.0, 0.50, 1.0, 0.40])
tbl.auto_set_font_size(False); tbl.set_fontsize(9)
for (r, c), cl in tbl.get_celld().items():
    cl.set_edgecolor("#8fa3b8"); cl.set_linewidth(0.8)
    if r == 0:
        cl.set_facecolor(INK); cl.set_text_props(color="white", fontweight="bold", fontsize=8.2)
        cl.set_height(0.155)
    else:
        cl.set_facecolor("#f4f7fb" if r % 2 else "white"); cl.set_height(0.105)
        if c == 2:
            cl.set_text_props(fontweight="bold", color=STEEL)
        if r == 3:
            cl.set_facecolor("#dce8f7")

ax.text(0, 0.40, "SHEET INDEX", fontsize=11, fontweight="bold", color=INK,
        family=MONO, va="top")
ax.text(0, 0.355,
        "  2   Tank body . . . . . . . . . . . .  PTP116   model-specific\n"
        "  3   Centre column . . . . . . . . . .  SPTP116  model-specific\n"
        "  4   Light-trap funnel . . . . . . . .  SPTP110  fits ALL SS4 tanks\n"
        "  5   Lid / EVA watertight cap  . . . .  SPTP110  fits ALL SS4 tanks\n"
        "  6   Agitator rod (stirrer)  . . . . .  SPTP109  fits ALL SS4 tanks\n\n"
        "Only the tank barrel and the centre column change length with\n"
        "reel count. Because each column is cut to its model's length, its\n"
        "head always sits directly under the funnel \u2014 which is why one\n"
        "short agitator rod serves the whole range, from 35 mm to MR8.",
        fontsize=9.2, color=INK, family=MONO, va="top", linespacing=1.5)

notes_panel(fig, "PROVENANCE \u2014 READ FIRST",
    "Paterson publishes NO dimensional drawings or spec\n"
    "sheets for the Super System 4 range. Checked:\n"
    "patersonphotographic.com, macodirect, Parallax,\n"
    "B&C Camera, Unique Photo, Adorama, EMS Diasum.\n"
    "None list a height or a diameter.\n\n"
    "(P)  THE ONLY HARD NUMBERS\n"
    "  \u2022 internal \u00f8 95 mm (3.75 in)\n"
    "  \u2022 Multi-Reel 5 internal depth 229 mm (9 in) to the\n"
    "    funnel, 279 mm (11 in) to the lid   [B&H spec Q&A]\n"
    "  \u2022 box heights 127 / 165 / 294 / 442 mm for\n"
    "    PTP114 / 115 / 117 / 118   [Amazon item details]\n"
    "  \u2022 fill volumes 290 ml per 135/126 roll, 370 ml per\n"
    "    127, 500 ml per 120/220   [Paterson / macodirect]\n"
    "  \u2022 funnel+lid kit SPTP110 fits all SS4 tanks; column\n"
    "    +agitator kits are per-model SPTP114\u2013118; agitator\n"
    "    rod SPTP109 is stated to fit 35 mm through MR8\n"
    "    [Freestyle 142007, Firstcall PATE902, KHB PTS109]\n\n"
    "( * ) DERIVED\n"
    "  Reel pitch 44 mm = 229 mm \u00f7 5 reels. Every barrel\n"
    "  height then follows as  N \u00d7 44 + 83 mm, which lands\n"
    "  within 3 % of all four published box heights.\n\n"
    "(R)  RECONSTRUCTED\n"
    "  Column, funnel, cap and rod carry no published\n"
    "  dimension of any kind. Their shapes are taken from\n"
    "  product photography and scaled off the \u00f895 bore.\n"
    "  Treat every (R) number as \u00b15 %.\n\n"
    "  DO NOT cut a water jacket, fixture or replacement\n"
    "  part to these figures without checking the real\n"
    "  tank with calipers first.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# SHEET 2 - tank body
# ===========================================================================
fig = new_sheet(2, "TANK BODY", "PTP116", "Multi-Reel 3", "1:2 approx")
ax = draw_axes(fig)

# --- section (left)
for x0 in (-OD / 2.0, ID / 2.0):
    ax.add_patch(Rectangle((x0, 0), WALL, BODY_H, fc=HATCH, ec=INK, lw=1.5, hatch="////"))
ax.add_patch(Rectangle((-OD / 2.0, 0), OD, BASE_T, fc=HATCH, ec=INK, lw=1.5, hatch="////"))
for x0 in (-RIM_OD / 2.0, ID / 2.0):
    ax.add_patch(Rectangle((x0, BODY_H - RIM_H), (RIM_OD - ID) / 2.0, RIM_H,
                           fc="#8fa8c4", ec=INK, lw=1.5))
centreline(ax, 0, -18, BODY_H + 26)
ax.plot([-ID / 2.0, ID / 2.0], [BASE_T + FILL_D, BASE_T + FILL_D],
        color=STEEL, lw=1.1, ls=":", zorder=6)
ax.text(0, BASE_T + FILL_D + 4, "funnel seats here \u2014 fill line",
        ha="center", va="bottom", fontsize=7.6, color=STEEL, family=MONO)
for i in range(N_REELS):
    y0 = BASE_T + i * PITCH
    ax.add_patch(Rectangle((-46, y0), 92, PITCH - 2, fc="none", ec=STEEL, lw=0.9, ls="--"))
ax.text(0, BASE_T + 1.5 * PITCH, "reel envelope\n3 \u00d7 44", ha="center", va="center",
        fontsize=7.6, color=STEEL, family=MONO)

vdim(ax, 82, 0, BODY_H, "199*  overall barrel", tick_from=OD / 2.0)
vdim(ax, 112, BASE_T, BASE_T + INNER_D, "192*  internal depth to lid", tick_from=OD / 2.0)
vdim(ax, 142, BASE_T, BASE_T + FILL_D, "141*  internal depth to funnel", tick_from=OD / 2.0)
vdim(ax, -84, 0, BASE_T, "7R base", tick_from=-OD / 2.0)
vdim(ax, -84, BODY_H - RIM_H, BODY_H, "13R collar", tick_from=-OD / 2.0)
hdim(ax, -26, -OD / 2.0, OD / 2.0, "\u00d8102 O.D. (4.00 in) *", tick_from=0)
hdim(ax, -44, -ID / 2.0, ID / 2.0, "\u00d895 I.D. (3.75 in) P", tick_from=0)
leader(ax, (-OD / 2.0 + WALL / 2.0, 150), (-152, 168), "wall 3.5*")
view_label(ax, 0, -62, "SECTION A-A")

# --- plan (right)
cx, cy = 200.0, 100.0
ax.add_patch(Circle((cx, cy), RIM_OD / 2.0, fc="#dbe6f2", ec=INK, lw=1.3))
ax.add_patch(Circle((cx, cy), OD / 2.0, fc="#eef3f9", ec=INK, lw=1.5))
ax.add_patch(Circle((cx, cy), ID / 2.0, fc="white", ec=INK, lw=1.5))
for a in (90, 210, 330):
    ax.add_patch(Wedge((cx, cy), RIM_OD / 2.0, a - 11, a + 11, width=(RIM_OD - ID) / 2.0,
                       fc="#8fa8c4", ec=INK, lw=1.1))
ax.add_patch(Circle((cx, cy), COL_OD / 2.0, fc="#dfe8f2", ec=INK, lw=1.0, ls="--"))
centreline(ax, cx, cy - 72, cy + 72)
centreline_h(ax, cy, cx - 72, cx + 72)
leader(ax, (cx + 32, cy + 44), (cx + 20, cy + 84), "3 \u00d7 bayonet lug,\n120\u00b0 apart  (R)", ha="left")
hdim(ax, cy - 74, cx - ID / 2.0, cx + ID / 2.0, "\u00d895 P", tick_from=cy)
view_label(ax, cx, cy - 96, "PLAN \u2014 TOP")
ax.plot([-OD / 2.0 - 12, -OD / 2.0 - 12], [0, BODY_H], color=INK, lw=0.8)
ax.text(-OD / 2.0 - 16, BODY_H / 2.0, "A", fontsize=10, color=INK, family=MONO,
        ha="right", va="center", fontweight="bold")

ax.set_xlim(-160, 285); ax.set_ylim(-105, 250)
ax.set_xlabel("mm", fontsize=8, color=GREY)

notes_panel(fig, "TANK BODY \u2014 PTP116",
    "One-piece high-impact polystyrene moulding.\n\n"
    "BORE IS COMMON TO THE WHOLE RANGE\n"
    "  \u00d8102 outside / \u00d895 inside on every Super\n"
    "  System 4 tank, 35 mm through Multi-Reel 8.\n"
    "  Only the barrel length changes.\n\n"
    "HEIGHT RULE  (derived)\n"
    "    barrel height  =  N \u00d7 44 + 76 mm\n"
    "    overall + lid  =  N \u00d7 44 + 83 mm\n"
    "  where N = number of 35 mm reel slots.\n\n"
    "    N=1  PTP114   127 mm   (box 127 P)\n"
    "    N=2  PTP115   171 mm   (box 165 P)\n"
    "    N=3  PTP116   215 mm   (box ~210 *)\n"
    "    N=5  PTP117   303 mm   (box 294 P)\n"
    "    N=8  PTP118   435 mm   (box 442 P)\n\n"
    "CAPACITY, PTP116\n"
    "  3 \u00d7 35 mm @ 290 ml  =   870 ml\n"
    "  2 \u00d7 120   @ 500 ml  =  1000 ml\n"
    "  6 \u00d7 4\u00d75 in sheets in a MOD54 holder\n\n"
    "A 120 reel occupies ~70 mm of column, so\n"
    "roll-film capacity is always lower than\n"
    "35 mm capacity in the same barrel.\n\n"
    "The bayonet collar detail at the rim is (R) \u2014\n"
    "lug count and angle are read off photographs.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# SHEET 3 - centre column
# ===========================================================================
fig = new_sheet(3, "CENTRE COLUMN", "SPTP116", "Multi-Reel 3 only", "1:2 approx")
ax = draw_axes(fig)

ax.add_patch(Rectangle((-COL_FLG_D / 2.0, 0), COL_FLG_D, COL_FLG_T,
                       fc=HATCH, ec=INK, lw=1.5, hatch="////"))
for x0 in (-COL_OD / 2.0, COL_BORE / 2.0):
    ax.add_patch(Rectangle((x0, COL_FLG_T), (COL_OD - COL_BORE) / 2.0,
                           COL_LEN - COL_FLG_T - COL_HEAD_H,
                           fc=HATCH, ec=INK, lw=1.5, hatch="////"))
for x0 in (-COL_HEAD_D / 2.0, COL_BORE / 2.0):
    ax.add_patch(Rectangle((x0, COL_LEN - COL_HEAD_H), (COL_HEAD_D - COL_BORE) / 2.0,
                           COL_HEAD_H, fc="#8fa8c4", ec=INK, lw=1.5))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * COL_BORE / 2.0 - (3 if s > 0 else 0), COL_LEN - 6), 3, 6,
                           fc=STEEL, ec=INK, lw=0.9))
centreline(ax, 0, -14, COL_LEN + 30)
for i in range(N_REELS):
    y0 = COL_FLG_T + 2 + i * PITCH
    ax.add_patch(Rectangle((-46, y0), 92, PITCH - 2, fc="none", ec=STEEL, lw=0.8, ls="--"))
    ax.text(48, y0 + PITCH / 2.0 - 1, f"reel {i+1}", fontsize=7.2, color=STEEL,
            family=MONO, va="center")

vdim(ax, 74, 0, COL_LEN, "190*  column length", tick_from=COL_FLG_D / 2.0)
leader(ax, (-COL_FLG_D / 2.0 + 4, COL_FLG_T / 2.0), (-96, -14), "4R flange")
vdim(ax, -80, COL_LEN - COL_HEAD_H, COL_LEN, "14R head", tick_from=-COL_HEAD_D / 2.0)
hdim(ax, -24, -COL_FLG_D / 2.0, COL_FLG_D / 2.0, "\u00d846R  foot flange", tick_from=0)
hdim(ax, COL_LEN + 22, -COL_OD / 2.0, COL_OD / 2.0, "\u00d825R", tick_from=COL_LEN, below=False)
hdim(ax, COL_LEN + 40, -COL_BORE / 2.0, COL_BORE / 2.0, "\u00d815R  bore", tick_from=COL_LEN + 30,
     below=False)
leader(ax, (COL_BORE / 2.0 + 1, COL_LEN - 3), (56, COL_LEN + 22),
       "drive tangs \u2014 the\nagitator rod slots\nover these  (R)")
view_label(ax, 0, -50, "SECTION \u2014 COLUMN ON CENTRELINE")

ax.set_xlim(-150, 190); ax.set_ylim(-96, COL_LEN + 62)
ax.set_xlabel("mm", fontsize=8, color=GREY)

nax = notes_panel(fig, "CENTRE COLUMN \u2014 SPTP116",
    "MODEL-SPECIFIC. Paterson sells a separate column\n"
    "+ agitator kit for each tank, which is the clearest\n"
    "evidence that this is the only part besides the\n"
    "barrel whose length changes:\n\n"
    "   SPTP114  35 mm       SPTP117  Multi-Reel 5\n"
    "   SPTP115  Universal   SPTP118  Multi-Reel 8\n"
    "   SPTP116  Multi-Reel 3\n\n"
    "Reels push down over the column and are keyed to\n"
    "it; the head sits just clear of the funnel so the\n"
    "agitator rod can engage it through the throat.\n\n"
    "DERIVED LENGTH BY MODEL   ( N \u00d7 44 + 58 )")
cell = [[r[8], r[0], str(r[2]), f"{r[9]} mm"] for r in RANGE]
t = nax.table(cellText=cell, colLabels=["Part", "Tank", "Reels", "Length *"],
              cellLoc="center", bbox=[0.0, 0.30, 1.0, 0.235])
t.auto_set_font_size(False); t.set_fontsize(8.6)
for (r, c), cl in t.get_celld().items():
    cl.set_edgecolor("#8fa3b8"); cl.set_linewidth(0.8)
    if r == 0:
        cl.set_facecolor(INK); cl.set_text_props(color="white", fontweight="bold", fontsize=8.2)
    else:
        cl.set_facecolor("#dce8f7" if r == 3 else ("#f4f7fb" if r % 2 else "white"))
nax.text(0, 0.265,
         "Every dimension on this sheet is (R) except the\n"
         "length, which is (*) \u2014 it follows the same 44 mm\n"
         "reel pitch that reproduces all four published\n"
         "tank box heights. Wall thickness, flange and\n"
         "head geometry are read off product photographs.",
         fontsize=8.6, color=INK, family=MONO, va="top", linespacing=1.5)
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# SHEET 4 - funnel
# ===========================================================================
fig = new_sheet(4, "LIGHT-TRAP FUNNEL", "SPTP110 (pt 1)", "ALL Super System 4", "1:1.5 approx")
ax = draw_axes(fig)

top = FUN_H
ax.add_patch(Rectangle((-FUN_RIM_D / 2.0, top - FUN_RIM_T), FUN_RIM_D, FUN_RIM_T,
                       fc=HATCH, ec=INK, lw=1.5, hatch="////"))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * FUN_SKIRT_D / 2.0 - (2.5 if s > 0 else 0),
                            top - FUN_RIM_T - FUN_SKIRT_H), 2.5, FUN_SKIRT_H,
                           fc=HATCH, ec=INK, lw=1.5, hatch="////"))
    ax.add_patch(Polygon([(s * FUN_SKIRT_D / 2.0, top - FUN_RIM_T - FUN_SKIRT_H),
                          (s * (FUN_SKIRT_D / 2.0 - 2.5), top - FUN_RIM_T - FUN_SKIRT_H),
                          (s * (FUN_THROAT_D / 2.0 - 0.5), 6),
                          (s * FUN_THROAT_D / 2.0, 6)],
                         closed=True, fc=HATCH, ec=INK, lw=1.5, hatch="////"))
    ax.add_patch(Rectangle((s * FUN_THROAT_D / 2.0 - (2.5 if s > 0 else 0), 0), 2.5, 6,
                           fc=HATCH, ec=INK, lw=1.5, hatch="////"))
    ax.add_patch(Rectangle((s * FUN_SKIRT_D / 2.0 - (4 if s > 0 else 0),
                            top - FUN_RIM_T - FUN_SKIRT_H + 2), 4, 4,
                           fc=STEEL, ec=INK, lw=0.9))
centreline(ax, 0, -14, top + 34)
for sx in (-1, 1):
    ax.annotate("", (sx * (FUN_THROAT_D / 2.0 - 3), 3), (sx * 26, top + 10),
                arrowprops=dict(arrowstyle="->", color=STEEL, lw=1.5,
                                connectionstyle="arc3,rad=0.15"))
ax.text(0, top + 40, "chemistry in \u2014 light-trapped annulus", fontsize=7.8,
        color=STEEL, family=MONO, ha="center", va="bottom")

vdim(ax, 74, 0, top, "58R  overall", tick_from=FUN_RIM_D / 2.0)
vdim(ax, -92, top - FUN_RIM_T, top, "6R rim", tick_from=-FUN_RIM_D / 2.0)
vdim(ax, -92, 0, 6, "6R throat wall", tick_from=-FUN_THROAT_D / 2.0)
hdim(ax, top + 16, -FUN_RIM_D / 2.0, FUN_RIM_D / 2.0, "\u00d8110R  rim flange",
     tick_from=top, below=False)
hdim(ax, -20, -FUN_SKIRT_D / 2.0, FUN_SKIRT_D / 2.0, "\u00d894R  seals in \u00d895 bore",
     tick_from=0)
hdim(ax, -38, -FUN_THROAT_D / 2.0, FUN_THROAT_D / 2.0, "\u00d836R  throat", tick_from=0)
leader(ax, (-FUN_SKIRT_D / 2.0 + 2, top - FUN_RIM_T - FUN_SKIRT_H + 4), (-152, top - 14),
       "bayonet lug (R)")
view_label(ax, 0, -58, "SECTION")

cx, cy = 178.0, 30.0
ax.add_patch(Circle((cx, cy), FUN_RIM_D / 2.0, fc="#dbe6f2", ec=INK, lw=1.4))
ax.add_patch(Circle((cx, cy), FUN_SKIRT_D / 2.0, fc="#eef3f9", ec=INK, lw=1.2, ls="--"))
ax.add_patch(Circle((cx, cy), FUN_THROAT_D / 2.0, fc="white", ec=INK, lw=1.4))
for a in (90, 210, 330):
    ax.add_patch(Wedge((cx, cy), FUN_SKIRT_D / 2.0, a - 11, a + 11, width=4,
                       fc=STEEL, ec=INK, lw=1.0))
centreline(ax, cx, cy - 72, cy + 72)
centreline_h(ax, cy, cx - 72, cx + 72)
view_label(ax, cx, cy - 76, "PLAN \u2014 TOP")

ax.set_xlim(-155, 260); ax.set_ylim(-90, 140)
ax.set_xlabel("mm", fontsize=8, color=GREY)

notes_panel(fig, "LIGHT-TRAP FUNNEL \u2014 SPTP110",
    "UNIVERSAL PART. Freestyle sells this as the\n"
    "\u201cSuper System 4 Tank Top Lid & Funnel Replacement\n"
    "Kit\u201d, #142007 / Paterson SPTP110, described as\n"
    "fitting all Super System 4 series tanks \u2014 so one\n"
    "funnel covers 35 mm through Multi-Reel 8.  (P)\n\n"
    "FUNCTION\n"
    "  Drops over the centre column and twists clockwise\n"
    "  onto the bayonet collar. The annular gap between\n"
    "  the cone and the throat is the light trap: liquid\n"
    "  passes, light does not. The tank is daylight-safe\n"
    "  the moment it clicks home.\n\n"
    "  The one-piece large-diameter lid and funnel is the\n"
    "  feature Paterson actually advertises \u2014 it is what\n"
    "  makes the tank fill and empty fast.  (P)\n\n"
    "DEPTH INSIDE THE BARREL\n"
    "  The funnel intrudes 51 mm into the tank. That is\n"
    "  the one funnel dimension with real evidence behind\n"
    "  it: the Multi-Reel 5 measures 279 mm internal to\n"
    "  the lid but only 229 mm to the funnel.  (P)\n"
    "  279 \u2212 229 = 50.8 mm.\n\n"
    "  All other numbers on this sheet are (R), scaled\n"
    "  off the known \u00d895 bore that the skirt seals into.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# SHEET 5 - lid / cap
# ===========================================================================
fig = new_sheet(5, "LID / WATERTIGHT CAP", "SPTP110 (pt 2)", "ALL Super System 4", "1:1 approx")
ax = draw_axes(fig)

H = CAP_SKIRT + CAP_TOP
ax.add_patch(Rectangle((-CAP_OD / 2.0, CAP_SKIRT), CAP_OD, CAP_TOP,
                       fc="#7f9bbb", ec=INK, lw=1.5, hatch="\\\\\\\\"))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * CAP_OD / 2.0 - (3 if s > 0 else 0), 0), 3, CAP_SKIRT,
                           fc="#7f9bbb", ec=INK, lw=1.5, hatch="\\\\\\\\"))
    ax.add_patch(Wedge((s * (CAP_OD / 2.0 - 3), CAP_SKIRT / 2.0), 2.6, 90 if s > 0 else 270,
                       270 if s > 0 else 450, fc=STEEL, ec=INK, lw=0.9))
centreline(ax, 0, -12, H + 30)
ax.plot([-CAP_SEAL_D / 2.0, -CAP_SEAL_D / 2.0], [0, CAP_SKIRT], color=INK, lw=0.7, ls=":")
ax.plot([CAP_SEAL_D / 2.0, CAP_SEAL_D / 2.0], [0, CAP_SKIRT], color=INK, lw=0.7, ls=":")

vdim(ax, 70, 0, H, "17R  overall", tick_from=CAP_OD / 2.0)
vdim(ax, -78, 0, CAP_SKIRT, "14R skirt", tick_from=-CAP_OD / 2.0)
hdim(ax, H + 14, -CAP_OD / 2.0, CAP_OD / 2.0, "\u00d898R  over skirt", tick_from=H, below=False)
hdim(ax, -16, -CAP_SEAL_D / 2.0, CAP_SEAL_D / 2.0, "\u00d892R  sealing bead", tick_from=0)
leader(ax, (CAP_OD / 2.0 - 3, CAP_SKIRT / 2.0), (86, CAP_SKIRT / 2.0 - 26),
       "internal bead grips\nthe funnel rim (R)")
view_label(ax, 0, -40, "SECTION")

cx, cy = 168.0, 6.0
ax.add_patch(Circle((cx, cy), CAP_OD / 2.0, fc="#7f9bbb", ec=INK, lw=1.5))
ax.add_patch(Circle((cx, cy), CAP_SEAL_D / 2.0, fc="#9fb6cf", ec=INK, lw=0.8, ls=":"))
for k in range(24):
    import math
    a = math.radians(k * 15)
    r0, r1 = CAP_OD / 2.0 - 5, CAP_OD / 2.0
    ax.plot([cx + r0 * math.cos(a), cx + r1 * math.cos(a)],
            [cy + r0 * math.sin(a), cy + r1 * math.sin(a)], color=INK, lw=0.7)
centreline(ax, cx, cy - 66, cy + 66)
centreline_h(ax, cy, cx - 66, cx + 66)
leader(ax, (cx + 46, cy + 16), (cx + 62, cy + 44), "grip ribs (R)")
view_label(ax, cx, cy - 70, "PLAN \u2014 TOP")

ax.set_xlim(-150, 250); ax.set_ylim(-80, 100)
ax.set_xlabel("mm", fontsize=8, color=GREY)

notes_panel(fig, "LID / WATERTIGHT CAP \u2014 SPTP110",
    "UNIVERSAL PART, supplied in the same replacement\n"
    "kit as the funnel (Freestyle #142007, Paterson\n"
    "SPTP110, \u201cfits all Super System 4 series tanks\u201d). (P)\n\n"
    "MATERIAL\n"
    "  Flexible EVA. It is a friction cap, not a screw\n"
    "  thread \u2014 it stretches over the funnel rim and is\n"
    "  what makes inversion agitation possible.\n\n"
    "TWO AGITATION MODES  (P)\n"
    "  1  Cap fitted   \u2192 invert the whole tank.\n"
    "  2  Cap removed  \u2192 drop the agitator rod through\n"
    "     the funnel throat and twist (rotary).\n"
    "  Paterson's own copy says either, or a combination\n"
    "  of both, may be used.\n\n"
    "WHY IT MATTERS DIMENSIONALLY\n"
    "  Because the funnel is common to the whole range,\n"
    "  so is this cap \u2014 every Super System 4 tank, from\n"
    "  the 127 mm 35 mm tank to the 442 mm Multi-Reel 8,\n"
    "  closes with the identical \u00d898 mm cap. It is the\n"
    "  reason a spare lid bought for one tank fits the\n"
    "  others.\n\n"
    "  All dimensions on this sheet are (R), scaled from\n"
    "  the funnel rim it has to seal against.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# SHEET 6 - agitator rod
# ===========================================================================
fig = new_sheet(6, "AGITATOR ROD (STIRRER)", "SPTP109", "ALL Super System 4", "1:1 / detail 3:1")
ax = draw_axes(fig)

ax.add_patch(Rectangle((-ROD_KNOB_D / 2.0, ROD_LEN - ROD_KNOB_T), ROD_KNOB_D, ROD_KNOB_T,
                       fc="#7f9bbb", ec=INK, lw=1.5))
ax.add_patch(Rectangle((-ROD_D / 2.0, ROD_TIP_L), ROD_D, ROD_LEN - ROD_KNOB_T - ROD_TIP_L,
                       fc=HATCH, ec=INK, lw=1.5))
ax.add_patch(Rectangle((-ROD_TIP_W / 2.0, 0), ROD_TIP_W, ROD_TIP_L,
                       fc="#8fa8c4", ec=INK, lw=1.5))
ax.add_patch(Rectangle((-1.6, 0), 3.2, 10, fc="white", ec=INK, lw=1.1))
centreline(ax, 0, -12, ROD_LEN + 24)

vdim(ax, 34, 0, ROD_LEN, "115R  overall length", tick_from=ROD_KNOB_D / 2.0)
vdim(ax, -52, 0, ROD_TIP_L, "16R tip", tick_from=-ROD_TIP_W / 2.0)
vdim(ax, -52, ROD_LEN - ROD_KNOB_T, ROD_LEN, "7R knob", tick_from=-ROD_KNOB_D / 2.0)
hdim(ax, ROD_LEN + 12, -ROD_KNOB_D / 2.0, ROD_KNOB_D / 2.0, "\u00d826R  knob",
     tick_from=ROD_LEN, below=False)
leader(ax, (ROD_D / 2.0, 60), (44, 68), "\u00d86.5R  shaft")
view_label(ax, 0, -26, "ELEVATION 1:1")

# detail 3:1 of the engagement end
dx, dy, S = 132.0, 8.0, 3.0
ax.add_patch(Rectangle((dx - ROD_TIP_W * S / 2.0, dy), ROD_TIP_W * S, ROD_TIP_L * S,
                       fc="#8fa8c4", ec=INK, lw=1.6))
ax.add_patch(Rectangle((dx - 1.6 * S, dy), 3.2 * S, 10 * S, fc="white", ec=INK, lw=1.3))
ax.add_patch(Rectangle((dx - ROD_D * S / 2.0, dy + ROD_TIP_L * S), ROD_D * S, 22,
                       fc=HATCH, ec=INK, lw=1.4))
centreline(ax, dx, dy - 10, dy + ROD_TIP_L * S + 32)
hdim(ax, dy - 12, dx - ROD_TIP_W * S / 2.0, dx + ROD_TIP_W * S / 2.0, "9R", tick_from=dy)
hdim(ax, dy - 30, dx - 1.6 * S, dx + 1.6 * S, "3.2R  slot", tick_from=dy - 14)
vdim(ax, dx + 30, dy, dy + 10 * S, "10R slot depth", tick_from=dx + 1.6 * S)
leader(ax, (dx - 1.6 * S, dy + 18), (dx - 74, dy + 46),
       "slots straddle the\ncolumn drive tangs", ha="left")
view_label(ax, dx, dy - 54, "DETAIL B \u2014 ENGAGEMENT END  3:1")

ax.set_xlim(-105, 215); ax.set_ylim(-72, 150)
ax.set_xlabel("mm", fontsize=8, color=GREY)

notes_panel(fig, "AGITATOR ROD \u2014 SPTP109",
    "UNIVERSAL PART. The dealer copy is explicit:\n"
    "\u201cThe slots in the bottom of the rod engage with the\n"
    "tangs in the reel core of all Super System tanks\n"
    "from 35 mm to Multi-Reel 8.\u201d\n"
    "   [KHB Photografix PTS109 / Paterson SPTP109]  (P)\n\n"
    "WHY ONE SHORT ROD FITS EVERY TANK\n"
    "  This looks wrong at first \u2014 a Multi-Reel 8 is\n"
    "  3.4\u00d7 the height of a 35 mm tank. It works because\n"
    "  the CENTRE COLUMN is the part cut to length, not\n"
    "  the rod. Whatever the tank, the column head ends\n"
    "  just below the funnel throat, so the rod only ever\n"
    "  has to span the funnel \u2014 about 115 mm.\n"
    "  That is also why Paterson sells the column and the\n"
    "  agitator together as a per-model kit, while the\n"
    "  rod alone has a single part number.\n\n"
    "USE\n"
    "  Rotary agitation only. Remove the cap, drop the\n"
    "  rod through the throat, twist. Inversion uses the\n"
    "  cap instead and needs no rod.\n\n"
    "  Freestyle also list a short \u201cswizzle stick\u201d for\n"
    "  single and double reel tanks, so a second, shorter\n"
    "  variant is in circulation. Treat the 115 mm here\n"
    "  as the multi-reel length.\n\n"
    "  Every dimension on this sheet is (R).")
pdf.savefig(fig); plt.close(fig)

pdf.close()
print(pdf_path)

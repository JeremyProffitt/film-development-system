"""
Paterson Super System 4 Multi-Reel 3 (PTP116)
Fill and drain study: every route, with and without a bottom port.

12-sheet A3 landscape PDF.
"""

import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import (Rectangle, Circle, Polygon, FancyBboxPatch,
                                Wedge, Arc)

INK, GREY, DIMC = "#10243b", "#5b6b7d", "#b3261e"
C1, C2, C3, C4 = "#2f6fb5", "#c26a00", "#8a4fbd", "#0e8a5f"   # validated 4-slot
HATCH, MONO, SURF = "#a8bcd2", "monospace", "#fcfcfb"

# ---------------------------------------------------------------------------
# Geometry (mm) and hydraulic model
# ---------------------------------------------------------------------------
G = 9.81
A_TANK = 65.5e-4          # m^2   free plan area of a loaded MR3
Z_FILL = 0.141            # m     working depth to the funnel underside
R_THROAT = 18.0           # mm    funnel throat radius - the spill lip
Z_MM = 141.0              # mm    working depth
H_RES = 0.60              # m     default reservoir surface above tank floor
CD_BULK = 0.55            # bulkhead + valve + 0.5 m hose
CD_PIPE = 0.45            # long tube inside the centre column


def q_grav(d_mm, H, cd=CD_BULK):
    a = math.pi * (d_mm / 1000.0) ** 2 / 4.0
    return cd * a * math.sqrt(2 * G * H)


def fill_time(d_mm, H=H_RES, z=Z_FILL, cd=CD_BULK):
    a = math.pi * (d_mm / 1000.0) ** 2 / 4.0
    return (A_TANK / (cd * a * math.sqrt(2 * G))) * 2.0 * (math.sqrt(H) - math.sqrt(H - z))


def drain_time(d_mm, z=Z_FILL, cd=CD_BULK):
    a = math.pi * (d_mm / 1000.0) ** 2 / 4.0
    return (A_TANK / (cd * a)) * math.sqrt(2 * z / G)


def tilt_to_spill(z_mean_mm):
    return math.degrees(math.atan((Z_MM - z_mean_mm) / R_THROAT))


def max_level_at_tilt(theta_deg):
    return Z_MM - R_THROAT * math.tan(math.radians(theta_deg))


ROUTES = [
    ("1  Stock pour + invert",          None, None,     20.0, 15.0, "none"),
    ("2  Stock + 30\u00b0 tilt technique",   None, None,     10.0, 15.0, "none"),
    ("3  Funnel skirt port 1/2 in",     15.8, CD_BULK,  None, 15.0, "funnel"),
    ("4  Centre-column standpipe",      18.0, CD_PIPE,  None, None, "column"),
    ("5  Bottom bulkhead 1/2 in",       15.8, CD_BULK,  None, None, "TANK"),
    ("6  Bottom bulkhead 3/4 in",       20.9, CD_BULK,  None, None, "TANK"),
]


def route_times(r):
    _, d, cd, f, dr, _ = r
    return (f if f is not None else fill_time(d, cd=cd),
            dr if dr is not None else drain_time(d, cd=cd))


# ---------------------------------------------------------------------------
# Sheet framework
# ---------------------------------------------------------------------------
NSHEET = 15


def new_sheet(n, title, subtitle):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=150, facecolor="white")
    fig.patches.append(Rectangle((0.018, 0.018), 0.964, 0.964, transform=fig.transFigure,
                                 fill=False, ec=INK, lw=2.0, zorder=5))
    fig.patches.append(Rectangle((0.028, 0.028), 0.944, 0.944, transform=fig.transFigure,
                                 fill=False, ec=INK, lw=0.7, zorder=5))
    fig.text(0.045, 0.958, "PATERSON MULTI-REEL 3 (PTP116)  \u00b7  FILL & DRAIN STUDY",
             fontsize=10.5, color=GREY, family=MONO, va="center")
    fig.text(0.955, 0.958, f"SHEET {n} OF {NSHEET}", fontsize=10.5, color=GREY,
             family=MONO, va="center", ha="right")
    fig.lines.append(plt.Line2D([0.045, 0.955], [0.945, 0.945],
                                transform=fig.transFigure, color=INK, lw=0.7))
    fig.text(0.045, 0.915, title, fontsize=17, fontweight="bold", color=INK, va="center")
    fig.text(0.045, 0.886, subtitle, fontsize=10.5, color=GREY, family=MONO, va="center")
    fig.text(0.045, 0.032, "Hydraulics computed from the PTP116 drawing set. Tank "
                           "dimensions are a reconstruction \u2014 verify with calipers "
                           "before drilling, printing or buying fittings.",
             fontsize=7.8, color=GREY, family=MONO, va="bottom")
    return fig


def body(fig, x, y, text, fs=9.4, color=INK, weight="normal"):
    return fig.text(x, y, text, fontsize=fs, color=color, family=MONO,
                    va="top", linespacing=1.55, fontweight=weight)


def head(fig, x, y, text, fs=11.5, color=INK):
    return fig.text(x, y, text, fontsize=fs, fontweight="bold", color=color,
                    family=MONO, va="top")


def callout(fig, x, y, w, h, text, accent=C1, fs=9.6, title=None):
    fig.patches.append(FancyBboxPatch((x, y), w, h, transform=fig.transFigure,
                                      boxstyle="round,pad=0.006,rounding_size=0.008",
                                      fc="#f2f6fb", ec=accent, lw=1.8, zorder=4))
    ty = y + h - 0.022
    if title:
        fig.text(x + 0.014, ty, title, fontsize=10.5, fontweight="bold",
                 color=accent, family=MONO, va="top", zorder=6)
        ty -= 0.030
    fig.text(x + 0.014, ty, text, fontsize=fs, color=INK, family=MONO,
             va="top", linespacing=1.5, zorder=6)


def table(ax, cells, cols, bbox, highlight=None, colcolor=None, fs=8.8,
          rowcolor=None, colw=None):
    t = ax.table(cellText=cells, colLabels=cols, cellLoc="center", bbox=bbox)
    t.auto_set_font_size(False); t.set_fontsize(fs)
    for (r, c), cl in t.get_celld().items():
        cl.set_edgecolor("#8fa3b8"); cl.set_linewidth(0.8)
        if colw:
            cl.set_width(colw[c])
        if r == 0:
            cl.set_facecolor(INK)
            cl.set_text_props(color="white", fontweight="bold", fontsize=fs - 0.5)
        else:
            cl.set_facecolor("#f4f7fb" if r % 2 else "white")
            if rowcolor and r in rowcolor:
                cl.set_facecolor(rowcolor[r])
            if highlight is not None and r == highlight:
                cl.set_facecolor("#dce8f7"); cl.set_text_props(fontweight="bold")
            if colcolor and c in colcolor:
                cl.set_text_props(color=colcolor[c], fontweight="bold")
    return t


def tank_outline(ax, fill_to=None, reels=True, x0=0.0):
    ax.add_patch(Rectangle((x0 - 51, 0), 102, 199, fc="none", ec=INK, lw=1.5))
    ax.add_patch(Rectangle((x0 - 47.5, 7), 95, 192, fc="white", ec=INK, lw=0.9))
    if fill_to:
        ax.add_patch(Rectangle((x0 - 47.5, 7), 95, fill_to - 7, fc="#dce8f7", ec="none"))
    if reels:
        for i in range(3):
            ax.add_patch(Rectangle((x0 - 46, 7 + i * 44), 92, 42, fc="none",
                                   ec=C1, lw=0.8, ls="--"))
    ax.add_patch(Rectangle((x0 - 12.5, 7), 25, 185, fc="#eef3f9", ec=INK, lw=0.9))
    ax.add_patch(Polygon([(x0 - 47.5, 192), (x0 + 47.5, 192), (x0 + 18, 148),
                          (x0 - 18, 148)], closed=True, fc="#eef3f9", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((x0 - 55, 192), 110, 8, fc="#cfdceb", ec=INK, lw=1.2))


out = "fill_and_drain_study.pdf"
pdf = PdfPages(out)

# ===========================================================================
# 1  SUMMARY
# ===========================================================================
fig = new_sheet(1, "Every route, ranked", "fill and drain, with and without a bottom port")

rows, rowcol = [], {}
for i, r in enumerate(ROUTES, start=1):
    f, d = route_times(r)
    rows.append([r[0], f"{f:.1f} s", f"{d:.1f} s", r[5]])
    if r[5] == "TANK":
        rowcol[i] = "#f8ece6"
rows.append(["7  Route 4 or 5 + recirculating pump", "as above", "as above", "as above"])
rows.append(["8  Motorised tilt cradle", "10.0 s", "12.0 s", "none"])

axt = fig.add_axes([0.045, 0.545, 0.60, 0.30]); axt.axis("off")
table(axt, rows, ["Route", "Fill", "Drain", "Cuts into"], [0, 0.0, 1.0, 1.0],
      highlight=4, colcolor={1: C1, 2: C2}, rowcolor=rowcol,
      colw=[0.45, 0.17, 0.17, 0.21])

callout(fig, 0.045, 0.305, 0.60, 0.215, accent=C4,
        title="THE RESULT THAT MATTERS",
        text="Route 4 \u2014 a printed replacement centre column with an \u00f818 mm through\n"
             "bore, open at the foot \u2014 gives 2.5 s fill and 9.7 s drain. That is\n"
             "bulkhead performance, from the bottom of the tank, with ZERO holes in\n"
             "the tank. The column is a cheap consumable spare; the tank is not.\n\n"
             "If you were going to drill the tank for a 1/2 in port, print a column\n"
             "instead. It is faster, it is reversible, it cannot leak onto your\n"
             "bench, and it is light-tight almost by accident \u2014 the feed runs down\n"
             "a black tube inside a black tube.")

head(fig, 0.045, 0.285, "AND THE ONE THAT SURPRISES PEOPLE")
body(fig, 0.045, 0.252,
     "Gravity beats every affordable pump. 0.6 m of head through a 1/2 in line\n"
     "delivers 370 ml/s \u2014 22 litres a minute. A cheap diaphragm pump manages\n"
     "4\u20137 L/min; a small peristaltic manages 0.5\u20133, slower than the stock funnel\n"
     "you are trying to escape. You would need a 22 L/min chemical-proof pump to\n"
     "match a shelf 600 mm above the bench.\n\n"
     "Pumps are not for filling. They are for recirculating \u2014 4 L/min is ample for\n"
     "continuous agitation \u2014 and for pulling the last residue out of the reels.",
     fs=9.2)

head(fig, 0.675, 0.845, "ANSWERS TO THE FOUR QUESTIONS")
body(fig, 0.675, 0.812,
     "WITH A BOTTOM VALVE\n"
     "  Gravity fill from a raised reservoir, gravity\n"
     "  drain to a bucket below the bench. Do not pump\n"
     "  either direction. 1/2 in, not 3/4 in. Sheets\n"
     "  9 and 10.\n\n"
     "WITHOUT A BOTTOM VALVE\n"
     "  Centre-column standpipe (route 4) if you will\n"
     "  print a part; 30\u00b0 tilt pouring (route 2) if you\n"
     "  will not. Sheets 8 and 4.\n\n"
     "PLUMBING IN AND OUT INSIDE THE FUNNEL\n"
     "  Two ways, and they are not equivalent. A port\n"
     "  through the funnel SKIRT is a fast top fill and\n"
     "  no drain at all. A tube down the CENTRE COLUMN\n"
     "  is a fast bottom fill and a fast drain. Take the\n"
     "  second. Sheets 7 and 8.\n\n"
     "TILTING\n"
     "  Fill: 25\u201330\u00b0 from vertical, and it keeps working\n"
     "  until the tank is 93 % full. Worth about 2\u00d7.\n"
     "  Drain: the geometry demands 83\u00b0 to empty and\n"
     "  full inversion to clear the reels. Tilt is a\n"
     "  filling tool, not a draining one. Sheets 4\u20136.",
     fs=9.2)
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 2  BASELINE
# ===========================================================================
fig = new_sheet(2, "Baseline \u2014 why the standard tank is slow",
                "one opening, two fluids, opposite directions")
ax = fig.add_axes([0.045, 0.10, 0.36, 0.755]); ax.set_aspect("equal"); ax.axis("off")
tank_outline(ax, fill_to=141)
ax.annotate("", (-9, 150), (-26, 232), arrowprops=dict(arrowstyle="-|>", color=C1,
            lw=2.6, connectionstyle="arc3,rad=0.2"))
ax.text(-30, 240, "chemistry DOWN", color=C1, family=MONO, fontsize=9.2,
        ha="center", va="bottom", fontweight="bold")
ax.annotate("", (26, 232), (9, 150), arrowprops=dict(arrowstyle="-|>", color=C2,
            lw=2.6, connectionstyle="arc3,rad=0.2"))
ax.text(34, 240, "air UP", color=C2, family=MONO, fontsize=9.2,
        ha="center", va="bottom", fontweight="bold")
ax.plot([-18, 18], [148, 148], color=DIMC, lw=1.6)
ax.annotate("\u00d836 throat \u2014 shared by\nboth flows, so it behaves\nlike a \u00d810 orifice",
            (-14, 148), (-112, 118), color=DIMC, family=MONO, fontsize=8.6,
            va="center", arrowprops=dict(arrowstyle="->", color=DIMC, lw=1.0))
ax.text(0, 70, "1000 ml\n141 mm deep\n65.5 cm\u00b2 plan area", ha="center", va="center",
        family=MONO, fontsize=9, color=INK,
        bbox=dict(fc="white", ec="#8fa3b8", lw=0.7, alpha=0.9, pad=3))
ax.set_xlim(-115, 115); ax.set_ylim(-14, 275)

head(fig, 0.44, 0.845, "THE MEASUREMENT EVERYTHING IS ANCHORED TO")
body(fig, 0.44, 0.812,
     "A Multi-Reel 3 takes 15\u201325 s to accept 1000 ml through\n"
     "the funnel. Call it 20 s \u2192 50 ml/s. Back out the\n"
     "effective orifice:\n\n"
     "    head in the funnel      h  \u2248 0.05 m\n"
     "    ideal velocity      \u221a(2gh) = 0.99 m/s\n"
     "    with Cd 0.6             v  = 0.60 m/s\n"
     "    area needed         A = Q/v = 83 mm\u00b2\n"
     "    equivalent bore            \u00f810.3 mm\n\n"
     "A \u00d836 throat performing like a \u00d810 hole. The missing\n"
     "92 % of the area is occupied by air trying to get out.\n"
     "That is the entire problem, and every route in this\n"
     "document is a different way of giving the air its own\n"
     "way out.", fs=9.2)

head(fig, 0.44, 0.545, "COUNTER-CURRENT FLOODING — THE GOVERNING PHYSICS")
body(fig, 0.44, 0.512,
     "Liquid down and gas up in one vertical tube is a classic\n"
     "flooding problem. The Wallis criterion,\n\n"
     "      √j*_g  +  m · √j*_l   =   C\n"
     "      j*_k = j_k · √( ρ_k / (g D Δρ) )\n\n"
     "says the tube jams once the two superficial velocities\n"
     "together exceed a constant. Below the limit you get smooth\n"
     "stratified flow; above it, slug flow — the glugging you\n"
     "can hear. Two levers fall straight out of it:\n\n"
     "  • raise D           → a bigger path (routes 3–6)\n"
     "  • incline the tube  → gravity separates the phases\n"
     "                        instead of making them fight\n\n"
     "Everything in this document is one of those two.", fs=9.2)

callout(fig, 0.44, 0.062, 0.515, 0.20, accent=C2, fs=9.4,
        title="WHEN THIS ACTUALLY MATTERS",
        text="Development starts when the first film meets developer, so a\n"
             "20 s fill means the bottom reel develops 20 s longer than the\n"
             "top one.\n\n"
             "  at 9 min   20 s is 3.7 %   invisible\n"
             "  at 6 min   20 s is 5.6 %   borderline\n"
             "  at 3 min   20 s is 11 %    a visible density gradient\n\n"
             "Below about 4 minutes, no pouring technique is good enough.\n"
             "That threshold should decide whether you build any of this.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 3  OPTIONS MAP
# ===========================================================================
fig = new_sheet(3, "The six physical routes",
                "where the liquid goes in, and where the air it displaces comes out")
ax = fig.add_axes([0.045, 0.345, 0.91, 0.515]); ax.set_aspect("equal"); ax.axis("off")

names = ["1  STOCK", "2  TILT 30\u00b0", "3  SKIRT PORT", "4  STANDPIPE",
         "5  BULKHEAD 1/2", "6  BULKHEAD 3/4"]
accents = [GREY, C3, C2, C4, C1, C1]
for i, (nm, acc) in enumerate(zip(names, accents)):
    x0 = i * 182.0
    tank_outline(ax, fill_to=141, x0=x0)
    ax.text(x0, -34, nm, ha="center", va="top", fontsize=9.2, family=MONO,
            fontweight="bold", color=acc)
    if i == 0:
        ax.annotate("", (x0 - 6, 152), (x0 - 20, 228),
                    arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.2))
        ax.annotate("", (x0 + 22, 228), (x0 + 8, 152),
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2))
        ax.text(x0, -50, "in and out fight\nover one hole", ha="center", va="top", fontsize=8,
                family=MONO, color=GREY)
    if i == 1:
        ax.annotate("", (x0 - 8, 152), (x0 - 32, 218),
                    arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.2))
        ax.annotate("", (x0 + 26, 224), (x0 + 8, 152),
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2))
        ax.add_patch(Arc((x0, 100), 156, 156, theta1=62, theta2=90, color=C3, lw=1.8))
        ax.text(x0 + 66, 190, "30\u00b0", fontsize=9, family=MONO, color=C3,
                fontweight="bold")
        ax.text(x0, -50, "gravity splits the\ntwo flows apart", ha="center", va="top", fontsize=8,
                family=MONO, color=GREY)
    if i == 2:
        ax.add_patch(Rectangle((x0 + 47, 168), 30, 12, fc=C2, ec=INK, lw=1.0))
        ax.annotate("", (x0 + 44, 174), (x0 + 106, 174),
                    arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.4))
        ax.annotate("", (x0 + 4, 244), (x0 + 4, 154),
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2))
        ax.text(x0, -50, "fast top fill,\nno drain", ha="center", va="top", fontsize=8,
                family=MONO, color=GREY)
    if i == 3:
        ax.add_patch(Rectangle((x0 - 7, 12), 14, 182, fc="#d8f0e4", ec=C4, lw=1.6))
        ax.annotate("", (x0, 20), (x0, 246), arrowprops=dict(arrowstyle="-|>",
                    color=C1, lw=2.4))
        ax.annotate("", (x0 + 34, 240), (x0 + 20, 152),
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.0))
        ax.text(x0, -50, "bottom fill AND\nbottom drain,\nno holes", ha="center", va="top",
                fontsize=8, family=MONO, color=C4, fontweight="bold")
    if i in (4, 5):
        w = 16 if i == 4 else 22
        ax.add_patch(Rectangle((x0 - w / 2, -32), w, 34, fc="#dce8f7", ec=C1, lw=1.6))
        ax.annotate("", (x0, 4), (x0, -28), arrowprops=dict(arrowstyle="-|>",
                    color=C1, lw=2.4))
        ax.annotate("", (x0 + 32, 240), (x0 + 18, 152),
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.0))
        ax.text(x0, -50, "drilled tank" + ("" if i == 4 else "\nloses a reel"),
                ha="center", va="top", fontsize=8, family=MONO,
                color=DIMC if i == 5 else GREY)
ax.set_xlim(-108, 5 * 182 + 108); ax.set_ylim(-92, 262)

head(fig, 0.045, 0.285, "READING THE MAP")
body(fig, 0.045, 0.252,
     "Blue arrows are chemistry, orange arrows are the air it displaces. A route is FAST exactly when the two arrows do not share a\n"
     "hole, and it is EVEN when the blue arrow enters at the bottom, so the liquid front rises through the reels pushing the air ahead\n"
     "of it. Routes 4, 5 and 6 do both. Route 3 separates the flows but still pours onto the top reel. Routes 1 and 2 do neither \u2014\n"
     "route 2 simply makes the shared hole behave better by tipping it.", fs=9.4)

callout(fig, 0.045, 0.062, 0.44, 0.112, accent=C4,
        title="ONLY TWO ROUTES DRAIN FROM THE BOTTOM",
        text="Route 4, and routes 5/6. Everything else drains by turning\n"
             "the tank upside down, because the reels leave only ~1.5 mm\n"
             "of radial clearance \u2014 no dip tube can run down the wall.")
callout(fig, 0.515, 0.062, 0.44, 0.112, accent=C2,
        title="ROUTE 3 IS A HALF-MEASURE",
        text="It buys the full fill speed and none of the drain speed or\n"
             "evenness. Worth it only if you refuse to touch the centre\n"
             "column. Sheet 7.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 4  TILT FOR FILLING
# ===========================================================================
fig = new_sheet(4, "Tilting to fill \u2014 how far, and how far it gets you",
                "the throat floods from the inside only when the tank is nearly full")

ax = fig.add_axes([0.055, 0.335, 0.40, 0.49], facecolor=SURF)
th = [t * 0.5 for t in range(0, 121)]
ax.plot(th, [max_level_at_tilt(t) / Z_MM * 100 for t in th], color=C3, lw=2.2)
for t in (10, 20, 30, 40, 50, 60):
    y = max_level_at_tilt(t) / Z_MM * 100
    ax.plot([t], [y], "o", ms=8.5, color=C3, mec="white", mew=1.8, zorder=6)
    ax.annotate(f"{y:.0f} %", (t, y), (t, y + 3.0), ha="center", fontsize=8.8,
                color=INK, family=MONO)
ax.axvspan(25, 30, color="#ece4f6", zorder=0)
ax.text(27.5, 26, "useful\nband", ha="center", fontsize=9, color=C3, family=MONO,
        fontweight="bold")
ax.set_xlim(0, 60); ax.set_ylim(22, 106)
ax.set_xlabel("tilt from vertical   degrees", fontsize=10, color=INK)
ax.set_ylabel("fill level when the throat floods   %", fontsize=9.6, color=INK)
ax.set_title("Tilt stays usable almost to the top", fontsize=9.6, color=GREY,
             loc="left", pad=8)
ax.grid(True, color="#dfe6ee", lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#8fa3b8")
ax.tick_params(colors=GREY, labelsize=9)

axd = fig.add_axes([0.055, 0.075, 0.40, 0.20]); axd.set_aspect("equal"); axd.axis("off")
for k, (t, lab) in enumerate(((0, "0\u00b0  glugs"), (30, "30\u00b0  smooth"),
                              (50, "50\u00b0  pools in cone"))):
    x0 = k * 134
    tr = matplotlib.transforms.Affine2D().rotate_deg(-t).translate(x0, 0) + axd.transData
    axd.add_patch(Rectangle((-24, 0), 48, 96, fc="#eef3f9", ec=INK, lw=1.3, transform=tr))
    axd.add_patch(Rectangle((-24, 0), 48, 64, fc="#dce8f7", ec="none", transform=tr))
    axd.add_patch(Polygon([(-24, 96), (24, 96), (9, 74), (-9, 74)], closed=True,
                          fc="#cfdceb", ec=INK, lw=1.1, transform=tr))
    axd.text(x0, -22, lab, ha="center", fontsize=9, family=MONO, color=INK)
axd.set_xlim(-78, 360); axd.set_ylim(-44, 118)

head(fig, 0.49, 0.845, "WHY TILTING WORKS")
body(fig, 0.49, 0.812,
     "Upright, the throat is one vertical pipe carrying liquid\n"
     "down and air up at the same time. The phases fight, the\n"
     "flow goes to slug flow, and it burps.\n\n"
     "Tilt it and gravity stratifies them: liquid runs down the\n"
     "low side of the throat, air escapes along the high side.\n"
     "You have made two channels out of one without touching the\n"
     "tank \u2014 in flooding terms, you have raised C.\n\n"
     "Effect in practice: roughly 20 s \u2192 10 s. About 2\u00d7, which\n"
     "matches the 1.5\u20132.5\u00d7 that inclining a counter-current\n"
     "tube is generally worth.", fs=9.2)

head(fig, 0.49, 0.585, "WHY 25–30° AND NOT MORE")
body(fig, 0.49, 0.552,
     "Two limits close in from opposite sides. BELOW ~20°\n"
     "stratification is incomplete and the flow still slugs\n"
     "intermittently. ABOVE ~35° chemistry pools in the funnel\n"
     "cone instead of draining through the throat, and the cone\n"
     "becomes the restriction instead.\n\n"
     "What does NOT stop you is flooding from the inside. With\n"
     "the tank tilted θ the liquid climbs the low wall and\n"
     "reaches the throat lip when\n\n"
     "     z_mean  +  r_throat · tanθ   >   141 mm\n\n"
     "At 30° that is 130.6 mm — 93 % full, so you can hold the\n"
     "tilt through almost the whole pour and only bring the\n"
     "tank upright for the last splash.", fs=9.2)

callout(fig, 0.49, 0.070, 0.465, 0.225, accent=C3, fs=9.4,
        title="THE TECHNIQUE, WRITTEN OUT",
        text="1  Start at 25–30°, throat low-side down, jug spout\n"
             "   20–30 mm clear of the opening — never sealing it.\n"
             "2  Pour steadily against the low wall of the cone.\n"
             "3  At about 90 % — you will feel it slow — bring the\n"
             "   tank upright and let the last 100 ml settle in.\n"
             "4  Cap, then start the timer at the HALFWAY point of\n"
             "   the pour, not the end. That halves the residual\n"
             "   error for nothing.\n\n"
             "Free, reversible, and it works on every tank in the range.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 5  TILT FOR DRAINING
# ===========================================================================
fig = new_sheet(5, "Tilting to drain \u2014 the geometry says no",
                "you cannot pour this tank empty without very nearly inverting it")

ax = fig.add_axes([0.055, 0.30, 0.41, 0.525], facecolor=SURF)
vols = list(range(0, 101))
ax.plot(vols, [tilt_to_spill(Z_MM * v / 100.0) for v in vols], color=C2, lw=2.2)
for v in (100, 90, 75, 50, 25, 10, 0):
    a = tilt_to_spill(Z_MM * v / 100.0)
    ax.plot([v], [a], "o", ms=8.5, color=C2, mec="white", mew=1.8, zorder=6)
    lx, ly = (v - 6, a + 3.5) if v > 92 else (v + 2.5, a - 4.0)
    ax.annotate(f"{a:.0f}\u00b0", (v, a), (lx, ly), fontsize=8.8,
                color=INK, family=MONO)
ax.axhspan(75, 90, color="#f8ece6", zorder=0)
ax.text(52, 86, "practically on its side", fontsize=9, color=C2, family=MONO,
        ha="center", fontweight="bold")
ax.set_xlim(0, 102); ax.set_ylim(0, 92)
ax.set_xlabel("liquid remaining in the tank   %", fontsize=10, color=INK)
ax.set_ylabel("tilt from vertical needed to keep pouring   degrees",
              fontsize=9.4, color=INK)
ax.set_title("\u03b8 = arctan( (141 \u2212 z_mean) / 18 )", fontsize=9.6, color=GREY,
             loc="left", pad=8)
ax.grid(True, color="#dfe6ee", lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#8fa3b8")
ax.tick_params(colors=GREY, labelsize=9)

head(fig, 0.50, 0.845, "THE DERIVATION")
body(fig, 0.50, 0.812,
     "Tilt the tank by θ. The free surface stays horizontal, so\n"
     "in the tank’s own frame it is a plane inclined at θ and\n"
     "the liquid climbs the low wall by r·tanθ. It can leave\n"
     "only over the throat lip, 141 mm up the axis and 18 mm\n"
     "out from it, so it pours once the surface covers that lip:\n\n"
     "     z_mean  +  18 · tanθ   >   141\n"
     "     θ  >  arctan( (141 − z_mean) / 18 )\n\n"
     "  full        z=141   θ =  0°   spills at once\n"
     "  90 % left   z=127   θ = 38°\n"
     "  75 % left   z=106   θ = 63°\n"
     "  50 % left   z= 71   θ = 76°\n"
     "  25 % left   z= 35   θ = 80°\n"
     "  bone dry    z=  0   θ = 83°\n\n"
     "The 18 mm throat radius is the villain. Even if the whole\n"
     "ø95 bore could discharge, the last drop would still need\n"
     "arctan(141/47.5) = 71°.", fs=9.2)

head(fig, 0.50, 0.505, "AND THE CURVE UNDERSTATES IT")
body(fig, 0.50, 0.472,
     "That model is an open cylinder. The real tank adds three\n"
     "things it does not capture:\n\n"
     "  • the funnel cone is in the way and traps a pocket on\n"
     "    the high side;\n"
     "  • surface tension holds 20–40 ml in the reel spirals at\n"
     "    any angle — only a shake clears it;\n"
     "  • air has to come back IN as liquid leaves, so the\n"
     "    counter-current fight from sheet 2 applies in reverse\n"
     "    and it glugs the whole way down.\n\n"
     "This is why Paterson’s own instruction is to invert. It is\n"
     "not laziness — it is the only angle that works.", fs=9.2)

callout(fig, 0.50, 0.062, 0.455, 0.185, accent=C2, fs=9.2,
        title="CONCLUSION ON TILT",
        text="Tilt is a FILLING tool. It roughly halves the fill time\n"
             "and costs nothing.\n\n"
             "It is not a draining tool. Anything short of 80° leaves a\n"
             "quarter of your chemistry in the tank, and a partial tilt\n"
             "that dribbles for 30 s is worse for evenness than a clean\n"
             "15 s inversion. For a fast drain you need a bottom path —\n"
             "route 4, 5 or 6.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 6  AUTOMATIC TILT
# ===========================================================================
fig = new_sheet(6, "Doing the tilting automatically",
                "a three-position cradle \u2014 and why it is really an agitation machine")

ax = fig.add_axes([0.045, 0.32, 0.42, 0.51]); ax.set_aspect("equal"); ax.axis("off")
for k, (t, lab, col) in enumerate(((30, "FILL\n30\u00b0", C3),
                                   (0, "PROCESS\n0\u00b0 \u00b1 inversion", C1),
                                   (150, "DRAIN\n150\u00b0", C2))):
    x0 = k * 165
    tr = matplotlib.transforms.Affine2D().rotate_deg(-t).translate(x0, 40) + ax.transData
    ax.add_patch(Rectangle((-26, -48), 52, 100, fc="#eef3f9", ec=INK, lw=1.4,
                           transform=tr))
    ax.add_patch(Polygon([(-26, 52), (26, 52), (10, 30), (-10, 30)], closed=True,
                         fc="#cfdceb", ec=INK, lw=1.1, transform=tr))
    ax.plot([x0], [40], "o", ms=10, color=INK, zorder=8)
    ax.text(x0, -54, lab, ha="center", fontsize=9.2, family=MONO, fontweight="bold",
            color=col)
    ax.plot([x0 - 46, x0 + 46], [-30, -30], color=GREY, lw=2.2)
ax.text(165, -86, "pivot through the tank axis at its loaded centre of mass\n"
                  "\u2192 near-zero torque; a hobby servo is enough",
        ha="center", fontsize=8.6, family=MONO, color=GREY)
ax.set_xlim(-86, 420); ax.set_ylim(-100, 150)

head(fig, 0.50, 0.845, "SPECIFICATION")
body(fig, 0.50, 0.812,
     "PIVOT       through the tank axis at 100 mm up \u2014 the loaded\n"
     "            centre of mass. Balanced, so the motor only\n"
     "            fights friction.\n"
     "TORQUE      1.5 kg at 15 mm worst-case offset \u2248 0.22 N\u00b7m.\n"
     "            A 20 kg\u00b7cm hobby servo is four times that.\n"
     "STOPS       30\u00b0 fill \u00b7 0\u00b0 process \u00b7 150\u2013180\u00b0 drain.\n"
     "ROTATION    continuous 180\u00b0 for inversion agitation, one or\n"
     "            two inversions per 10 s with a dwell at each end.\n"
     "CRADLE      two printed saddles on \u00f8102, one M6 rod, a strap\n"
     "            over the lid. The lid MUST be strapped \u2014 an EVA\n"
     "            cap will let go at 180\u00b0 under load.\n"
     "CONTROL     three-position cam, or a servo with three preset\n"
     "            angles and a cheap microcontroller.", fs=9.2)

head(fig, 0.50, 0.575, "BE HONEST ABOUT WHAT IT BUYS")
body(fig, 0.50, 0.542,
     "FILLING     30\u00b0 held perfectly still is worth maybe a second\n"
     "            over doing it by hand. Not the reason to build it.\n\n"
     "DRAINING    A motorised 150\u00b0 dump genuinely beats hand\n"
     "            inversion \u2014 repeatable, and it frees both hands.\n"
     "            About 12 s, every time.\n\n"
     "AGITATION   This is the real prize. An identical inversion\n"
     "            pattern every run, every roll, forever. The\n"
     "            largest source of run-to-run variation in hand\n"
     "            processing is agitation, not fill time.\n\n"
     "TEMPERATURE The cradle can sit in a water bath. Add a\n"
     "            recirculating pump and you have built a Jobo.", fs=9.2)

callout(fig, 0.045, 0.080, 0.91, 0.19, accent=C3,
        title="HOW IT COMBINES WITH THE OTHER ROUTES",
        text="A tilt cradle and a bottom path are not alternatives \u2014 they solve different halves of the problem, and the best machine has both.\n\n"
             "  cradle alone            10 s fill \u00b7 12 s drain \u00b7 perfect agitation \u00b7 no plumbing and no holes\n"
             "  column standpipe alone  2.5 s fill \u00b7 9.7 s drain \u00b7 hand agitation \u00b7 one printed part\n"
             "  both                    2.5 s fill \u00b7 9.7 s drain \u00b7 perfect agitation \u2014 but the feed hose must release before the cradle inverts,\n"
             "                          which is exactly what the quick-disconnect on sheet 12 is for.\n\n"
             "If you build one thing, build the standpipe. If you build two, add the cradle \u2014 for the agitation, not for the tilting.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 7  FUNNEL SKIRT PORT
# ===========================================================================
fig = new_sheet(7, "Plumbing through the funnel \u2014 the skirt port",
                "drill the cheap universal spare, not the tank")

ax = fig.add_axes([0.045, 0.315, 0.40, 0.51]); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((-55, 0), 110, 6, fc=HATCH, ec=INK, lw=1.4, hatch="////"))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * 47 - (2.5 if s > 0 else 0), -12), 2.5, 12,
                           fc=HATCH, ec=INK, lw=1.3, hatch="////"))
    ax.add_patch(Polygon([(s * 47, -12), (s * 44.5, -12), (s * 17.5, -46),
                          (s * 20, -46)], closed=True, fc=HATCH, ec=INK, lw=1.3))
ax.add_patch(Rectangle((47, -10), 34, 9, fc=C2, ec=INK, lw=1.3))
ax.text(84, -5.5, "1/2 in barb\nthrough the skirt", fontsize=8.6, family=MONO,
        color=C2, va="center")
ax.annotate("", (44, -5.5), (110, -5.5), arrowprops=dict(arrowstyle="<|-", color=C1, lw=2.6))
ax.annotate("", (0, 54), (0, -40), arrowprops=dict(arrowstyle="<|-", color=C2, lw=2.4))
ax.text(5, 42, "throat becomes a\ndedicated VENT", fontsize=8.8, family=MONO, color=C2)
ax.add_patch(Rectangle((-44, -26), 88, 5, fc="#dce8f7", ec=C1, lw=1.2))
ax.annotate("diffuser ring spreads\nthe jet round the wall", (-30, -23.5),
            (-118, -44), fontsize=8.2, family=MONO, color=C1, va="center",
            arrowprops=dict(arrowstyle="->", color=C1, lw=0.9))
ax.plot([-62, 62], [-72, -72], color=C1, lw=1.6, ls=":")
ax.text(-62, -78, "liquid level 141 \u2014 the port discharges ABOVE it",
        fontsize=8.4, family=MONO, color=GREY, va="top")
ax.text(0, 68, "FUNNEL SECTION", ha="center", fontsize=9.6, family=MONO,
        fontweight="bold", color=INK)
ax.set_xlim(-124, 156); ax.set_ylim(-98, 84)

head(fig, 0.49, 0.845, "THE IDEA")
body(fig, 0.49, 0.812,
     "The funnel and lid are a universal spare \u2014 SPTP110, sold\n"
     "for about the price of a roll of film and fitting every\n"
     "tank in the range. So modify that instead of the tank.\n"
     "Buy two: one stock, one drilled. Swap back in thirty\n"
     "seconds; sell the tank on unmarked.\n\n"
     "Fit a 1/2 in barb through the SKIRT \u2014 the cylindrical part\n"
     "that seals into the \u00f895 bore \u2014 so it discharges below the\n"
     "light trap, straight into the tank. The throat above then\n"
     "carries nothing but air.\n\n"
     "That is the whole trick: you have not made the hole bigger,\n"
     "you have given the air its own hole.", fs=9.2)

head(fig, 0.49, 0.600, "WHAT IT DELIVERS")
body(fig, 0.49, 0.567,
     "  fill   2.7 s   identical to a 1/2 in bottom bulkhead\n"
     "  drain  15 s    unchanged, still by inversion\n"
     "  tank   untouched\n\n"
     "The fill figure is real: once the vent is separate, the\n"
     "port is the only restriction left, so it obeys the same\n"
     "gravity equation as any other 1/2 in line.", fs=9.2)

head(fig, 0.49, 0.450, "THE TWO CATCHES")
body(fig, 0.49, 0.417,
     "1  IT IS STILL A TOP FILL. Chemistry lands on the top reel\n"
     "   and works down. You get the speed but not the even\n"
     "   rising front a bottom feed gives, and a bare jet will\n"
     "   hammer the top film — hence the diffuser ring.\n"
     "2  IT DOES NOTHING FOR DRAINING. The reels leave only\n"
     "   about 1.5 mm of radial clearance against the bore, so\n"
     "   no dip tube can reach the floor down the wall.\n\n"
     "A hole in the skirt is a straight line to the film. Trap\n"
     "it exactly like a bulkhead: opaque hose, 300 mm, one 90°\n"
     "bend, and test it per sheet 12.", fs=9.2)

callout(fig, 0.045, 0.062, 0.40, 0.175, accent=C2, fs=9.2,
        title="VERDICT ON THE SKIRT PORT",
        text="Half the benefit for a quarter of the nerve. Take it if\n"
             "you will not modify the centre column and you only care\n"
             "about fill speed — for instance if your problem is a\n"
             "3-minute push and your drain already overlaps a rinse.\n\n"
             "Otherwise go straight to the standpipe on the next\n"
             "sheet. It costs the same effort and does both jobs.")
callout(fig, 0.49, 0.062, 0.465, 0.175, accent=C4, fs=9.2,
        title="A NOTE ON VENT SIZING",
        text="The vent must pass air at the same volumetric rate the\n"
             "liquid arrives — 370 ml/s at 0.6 m of head. Through the\n"
             "ø36 throat that is 0.36 m/s of air and a pressure drop\n"
             "well under 1 Pa. Air is a thousand times lighter than\n"
             "developer; venting is never the limit once it has a\n"
             "path of its own. Leave the throat stock.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 8  COLUMN STANDPIPE
# ===========================================================================
fig = new_sheet(8, "The centre-column standpipe \u2014 best route overall",
                "bottom fill and bottom drain, and not one hole in the tank")

ax = fig.add_axes([0.045, 0.22, 0.29, 0.63]); ax.set_aspect("equal"); ax.axis("off")
tank_outline(ax, fill_to=141)
ax.add_patch(Rectangle((-9, 10), 18, 184, fc="#d8f0e4", ec=C4, lw=1.8))
ax.add_patch(Rectangle((-23, 7), 46, 5, fc="#cfdceb", ec=INK, lw=1.2))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * 9, 9), s * 12, 4, fc=C4, ec=INK, lw=0.9))
ax.annotate("", (0, 16), (0, 252), arrowprops=dict(arrowstyle="<|-", color=C1, lw=2.8))
ax.annotate("", (36, 246), (22, 152), arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2))
ax.text(40, 252, "air out\nthe throat", fontsize=8.6, family=MONO, color=C2)
ax.text(-58, 252, "feed / drain\nhose", fontsize=8.6, family=MONO, color=C1, ha="center")
ax.annotate("radial slots at the foot\nfeed the whole floor", (18, 11), (56, 46),
            fontsize=8.4, family=MONO, color=C4,
            arrowprops=dict(arrowstyle="->", color=C4, lw=1.0), va="center")
ax.annotate("\u00d825 outside / \u00d818 bore\nwall 3.5", (9, 112), (54, 130),
            fontsize=8.4, family=MONO, color=C4,
            arrowprops=dict(arrowstyle="->", color=C4, lw=1.0), va="center")
ax.set_xlim(-128, 156); ax.set_ylim(-16, 282)

head(fig, 0.355, 0.845, "WHAT YOU BUILD")
body(fig, 0.355, 0.812,
     "One printed part: a replacement centre column whose\n"
     "external geometry matches SPTP116 exactly, so the reels\n"
     "and funnel cannot tell the difference — but with a Ø18 mm\n"
     "bore running its full length and four radial slots at the\n"
     "foot. The top takes a push-fit hose tail instead of, or as\n"
     "well as, the agitator-rod socket, and a hose drops down\n"
     "through the funnel throat and clips on.\n\n"
     "PETG rather than PLA. Four perimeters, no sparse infill in\n"
     "the wall, and soak-test it for a week before it ever sees\n"
     "film — a delaminated column is a light leak.", fs=9.2)

head(fig, 0.355, 0.605, "WHY IT BEATS DRILLING THE TANK")
rows2 = [
    ["fill, 0.6 m head",  "2.5 s",  "2.7 s",       "standpipe"],
    ["drain, free",       "9.7 s",  "10.3 s",      "standpipe"],
    ["holes in the tank", "none",   "one",         "standpipe"],
    ["reversible",        "yes",    "no",          "standpipe"],
    ["light risk",        "low",    "medium",      "standpipe"],
    ["keeps 3 reels",     "yes",    "yes",         "tie"],
    ["can still invert",  "unclip", "QD needed",   "standpipe"],
]
axr = fig.add_axes([0.355, 0.265, 0.29, 0.315]); axr.axis("off")
table(axr, rows2, ["", "Standpipe", "1/2 in bulkhead", "Winner"],
      [0, 0.0, 1.0, 1.0], fs=8.6, colcolor={3: C4})

head(fig, 0.675, 0.845, "THE HYDRAULICS")
body(fig, 0.675, 0.812,
     "A \u00d818 bore, but a long one \u2014 190 mm of column plus the hose\n"
     "above it \u2014 so the discharge coefficient falls from 0.55 to\n"
     "about 0.45 for pipe friction and two bends.\n\n"
     "    fill   t = 2.5 s   from 0.6 m of head\n"
     "    drain  t = 9.7 s   free discharge\n\n"
     "Even carrying that penalty it still edges a 1/2 in\n"
     "bulkhead, because 18 mm of bore beats 15.8 mm by more than\n"
     "the friction costs.\n\n"
     "Do not go bigger. The column is \u00d825 outside and the reels\n"
     "hang on it; a \u00d820 bore leaves a 2.5 mm wall that will flex\n"
     "when three loaded reels are pushed down it.", fs=9.2)

head(fig, 0.675, 0.552, "LIGHT-TIGHTNESS \u2014 WHY THIS IS THE SAFER OPTION")
body(fig, 0.675, 0.519,
     "The feed path is a black tube inside a black tube inside a\n"
     "light-trapped funnel. Light entering the throat must turn a\n"
     "corner at the hose, travel 190 mm down a matt bore, then\n"
     "turn 90\u00b0 again at the foot slots before it could reach any\n"
     "film \u2014 which is wound on reels facing outward, away from\n"
     "the column.\n\n"
     "Compare a bulkhead: a straight hole through the floor into\n"
     "the chamber the film is sitting in. Both can be made safe.\n"
     "Only one is safe by accident.", fs=9.2)

callout(fig, 0.355, 0.062, 0.29, 0.185, accent=C2, fs=9.2,
        title="THE ONE REAL RISK",
        text="A printed column is structural \u2014 the\nreels and funnel lock to it. If it\ncracks mid-process the tank is no\n"
             "longer light-tight. Print two, soak-\ntest both, and keep the stock column.")
callout(fig, 0.675, 0.062, 0.28, 0.185, accent=C4, fs=9.2,
        title="OPERATING IT",
        text="Fill: clip on, open the clamp, count\nto three, unclip, cap the column head,\nagitate as normal.\n\n"
             "Drain: clip on, drop the hose end\nbelow the bench, let it siphon. No\npump, no power.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 9  BORE SIZING CHART
# ===========================================================================
fig = new_sheet(9, "Sizing any bottom path",
                "fill and drain time against bore, with every route marked")
ax = fig.add_axes([0.055, 0.115, 0.545, 0.705], facecolor=SURF)
ds = [8 + 0.2 * i for i in range(105)]
ax.plot(ds, [fill_time(d) for d in ds], color=C1, lw=2.0, label="Fill  (0.6 m head)")
ax.plot(ds, [drain_time(d) for d in ds], color=C2, lw=2.0, label="Drain (free discharge)")
ax.plot(ds, [fill_time(d, cd=CD_PIPE) for d in ds], color=C1, lw=1.3, ls=(0, (5, 3)),
        label="Fill,  Cd 0.45 (standpipe)")
ax.plot(ds, [drain_time(d, cd=CD_PIPE) for d in ds], color=C2, lw=1.3, ls=(0, (5, 3)),
        label="Drain, Cd 0.45 (standpipe)")

marks = [(12.5, '3/8"', GREY, CD_BULK), (15.8, '1/2 in port\nroutes 3 & 5', C1, CD_BULK),
         (18.0, 'standpipe\nroute 4', C4, CD_PIPE), (20.9, '3/4 in\nroute 6', C2, CD_BULK),
         (26.6, '1"', GREY, CD_BULK)]
for d, lab, col, cdm in marks:
    ft, dt = fill_time(d, cd=cdm), drain_time(d, cd=cdm)
    ax.plot([d], [ft], "o", ms=9, color=C1, mec="white", mew=1.8, zorder=6)
    ax.plot([d], [dt], "o", ms=9, color=C2, mec="white", mew=1.8, zorder=6)
    ax.annotate(f"{ft:.1f} s", (d, ft), (d, ft + 1.4 if ft < 3.4 else ft - 2.4),
                ha="center", fontsize=8.8, color=INK, family=MONO)
    ax.annotate(f"{dt:.1f} s", (d, dt), (d, dt + 1.3), ha="center", fontsize=8.8,
                color=INK, family=MONO)
    ax.axvline(d, color="#c9d4e0", lw=0.8, ls=":", zorder=1)
    ax.text(d, 26.2, lab, ha="center", va="bottom", fontsize=8.6, color=col,
            family=MONO, fontweight="bold")
ax.axhspan(15, 25, color="#e8eef5", zorder=0)
ax.text(28.6, 21.5, "stock funnel\n15\u201325 s", ha="right", va="center",
        fontsize=8.8, color=GREY, family=MONO)
ax.axvspan(17.2, 18.8, color="#dff2e8", zorder=0)
ax.set_xlim(8, 29); ax.set_ylim(0, 30)
ax.set_xlabel("bore   mm", fontsize=10, color=INK)
ax.set_ylabel("time   seconds", fontsize=10, color=INK)
ax.grid(True, color="#dfe6ee", lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#8fa3b8")
ax.tick_params(colors=GREY, labelsize=9)
lg = ax.legend(loc="upper right", frameon=True, fontsize=8.6, framealpha=1.0)
lg.get_frame().set_edgecolor("#8fa3b8")
ax.set_title("1000 ml \u00b7 65.5 cm\u00b2 plan area \u00b7 Cd 0.55, and 0.45 for the standpipe",
             fontsize=9.6, color=GREY, loc="left", pad=8)

head(fig, 0.635, 0.845, "BOTH CURVES GO AS 1/d\u00b2")
body(fig, 0.635, 0.812,
     "  3/8 \u2192 1/2 in    fill 4.3 \u2192 2.7 s    saves 1.6 s\n"
     "  1/2 \u2192 3/4 in    fill 2.7 \u2192 1.5 s    saves 1.2 s\n"
     "  3/4 \u2192 1 in      fill 1.5 \u2192 0.9 s    saves 0.6 s\n\n"
     "On filling, 3/4 in buys about a second over 1/2 in \u2014 less\n"
     "than your reaction time on a timer. On draining it is\n"
     "worth more, 5.9 s against 10.3 s, but sheet 10 shows what\n"
     "that costs in reels.", fs=9.2)

head(fig, 0.635, 0.645, "SIZING FROM FIRST PRINCIPLES")
body(fig, 0.635, 0.612,
     "Target: fill in under 5 % of the development time.\n\n"
     "    9 min development   \u2192  27 s allowed\n"
     "    6 min               \u2192  18 s\n"
     "    3 min push          \u2192   9 s\n"
     "    90 s  E6 first dev  \u2192   4.5 s\n\n"
     "Everything from 3/8 in upward clears the 3-minute bar.\n"
     "Only 1/2 in and above clears the 90-second bar. Since the\n"
     "hydraulic choice is therefore nearly free, make it on\n"
     "mechanical grounds instead \u2014 which is sheet 10.", fs=9.2)

callout(fig, 0.635, 0.115, 0.32, 0.19, accent=C4,
        title="WHERE THE CURVES STOP HELPING",
        text="Below about 2 s the fill is no longer\nlimited by the bore at all. It is limited\nby how fast you can open a valve, and by\n"
             "the air still leaving through the funnel.\n\n"
             "Past \u00f820 you are engineering for a second\nyou cannot measure. Stop at the standpipe.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 10  BOTTOM PORT GEOMETRY
# ===========================================================================
fig = new_sheet(10, "If you do drill it \u2014 will 3/4 in fit?",
                "the floor plan says yes, the headroom says only just")
ax = fig.add_axes([0.045, 0.38, 0.30, 0.46]); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Circle((0, 0), 51, fc="#eef3f9", ec=INK, lw=1.6))
ax.add_patch(Circle((0, 0), 47.5, fc="white", ec=INK, lw=1.4))
ax.add_patch(Circle((0, 0), 23, fc="#cfdceb", ec=INK, lw=1.3, ls="--"))
ax.text(0, 0, "column\nfoot\n\u00f846", ha="center", va="center", fontsize=8,
        family=MONO, color=INK)
for r, col in ((23, C2), (18, C1)):
    ax.add_patch(Circle((0, 0), r, fc="none", ec=col, lw=2.0))
ax.add_patch(Circle((0, 0), 14, fc="#f6e6d2", ec=C2, lw=1.6))
ax.add_patch(Circle((0, 0), 10.5, fc="#dce8f7", ec=C1, lw=1.6))
ax.annotate("\u00d828 hole (3/4 in)", (10, 10), (58, 40), fontsize=8.6, family=MONO,
            color=C2, arrowprops=dict(arrowstyle="->", color=C2, lw=1.0))
ax.annotate("\u00d846 flange (3/4 in) \u2014\nexactly the size of the\ncolumn foot it replaces",
            (-16.3, -16.3), (-101, -14), fontsize=8.4, family=MONO, color=C2,
            arrowprops=dict(arrowstyle="->", color=C2, lw=1.0), va="center")
ax.annotate("\u00d821 hole (1/2 in)", (-7.4, -7.4), (-96, -46), fontsize=8.4,
            family=MONO, color=C1,
            arrowprops=dict(arrowstyle="->", color=C1, lw=1.0), va="center")
ax.annotate("\u00d895 bore", (-33.6, 33.6), (-96, 56), fontsize=8.6, family=MONO,
            color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
ax.text(0, -70, "FLOOR PLAN \u2014 CENTRE MOUNTED", ha="center", fontsize=9.6,
        family=MONO, fontweight="bold", color=INK)
ax.set_xlim(-104, 104); ax.set_ylim(-80, 74)

ax2 = fig.add_axes([0.375, 0.38, 0.23, 0.46]); ax2.set_aspect("equal"); ax2.axis("off")
ax2.add_patch(Rectangle((-47.5, 0), 95, 141, fc="white", ec=INK, lw=1.4))
ax2.add_patch(Rectangle((-47.5, 132), 95, 9, fc="#f6e6d2", ec="none"))
for i in range(3):
    ax2.add_patch(Rectangle((-46, i * 44), 92, 42, fc="#dce8f7", ec=C1, lw=1.0))
    ax2.text(0, i * 44 + 21, f"reel {i+1}  44", ha="center", va="center",
             fontsize=8.4, family=MONO, color=INK)
ax2.annotate("", (60, 132), (60, 141), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.4))
ax2.text(68, 151, "9 mm \u2014 ALL THE SPARE\nHEIGHT THERE IS", fontsize=9,
         family=MONO, color=DIMC, va="center", fontweight="bold")
ax2.annotate("", (-60, 0), (-60, 141), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.4))
ax2.text(-64, 70, "141 usable depth", rotation=90, ha="center", va="center",
         fontsize=8.8, family=MONO, color=DIMC)
ax2.text(0, -16, "HEIGHT STACK-UP", ha="center", fontsize=9.6, family=MONO,
         fontweight="bold", color=INK)
ax2.set_xlim(-78, 150); ax2.set_ylim(-24, 168)

head(fig, 0.635, 0.845, "1  THE FLOOR PLAN \u2014 PASSES, BUT ONLY AT THE CENTRE")
body(fig, 0.635, 0.812,
     "Off-centre is impossible at any size. To clear the \u00f846\n"
     "column foot the port centre must sit at r \u2265 38 mm; to keep\n"
     "its flange inside the \u00f895 bore it must sit at r \u2264 32.5 mm.\n"
     "No overlap, even for 3/8 in.\n\n"
     "Centre mounted, a 3/4 in flange (\u00f846) sits inside the bore\n"
     "with 24 mm clearance all round. So the floor is not the\n"
     "constraint \u2014 but centring means the column foot has to go\n"
     "whatever bore you pick, which is most of the work of\n"
     "building a standpipe anyway.", fs=9.2)

head(fig, 0.635, 0.635, "2  THE HEADROOM \u2014 THIS IS WHAT DECIDES IT")
body(fig, 0.635, 0.602,
     "    usable depth to the funnel      141 mm\n"
     "    three reels at 44 mm pitch      132 mm\n"
     "    \u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\n"
     "    budget for everything inside      9 mm\n\n"
     "    1/2 in low-profile nut    6 mm, legs straddle it\n"
     "    3/4 in low-profile nut    9\u201310 mm, they cannot\n\n"
     "Exceed 9 mm and the top reel fouls the funnel: the lid\n"
     "will not lock, and a 3-reel tank has quietly become a\n"
     "2-reel tank.", fs=9.2)

callout(fig, 0.045, 0.085, 0.91, 0.205, accent=C2,
        title="VERDICT ON DRILLING",
        text="3/4 in is not too wide for the floor \u2014 it is too tall for the ceiling. Fitted dead centre it works, fills in 1.5 s, drains in 5.9 s,\n"
             "and will almost certainly cost you the third reel. If you routinely run two rolls, that is a fair trade.\n\n"
             "If you want three rolls and you are set on drilling, fit 1/2 in: 2.7 s and 10.3 s, full capacity.\n\n"
             "But note what sheet 8 showed. Both sizes require replacing the column foot, which is the same work as printing a standpipe \u2014 and the\n"
             "standpipe then gives 2.5 s and 9.7 s with no hole at all. The only remaining reason to drill is if you specifically want 3/4 in drain\n"
             "speed and will trade a reel for four seconds.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 11  PUMP VS GRAVITY
# ===========================================================================
fig = new_sheet(11, "Pump or gravity?",
                "gravity wins on speed; the pump wins at everything it is actually for")
ax = fig.add_axes([0.055, 0.455, 0.52, 0.375], facecolor=SURF)
YMAX = 46.0
for nm, lo, hi, lx, ly in (("small peristaltic  0.5\u20133 L/min", 0.5, 3, 0.85, 1.75),
                           ("12 V diaphragm  4\u20137 L/min", 4, 7, 0.85, 5.5),
                           ("12 V centrifugal  10\u201330 L/min", 10, 30, 0.135, 26.5)):
    ax.axhspan(lo, hi, color=C4, alpha=0.13, zorder=0)
    ax.text(lx, ly, nm, fontsize=8.3, family=MONO, color=INK, va="center",
            bbox=dict(fc="white", ec=C4, lw=0.7, alpha=0.92, pad=2.2), zorder=7)

Hs = [0.05 + 0.005 * i for i in range(331)]
for d, col, lab in ((12.5, C3, "3/8 in line"), (15.8, C1, "1/2 in line"),
                    (20.9, C2, "3/4 in line")):
    ax.plot(Hs, [q_grav(d, H) * 60000 for H in Hs], color=col, lw=2.0, label=lab)
    xs = [H for H in Hs if q_grav(d, H) * 60000 < YMAX - 3.5]
    xa = xs[-1] if xs else 1.5
    ax.annotate(lab, (xa, q_grav(d, xa) * 60000), (xa - 0.02, q_grav(d, xa) * 60000 + 2.6),
                fontsize=9, color=col, family=MONO, ha="right", fontweight="bold")
ax.axhline(4, color=GREY, lw=1.0, ls="--", zorder=1)
lg = ax.legend(loc="lower right", frameon=True, fontsize=9, framealpha=1.0)
lg.get_frame().set_edgecolor("#8fa3b8")
ax.set_xlim(0.05, 1.70); ax.set_ylim(0, YMAX)
ax.set_xlabel("reservoir surface above the tank floor   m", fontsize=10, color=INK)
ax.set_ylabel("delivery   litres / minute", fontsize=10, color=INK)
ax.set_title("Gravity delivery against what pumps in this price class really do",
             fontsize=9.6, color=GREY, loc="left", pad=8)
ax.grid(True, color="#dfe6ee", lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#8fa3b8")
ax.tick_params(colors=GREY, labelsize=9)

head(fig, 0.61, 0.845, "THE HEADLINE")
body(fig, 0.61, 0.812,
     "A shelf 600 mm above the bench feeding a 1/2 in line\n"
     "delivers 370 ml/s — 22 litres a minute.\n\n"
     "To match that you need a 22 L/min pump that is also\n"
     "fixer-proof. A cheap diaphragm pump gives 4–7; a small\n"
     "peristaltic gives 0.5–3, slower than the stock funnel.\n\n"
     "Even 200 mm of head beats every pump here bar a large\n"
     "centrifugal — which is rated at zero head anyway.", fs=9.2)

head(fig, 0.61, 0.645, "SO USE GRAVITY FOR FILL AND DRAIN")
body(fig, 0.61, 0.612,
     "  fill    reservoir on a shelf 0.4–0.8 m up, gate clamp\n"
     "          or ball valve at the tank. No power, no priming,\n"
     "          nothing extra to flush.\n"
     "  drain   tank on the bench, waste on the floor. 0.3 m of\n"
     "          drop is plenty.\n\n"
     "Volume is set by measuring into the reservoir, not by\n"
     "timing a pump — one less thing to get wrong.", fs=9.2)

head(fig, 0.61, 0.472, "AND USE A PUMP FOR WHAT IT IS GOOD AT")
body(fig, 0.61, 0.439,
     "RECIRCULATION  one turnover per 15 s is only 4 L/min, and\n"
     "   it gives continuous, perfectly repeatable agitation\n"
     "   with no inversion at all. The real reason to own one.\n"
     "LAST RESIDUE   gravity leaves 20–40 ml in the spirals; a\n"
     "   peristaltic pulls it out, gravity will not.\n"
     "NO SHELF       accept 8–15 s instead of 2.5 s.\n"
     "TEMPERING      circulate through a coil in a water bath.", fs=9.2)

callout(fig, 0.045, 0.042, 0.53, 0.268, accent=C4, fs=9.0,
        title="CHOOSING A PUMP, IF YOU BUY ONE",
        text="PERISTALTIC   Only the tube touches chemistry, so compatibility is a\n"
             "   tubing question and nothing else. Self-priming, safe to run dry,\n"
             "   reverses for fill and drain with one unit, meters volume by\n"
             "   revolution count. Slow. Norprene or platinum-cure silicone.\n"
             "DIAPHRAGM     The practical middle. Demand a Santoprene or EPDM\n"
             "   diaphragm and a polypropylene head. Self-priming, dry-run safe,\n"
             "   4–7 L/min, and cheap.\n"
             "CENTRIFUGAL   Fast and cheap, but not self-priming and destroyed by\n"
             "   running dry. Only worth it if it stays flooded.\n"
             "NEVER         Brass, bronze or aluminium wetted parts — fixer attacks\n"
             "   them and dissolved copper fogs film. Gear pumps. Anything you\n"
             "   cannot flush completely between developer and fixer.")
callout(fig, 0.61, 0.042, 0.345, 0.268, accent=C2, fs=9.0,
        title="CARRY-OVER — THE HIDDEN COST",
        text="Every metre of hose and every pump head\n"
             "holds chemistry the next step inherits. A\n"
             "1/2 in line 0.5 m long holds 98 ml — a\n"
             "tenth of your tank volume. Fixer carried\n"
             "into developer is the one that ruins film.\n\n"
             "  • one dedicated line per chemical, or\n"
             "  • a water flush between every step, or\n"
             "  • quick-disconnects and one hose set\n"
             "    per chemical.\n\n"
             "Gravity has the same problem and the same\n"
             "answers, with one fewer wetted part to flush.")

pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 12  DECISION + BUILD
# ===========================================================================
fig = new_sheet(12, "Decide, then build",
                "the matrix, the stack-up, and the test you must not skip")

axm = fig.add_axes([0.045, 0.505, 0.55, 0.34]); axm.axis("off")
mrows = [
    ["Shortest development \u2265 6 min", "2  tilt technique",   "free", "10 / 15"],
    ["\u2265 4 min, no tools",             "2  tilt technique",   "free", "10 / 15"],
    ["< 4 min, will print a part",  "4  column standpipe", "low",  "2.5 / 9.7"],
    ["< 4 min, will not print",     "3  funnel skirt port", "low", "2.7 / 15"],
    ["Want the fastest drain",      "6  3/4 in bulkhead",  "med",  "1.5 / 5.9"],
    ["Want repeatability",          "8  tilt cradle + 4",  "med",  "2.5 / 9.7"],
    ["Want it hands-off",           "7  recirc pump + 4",  "high", "2.5 / 9.7"],
]
table(axm, mrows, ["If this is you", "Build this", "Cost", "Fill / drain  s"],
      [0, 0.0, 1.0, 1.0], highlight=3, colcolor={3: C1},
      colw=[0.36, 0.28, 0.12, 0.24])

ax = fig.add_axes([0.600, 0.425, 0.185, 0.42]); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((-70, 0), 140, 7, fc=HATCH, ec=INK, lw=1.5, hatch="////"))
ax.text(-74, 3.5, "floor 7", ha="right", va="center", fontsize=8.2, family=MONO, color=INK)
ax.add_patch(Rectangle((-30, 7), 60, 2.5, fc="#6f8aa6", ec=INK, lw=1.0))
ax.add_patch(Rectangle((-30, -2.5), 60, 2.5, fc="#6f8aa6", ec=INK, lw=1.0))
ax.add_patch(Rectangle((-23, 9.5), 46, 6, fc="#cfdceb", ec=INK, lw=1.4))
ax.add_patch(Rectangle((-10.5, -26), 21, 41.5, fc="white", ec=INK, lw=1.4))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * 10.5, -26), s * 4, 41.5, fc="#cfdceb", ec=INK, lw=1.4))
ax.add_patch(Rectangle((-21, -26), 42, 8, fc="#cfdceb", ec=INK, lw=1.4))
ax.add_patch(Rectangle((-16, -50), 32, 24, fc="#8fa8c4", ec=INK, lw=1.4))
ax.text(0, -38, "valve", ha="center", va="center", fontsize=7.6, family=MONO,
        color="white", fontweight="bold")
ax.add_patch(Rectangle((-11, -66), 22, 16, fc="#4a5a6a", ec=INK, lw=1.3))
ax.text(15, -58, "opaque hose\n300 mm,\none 90\u00b0 bend", fontsize=8, family=MONO,
        color=INK, va="center")
ax.add_patch(Polygon([(-26, 15.5), (26, 15.5), (20, 24), (-20, 24)], closed=True,
                     fc="#dce8f7", ec=C1, lw=1.5))
ax.text(0, 20, "diffuser", ha="center", va="center", fontsize=7.4, family=MONO, color=C1)
for s in (-1, 1):
    ax.add_patch(Rectangle((s * 20, 24), s * 6, 8, fc="#cfdceb", ec=INK, lw=1.2))
ax.add_patch(Rectangle((-23, 32), 46, 4, fc="#cfdceb", ec=INK, lw=1.3))
ax.add_patch(Rectangle((-12.5, 36), 25, 26, fc="#eef3f9", ec=INK, lw=1.3))
ax.text(28, 34, "standoff +\ncolumn spigot", fontsize=8, family=MONO, color=INK,
        va="center")
ax.annotate("", (-58, 7), (-58, 36), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.4))
ax.text(-62, 21, "\u2264 9", rotation=90, ha="center", va="center", fontsize=8.6,
        family=MONO, color=DIMC, fontweight="bold")
ax.text(0, -84, "BULKHEAD STACK-UP", ha="center", fontsize=9, family=MONO,
        fontweight="bold", color=INK)
ax.set_xlim(-110, 122); ax.set_ylim(-96, 76)

head(fig, 0.790, 0.845, "MATERIALS")
body(fig, 0.790, 0.812,
     "USE    PP or PVDF bulkheads\n"
     "       EPDM or silicone gaskets\n"
     "       316 stainless if metal\n"
     "       black EPDM or silicone hose\n"
     "       PETG for printed parts\n\n"
     "NEVER  brass or bronze — fixer eats\n"
     "       it, copper fogs film\n"
     "       aluminium — developer eats it\n"
     "       natural rubber — swells\n"
     "       clear hose of any colour\n\n"
     "DO NOT CUT A THREAD IN THE TANK.\n"
     "7 mm of polystyrene splits on a\n"
     "tapered NPT thread — if not on\n"
     "assembly then on the third thermal\n"
     "cycle. Through-hole, gasket both\n"
     "sides, nut takes the load.", fs=8.8)

head(fig, 0.045, 0.455, "DRILLING HIPS")
body(fig, 0.045, 0.422,
     "1  Back the floor with a clamped scrap block.\n"
     "2  Step drill, never a hole saw — it grabs and splits.\n"
     "3  Low speed, no pressure.\n"
     "4  Chamfer both faces 0.5 mm to kill crack initiation.\n"
     "5  Nut hand tight plus a quarter turn; HIPS creeps.", fs=9.0)

head(fig, 0.045, 0.330, "COMMISSIONING, IN ORDER")
body(fig, 0.045, 0.297,
     "1  Water only. Check for leaks at temperature, twice.\n"
     "2  Time a 1000 ml fill and a full drain; those numbers\n"
     "   are now part of your process.\n"
     "3  Light-trap test, right. Then one roll of cheap film.", fs=9.0)

head(fig, 0.375, 0.455, "LIGHT-TRAP TEST — THE ONE YOU MUST NOT SKIP")
body(fig, 0.375, 0.422,
     "Any new opening is a light leak until proven otherwise.\n"
     "Light travels in straight lines, so 300 mm of opaque hose\n"
     "with one 90° bend defeats it; a closed valve defeats it\n"
     "absolutely.\n\n"
     "1  Load a strip of the fastest film you use.\n"
     "2  Assemble fully, port open, hose connected.\n"
     "3  Stand it in the brightest light you have for ten times\n"
     "   your longest process time.\n"
     "4  Develop it beside an unexposed control from that roll.\n"
     "5  Any density difference at all — the trap has failed.\n"
     "   Lengthen the hose or add a bend. Do not rationalise it.", fs=9.0)

callout(fig, 0.045, 0.058, 0.91, 0.163, accent=C1, fs=9.0,
        title="THE TRADE-OFF TO SETTLE BEFORE YOU BUILD ANYTHING",
        text="A hose attached to the tank cannot be inverted, and inversion is the agitation method the tank was designed around. Three ways out:\n\n"
             "  Rotary only       Use the agitator rod. Simplest, slightly more prone to edge effects. Re-test your times.\n"
             "  Quick-disconnect  Self-sealing QD at the port. Fill, disconnect, invert exactly as now, reconnect to drain. Keeps every existing time.\n"
             "  Recirculation     Pump continuously through the loop. Most even and most repeatable, and the largest build.\n\n"
             "The quick-disconnect is the right first build whichever route you pick: reversible, preserves your development times, costs one fitting.")
pdf.savefig(fig); plt.close(fig)







# ===========================================================================
# 13  FLUID ARCHITECTURE
# ===========================================================================
def valve(ax, x, y, s=2.4, col=INK, fc="white"):
    ax.add_patch(Polygon([(x - s, y - s), (x - s, y + s), (x, y)], closed=True,
                         fc=fc, ec=col, lw=1.3, zorder=6))
    ax.add_patch(Polygon([(x + s, y - s), (x + s, y + s), (x, y)], closed=True,
                         fc=fc, ec=col, lw=1.3, zorder=6))


def checkv(ax, x, y, s=2.0, col=C4):
    ax.add_patch(Polygon([(x - s, y + s), (x + s, y + s), (x, y - s)], closed=True,
                         fc="white", ec=col, lw=1.3, zorder=6))
    ax.plot([x - s, x + s], [y - s, y - s], color=col, lw=1.6, zorder=6)


def vessel(ax, x, y, w, h, title, sub, col):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.0",
                                fc="#f4f7fb", ec=col, lw=1.6, zorder=5))
    ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=8.6,
            family=MONO, fontweight="bold", color=col, zorder=7)
    ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center", fontsize=7.6,
            family=MONO, color=GREY, zorder=7)


fig = new_sheet(13, "Fluid architecture",
                "four sources, one tank, three destinations — and nothing shared that matters")
ax = fig.add_axes([0.045, 0.44, 0.91, 0.41]); ax.axis("off")

SRC = [("WASH WATER", "discard · 3–5 L", C1),
       ("DEVELOPER", "one-shot · 1 L", C3),
       ("STOP", "reuse or discard", C2),
       ("FIXER", "reusable · 1 L", C4)]
for i, (t, s_, c) in enumerate(SRC):
    x = 2 + i * 26
    vessel(ax, x, 76, 22, 9, t, s_, c)
    cx = x + 11
    ax.plot([cx, cx], [76, 64], color=INK, lw=1.4, zorder=4)
    checkv(ax, cx, 71.5)
    valve(ax, cx, 67.0)
    ax.plot([cx, 58], [64, 58], color=INK, lw=1.4, zorder=4)

ax.plot([58, 58], [58, 53], color=INK, lw=2.6, zorder=4)
ax.annotate("", (58, 51), (58, 54), arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.4))
ax.text(61, 55, "RISER  ~16 mL", fontsize=8.4, family=MONO, color=C1, va="center")

ax.add_patch(Rectangle((46, 22), 24, 30, fc="white", ec=INK, lw=1.8, zorder=3))
ax.add_patch(Rectangle((46, 22), 24, 19, fc="#dce8f7", ec="none", zorder=2))
ax.add_patch(Polygon([(46, 52), (70, 52), (61, 45), (55, 45)], closed=True,
                     fc="#eef3f9", ec=INK, lw=1.3, zorder=4))
for r in range(3):
    ax.add_patch(Rectangle((47.5, 23 + r * 6.0), 21, 5.4, fc="none", ec=C1,
                           lw=0.7, ls="--", zorder=4))
ax.add_patch(Rectangle((56.6, 23), 2.8, 28, fc="#d8f0e4", ec=C4, lw=1.5, zorder=5))
ax.text(48.5, 43.5, "MR3", fontsize=8, family=MONO, color=GREY, zorder=6)
ax.text(44, 47, "COLUMN — fill path only,\nnever sees used chemistry", fontsize=8.4,
        family=MONO, color=C4, ha="right", va="center")

ax.plot([58, 58], [22, 12], color=INK, lw=2.6, zorder=4)
valve(ax, 58, 17, col=C2)
ax.text(61, 17, "TRUNK  ~29 mL\nstraight down, no traps", fontsize=8.4, family=MONO,
        color=C2, va="center")
ax.plot([58], [12], "o", ms=7, color=INK, zorder=6)

DEST = [("DRAIN", "water + spent developer", C1, 2),
        ("FIXER BOTTLE", "reclaim · back to source", C4, 44),
        ("HAZARDOUS JUG", "silver-bearing, exhausted", C2, 86)]
for t, s_, c, x in DEST:
    vessel(ax, x, 0, 30, 9, t, s_, c)
    ax.annotate("", (x + 15, 9.4), (58, 12),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=1.6))
ax.text(96, 21, "3-way diverter —\nFAILS TO THE JUG,\nnever to the drain", fontsize=8.4,
        family=MONO, color=DIMC, ha="left", va="center", fontweight="bold")

checkv(ax, 5, 40)
ax.text(9, 40, "check valve or air gap on", fontsize=8.2, family=MONO,
        color=INK, va="center")
ax.text(9, 36.5, "every source — stops back-", fontsize=8.2, family=MONO,
        color=GREY, va="center")
ax.text(9, 33.0, "siphonage into a stock bottle", fontsize=8.2, family=MONO,
        color=GREY, va="center")
valve(ax, 5, 27)
ax.text(9, 27, "pinch valve — the tubing is", fontsize=8.2, family=MONO,
        color=INK, va="center")
ax.text(9, 23.5, "the only wetted part", fontsize=8.2, family=MONO,
        color=GREY, va="center")
ax.set_xlim(-2, 124); ax.set_ylim(-4, 88)

head(fig, 0.045, 0.405, "THE TWO RULES THAT DO MOST OF THE WORK")
body(fig, 0.045, 0.372,
     "1  EVERYTHING BELOW THE TANK SLOPES DOWN to its\n"
     "   destination. No horizontal runs, no U-traps, no\n"
     "   loops. Then every path empties itself after every\n"
     "   step and carry-over is a wall film, not a slug.\n"
     "   Worth about 40×; sheet 14 does the arithmetic.\n\n"
     "2  ROUTE THE WASH THROUGH THE SHARED PATH. By the end of\n"
     "   a wash the trunk has had 3–5 L of water through it.\n"
     "   The process you already run IS the flush.", fs=9.2)

head(fig, 0.375, 0.405, "WHY FILL AND DRAIN ARE SEPARATE PATHS")
body(fig, 0.375, 0.372,
     "Fill enters over the top, down the printed column, out\n"
     "at the floor. Drain leaves through a bulkhead in the\n"
     "floor, straight down. They share nothing but the tank.\n\n"
     "CORRECTION TO SHEET 8: a standpipe used for BOTH fill\n"
     "and drain has to siphon up over the column head at\n"
     "190 mm — above the 141 mm liquid surface. It will not\n"
     "self-prime. It works only if you drain immediately after\n"
     "filling, while the line is still full. For unattended use,\n"
     "drill the floor for the drain or pump the drain leg.", fs=9.2)

callout(fig, 0.695, 0.045, 0.26, 0.33, accent=C4, fs=9.0,
        title="IF YOU WILL NOT DRILL",
        text="Run everything through the column and\n"
             "accept one high point at the column\n"
             "head. Then you need:\n\n"
             "  • an air-admittance valve at the\n"
             "    apex. It breaks the siphon and\n"
             "    lets both legs drain, and it\n"
             "    doubles as the back-siphonage\n"
             "    guard;\n"
             "  • the drain sequenced straight\n"
             "    after the fill so the line stays\n"
             "    primed, or a pump on the drain\n"
             "    leg.\n\n"
             "Costs one component and some\n"
             "sequencing discipline, and keeps the\n"
             "tank unmarked.")

callout(fig, 0.045, 0.045, 0.63, 0.16, accent=C1, fs=9.2,
        title="WHY THIS SHAPE AND NOT A VALVE MATRIX",
        text="A full N×M matrix lets any source reach any destination. That sounds flexible and is\n"
             "actually a liability: one stuck valve can put fixer into the developer bottle.\n\n"
             "This layout is deliberately poorer. Sources only ever go one way — into the tank.\n"
             "Destinations are only reachable from the tank. Nothing routes bottle-to-bottle, so no\n"
             "single failure can cross-contaminate a stock solution. The worst case is a ruined run,\n"
             "not a ruined litre.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 14  CARRY-OVER BUDGET
# ===========================================================================
BORE_TRUNK = 15.8
FILM = 0.1
A_TRUNK = math.pi * BORE_TRUNK ** 2 / 4.0
P_TRUNK = math.pi * BORE_TRUNK


def bulk_ml(L):
    return A_TRUNK * L / 1000.0


def film_ml(L):
    return P_TRUNK * L * FILM / 1000.0


def purge_ml(v_res, target_ml=1.0):
    return v_res * math.log(v_res / target_ml) if v_res > target_ml else 0.0


fig = new_sheet(14, "Carry-over budget",
                "the one number that decides whether any of this works")
ax = fig.add_axes([0.055, 0.45, 0.52, 0.37], facecolor=SURF)
Ls = list(range(10, 1001, 5))
ax.plot(Ls, [bulk_ml(L) for L in Ls], color=C2, lw=2.2, label="trunk left full")
ax.plot(Ls, [film_ml(L) for L in Ls], color=C1, lw=2.2, label="trunk self-drained")
ax.set_yscale("log")
ax.axhspan(0.1, 10, color="#e6f0e9", zorder=0)
ax.axhspan(50, 400, color="#f8ece6", zorder=0)
ax.text(985, 3.0, "under 1 % of a 1 L fill — safe", fontsize=8.4, family=MONO,
        color=C4, ha="right", va="center")
ax.text(985, 180, "over 5 % — ruins film", fontsize=8.4, family=MONO,
        color=C2, ha="right", va="center")
L = 300
for f, col in ((bulk_ml, C2), (film_ml, C1)):
    ax.plot([L], [f(L)], "o", ms=9, color=col, mec="white", mew=1.8, zorder=6)
    ax.annotate(f"{f(L):.1f} mL", (L, f(L)), (L + 30, f(L) * 1.45),
                fontsize=9.2, family=MONO, color=INK, fontweight="bold")
ax.axvline(L, color="#c9d4e0", lw=0.9, ls=":", zorder=1)
ax.text(L, 0.13, "a typical 300 mm trunk", fontsize=8.4, family=MONO, color=GREY,
        ha="center", va="bottom")
ax.set_xlim(0, 1000); ax.set_ylim(0.1, 400)
ax.set_xlabel("shared trunk length   mm", fontsize=10, color=INK)
ax.set_ylabel("carried into the next step   mL   (log)", fontsize=9.6, color=INK)
ax.set_title("½ in bore · 0.1 mm drained film · 40× apart at every length",
             fontsize=9.6, color=GREY, loc="left", pad=8)
ax.grid(True, which="both", color="#dfe6ee", lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#8fa3b8")
ax.tick_params(colors=GREY, labelsize=9)
lgd = ax.legend(loc="lower right", frameon=True, fontsize=9.2, framealpha=1.0)
lgd.get_frame().set_edgecolor("#8fa3b8")

head(fig, 0.61, 0.845, "THE COMPONENT BUDGET")
axb = fig.add_axes([0.61, 0.590, 0.345, 0.225]); axb.axis("off")
brows = [
    ["Column Ø18 × 190", "48.3", "1.1"],
    ["Trunk ½ in × 300", "58.8", "1.5"],
    ["Valve bodies", "~5", "~0.2"],
    ["TOTAL", "112", "2.8"],
    ["as % of a 1 L fill", "11.2 %", "0.28 %"],
]
table(axb, brows, ["path element", "left full\nmL", "self-drained\nmL"],
      [0, 0.0, 1.0, 1.0], fs=8.8, highlight=4,
      colcolor={1: C2, 2: C1}, colw=[0.44, 0.28, 0.28])

head(fig, 0.61, 0.545, "AND THE PURGE IT IMPLIES")
body(fig, 0.61, 0.512,
     "To flush a residue down to 1 mL of the old liquid, a\n"
     "well-mixed line needs  V = V_res · ln( V_res / 1 mL ):\n\n"
     f"    left full     112 mL  →  purge {purge_ml(112):.0f} mL\n"
     f"    self-drained  2.8 mL  →  purge {purge_ml(2.8):.1f} mL\n\n"
     "Half a litre per step, or three millilitres. That ratio\n"
     "is the whole argument for fixing the geometry first.", fs=9.2)

callout(fig, 0.045, 0.055, 0.53, 0.325, accent=C2, fs=9.0,
        title="THE TWO WAYS CARRY-OVER HURTS — THEY ARE NOT THE SAME",
        text="POISONING   Fixer into developer. A few mL per litre is enough to\n"
             "   depress contrast and cause dichroic fog. Cumulative and\n"
             "   irreversible. This is the one that scraps film.\n\n"
             "DILUTION    Wash water into developer. 112 mL of water in a 1 L\n"
             "   fill is an 11 % dilution — an 11 % change in development\n"
             "   activity, which reads as flat, thin negatives. Predictable,\n"
             "   repeatable, and completely avoidable.\n\n"
             "Self-draining geometry fixes both at once. Where it cannot — the\n"
             "developer always follows the wash — a purge to waste is the\n"
             "answer, and at 3 mL it is not worth automating around.")
callout(fig, 0.61, 0.055, 0.345, 0.325, accent=C4, fs=9.0,
        title="WHERE 0.1 mm COMES FROM",
        text="A low-viscosity aqueous solution draining\n"
             "off a vertical plastic wall leaves a film\n"
             "of roughly 0.05–0.15 mm. 0.1 mm is the\n"
             "middle of that band.\n\n"
             "It scales with the square root of\n"
             "viscosity, so cold, syrupy stock leaves\n"
             "more and warm working-strength solution\n"
             "leaves less.\n\n"
             "Call the self-drained figure 2–5 mL\n"
             "rather than 2.8 mL and nothing changes:\n"
             "still forty times better than leaving the\n"
             "line full, still under half a percent of\n"
             "the tank volume.")
pdf.savefig(fig); plt.close(fig)

# ===========================================================================
# 15  PROCESS SEQUENCES
# ===========================================================================
fig = new_sheet(15, "Process sequences",
                "who follows whom, and the one step that needs a purge")

head(fig, 0.045, 0.845, "BLACK & WHITE — one-shot developer, reusable fixer")
axw = fig.add_axes([0.045, 0.600, 0.91, 0.220]); axw.axis("off")
bw = [
    ["1", "Pre-soak (optional)", "water", "discard", "1 L", "wash line", "drain", "no"],
    ["2", "Developer", "one-shot", "discard", "1 L", "dev reservoir", "drain", "YES  ~150 mL"],
    ["3", "Stop", "water or acid", "either", "1 L", "wash / stop bottle", "drain / stop bottle", "no"],
    ["4", "Fixer", "reusable", "reclaim", "1 L", "fixer bottle", "fixer bottle", "no"],
    ["5", "Wash", "water", "discard", "3–5 L", "wash line", "drain", "no — this IS the flush"],
    ["6", "Wetting agent", "one-shot", "discard", "1 L", "small reservoir", "drain", "no"],
]
table(axw, bw, ["#", "Step", "Liquid", "Class", "Vol", "Source", "Destination", "Purge first?"],
      [0, 0.0, 1.0, 1.0], fs=8.6, highlight=2,
      colcolor={7: DIMC}, colw=[0.04, 0.17, 0.11, 0.09, 0.06, 0.17, 0.18, 0.18])

head(fig, 0.045, 0.560, "C-41 — every bath reusable, 38 °C, and it breaks the easy rule")
axc = fig.add_axes([0.045, 0.290, 0.91, 0.250]); axc.axis("off")
c41 = [
    ["1", "Pre-warm", "water 38 °C", "discard", "1 L", "tempered wash", "drain", "no"],
    ["2", "Colour developer", "replenished", "reclaim", "1 L", "dev bottle", "dev bottle", "YES → replenisher"],
    ["3", "Bleach", "reusable", "reclaim", "1 L", "bleach bottle", "bleach bottle", "no"],
    ["4", "Wash", "water", "discard", "2 L", "wash line", "drain", "no"],
    ["5", "Fixer", "reusable", "reclaim", "1 L", "fixer bottle", "fixer bottle", "no"],
    ["6", "Wash", "water", "discard", "3 L", "wash line", "drain", "no"],
    ["7", "Stabiliser", "reusable", "reclaim", "1 L", "stab bottle", "stab bottle", "no"],
]
table(axc, c41, ["#", "Step", "Liquid", "Class", "Vol", "Source", "Destination", "Purge first?"],
      [0, 0.0, 1.0, 1.0], fs=8.6, highlight=2,
      colcolor={7: DIMC}, colw=[0.04, 0.17, 0.11, 0.09, 0.06, 0.17, 0.18, 0.18])

callout(fig, 0.045, 0.042, 0.44, 0.225, accent=C4, fs=9.2,
        title="THE FREE WIN — CONTAMINATION ONLY MATTERS ONE WAY",
        text="In both sequences each bath is preceded by something\n"
             "harmless to it:\n\n"
             "    stop ← developer    neutralised anyway\n"
             "    fixer ← stop        acid into acid fixer\n"
             "    wash ← fixer        irrelevant\n"
             "    developer ← wash    DILUTION — the only harmful one\n\n"
             "So exactly one step needs a purge, and in B&W it is the\n"
             "one-shot, where 150 mL to waste costs pennies.")
callout(fig, 0.515, 0.042, 0.44, 0.225, accent=C2, fs=9.2,
        title="WHERE C-41 IS HARDER",
        text="The colour developer is reusable AND follows a wash, so\n"
             "its purge cannot go to waste without losing stock. Send\n"
             "it to the replenisher jug and replenish on volume.\n\n"
             "Bleach carried back into the developer is the serious\n"
             "one — it oxidises the developing agent. Never sequence\n"
             "bleach before developer, and if a blix replaces steps 3\n"
             "and 5, put a wash either side of it.\n\n"
             "All lines and bottles must hold 38 °C ± 0.3.")
pdf.savefig(fig); plt.close(fig)

pdf.close()
print(out)

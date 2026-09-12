"""Shared A3 sheet framework: page borders and title bar, headings,
callouts, tables, dimension helpers, and multi-view STL rendering.

Imported by drawings.py; not runnable on its own."""

import os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch, Wedge
import matplotlib.image as mpimg
import trimesh
import render_stl as R

INK, GREY, DIMC = "#10243b", "#5b6b7d", "#b3261e"
C1, C2, C3, C4 = "#2f6fb5", "#c26a00", "#8a4fbd", "#0e8a5f"
MONO = "monospace"
STL, IMG = "stl", "_render"
os.makedirs(IMG, exist_ok=True)

# geometry, mirrored from model2.py
DRUM_OD, JOUR_D, JOUR_W = 270.0, 250.0, 34.0
MID_L, DRUM_L = 130.0, 198.0
HOLE_D, SLEEVE_T, SHELL_T = 106.0, 6.0, 8.0
N_TEETH, TOOTH_W, TOOTH_D = 78, 5.0, 3.0
TANK_OD, TANK_LEN = 102.0, 303.0
AXIS_H, NOTCH_R, FRAME_T, FRAME_HW, BASE_T = 175.0, 131.0, 26.0, 150.0, 10.0
MOT_ANG, WHEEL_OD, WHEEL_W = 40.0, 63.0, 29.0
ENV = (295.0, 315.0, 315.0)

R_PITCH = JOUR_D / 2.0 - TOOTH_D / 2.0          # tyre rides between crest and root
RATIO = (WHEEL_OD / 2.0) / R_PITCH
RPM = {3.0: 120.0, 4.5: 185.0, 6.0: 250.0}
TOOTH_PITCH = math.pi * JOUR_D / N_TEETH
NS = 4


def new_sheet(n, title, sub):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=150, facecolor="white")
    for r, lw in (((0.018, 0.018, 0.964, 0.964), 2.0), ((0.028, 0.028, 0.944, 0.944), 0.7)):
        fig.patches.append(Rectangle(r[:2], r[2], r[3], transform=fig.transFigure,
                                     fill=False, ec=INK, lw=lw, zorder=5))
    fig.text(0.045, 0.958, "PATERSON MULTI-REEL 5  ·  CROSS-AXIS TANK TUMBLER",
             fontsize=10.5, color=GREY, family=MONO, va="center")
    fig.text(0.955, 0.958, f"SHEET {n} OF {NS}", fontsize=10.5, color=GREY,
             family=MONO, va="center", ha="right")
    fig.lines.append(plt.Line2D([0.045, 0.955], [0.945, 0.945],
                                transform=fig.transFigure, color=INK, lw=0.7))
    fig.text(0.045, 0.915, title, fontsize=17, fontweight="bold", color=INK, va="center")
    fig.text(0.045, 0.886, sub, fontsize=10.5, color=GREY, family=MONO, va="center")
    fig.text(0.045, 0.032, "Every dimension measured off the exported STL. Motor and wheel "
             "data from Adafruit 3777 / 3766. Build envelope Bambu H2D dual-nozzle "
             "300 × 320 × 320 less 5 mm per axis.",
             fontsize=7.8, color=GREY, family=MONO, va="bottom")
    return fig


def head(f, x, y, t, fs=11.5, c=INK):
    return f.text(x, y, t, fontsize=fs, fontweight="bold", color=c, family=MONO, va="top")


def body(f, x, y, t, fs=9.2, c=INK):
    return f.text(x, y, t, fontsize=fs, color=c, family=MONO, va="top", linespacing=1.55)


def callout(f, x, y, w, h, text, accent=C1, fs=9.2, title=None):
    f.patches.append(FancyBboxPatch((x, y), w, h, transform=f.transFigure,
                                    boxstyle="round,pad=0.006,rounding_size=0.008",
                                    fc="#f2f6fb", ec=accent, lw=1.8, zorder=4))
    ty = y + h - 0.022
    if title:
        f.text(x + 0.014, ty, title, fontsize=10.5, fontweight="bold", color=accent,
               family=MONO, va="top", zorder=6)
        ty -= 0.030
    f.text(x + 0.014, ty, text, fontsize=fs, color=INK, family=MONO, va="top",
           linespacing=1.5, zorder=6)


def table(ax, cells, cols, bbox, fs=8.6, colw=None, colcolor=None):
    t = ax.table(cellText=cells, colLabels=cols, cellLoc="center", bbox=bbox)
    t.auto_set_font_size(False); t.set_fontsize(fs)
    for (r, c), cl in t.get_celld().items():
        cl.set_edgecolor("#8fa3b8"); cl.set_linewidth(0.8)
        if colw: cl.set_width(colw[c])
        if r == 0:
            cl.set_facecolor(INK); cl.set_text_props(color="white", fontweight="bold", fontsize=fs - .4)
        else:
            cl.set_facecolor("#f4f7fb" if r % 2 else "white")
            if colcolor and c in colcolor: cl.set_text_props(color=colcolor[c], fontweight="bold")
    return t


def hdim(ax, y, x0, x1, lab, tick=None, below=True, fs=8.5):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.15))
    if tick is not None:
        for x in (x0, x1):
            ax.plot([x, x], [tick, y + 3 * (-1 if below else 1)], color=DIMC, lw=.55, ls=(0, (4, 3)))
    ax.text((x0 + x1) / 2, y + (-6 if below else 5), lab, ha="center",
            va="top" if below else "bottom", fontsize=fs, color=DIMC, family=MONO)


def vdim(ax, x, y0, y1, lab, tick=None, fs=8.5):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=1.15))
    if tick is not None:
        for y in (y0, y1):
            ax.plot([tick, x + 3], [y, y], color=DIMC, lw=.55, ls=(0, (4, 3)))
    ax.text(x + 3.5, (y0 + y1) / 2, lab, rotation=90, ha="center", va="center",
            fontsize=fs, color=DIMC, family=MONO)


def leader(ax, xy, xyt, lab, fs=8.4, ha="left", col=DIMC):
    ax.annotate(lab, xy, xyt, arrowprops=dict(arrowstyle="->", color=col, lw=.95),
                fontsize=fs, color=col, family=MONO, ha=ha, va="center")


def load(n):
    p = os.path.join(STL, n)
    return trimesh.load(p, force="mesh") if os.path.exists(p) else None


def strip(fig, mesh, rect, names, label, px=780):
    if mesh is None:
        fig.text(rect[0], rect[1] + rect[3] / 2, "STL missing", color=DIMC, family=MONO); return
    vs = [v for v in R.VIEWS if v[0] in names]
    paths = R.render_views(mesh, os.path.join(IMG, label), views=vs, px=px)
    w = rect[2] / len(paths)
    for i, p in enumerate(paths):
        a = fig.add_axes([rect[0] + i * w, rect[1], w * .97, rect[3]])
        a.imshow(mpimg.imread(p)); a.axis("off")
        a.set_title(vs[i][0].upper(), fontsize=8.6, color=GREY, family=MONO, pad=2)


QTY = {"drum.stl": 1, "cradle.stl": 1, "motor_mount.stl": 4}


def manifest():
    rows, tot = [], 0.0
    for f in sorted(os.listdir(STL)):
        if not f.endswith(".stl"): continue
        m = trimesh.load(os.path.join(STL, f), force="mesh")
        b = m.bounds[1] - m.bounds[0]
        q = QTY.get(f, 1)
        g = m.volume / 1000 * .35 * 1.24 * q
        fits = "—" if f.startswith("assembly") else (
            "OK" if all(b[i] <= ENV[i] + .01 for i in range(3)) else "OVER")
        if not f.startswith("assembly"): tot += g
        rows.append([f[:-4], str(q), f"{b[0]:.0f}×{b[1]:.0f}×{b[2]:.0f}",
                     f"{m.volume/1000:.0f}", f"{g:.0f} g", fits])
    return rows, tot

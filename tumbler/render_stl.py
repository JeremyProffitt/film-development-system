"""
Deterministic multi-view STL renderer.

No OpenGL: shades triangles with matplotlib's 3D axes using a Lambert term on
the face normals, so it runs headless and gives identical output every run.

    render_views(mesh_or_path, out_prefix, views=..., px=1400)
    turntable(mesh_or_path, out_dir, frames=120)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

INK = "#10243b"
BASE = np.array([0.42, 0.56, 0.72])      # part colour
LIGHT = np.array([0.35, 0.45, 0.82])     # light direction
LIGHT = LIGHT / np.linalg.norm(LIGHT)

VIEWS = [("iso",      24, -58),
         ("front",     0, -90),
         ("side",      0,   0),
         ("top",      89, -90),
         ("under",   -28, -58),
         ("iso-rear",  24, 122)]


def _load(m):
    if isinstance(m, (str, os.PathLike)):
        m = trimesh.load(str(m), force="mesh")
    return m


def _shade(mesh):
    n = mesh.face_normals
    lam = np.clip(n @ LIGHT, 0.0, 1.0)
    amb = 0.34
    shade = amb + (1.0 - amb) * lam
    cols = np.clip(BASE[None, :] * shade[:, None], 0, 1)
    return np.concatenate([cols, np.ones((len(cols), 1))], axis=1)


def _draw(ax, mesh, elev, azim):
    tris = mesh.vertices[mesh.faces]
    pc = Poly3DCollection(tris, facecolors=_shade(mesh), linewidths=0)
    pc.set_edgecolor("none")
    ax.add_collection3d(pc)
    lo, hi = mesh.bounds
    ctr = (lo + hi) / 2.0
    r = float(np.max(hi - lo)) / 2.0 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def render_views(mesh, out_prefix, views=VIEWS, px=1200, title=None):
    mesh = _load(mesh)
    paths = []
    for name, elev, azim in views:
        fig = plt.figure(figsize=(px / 150.0, px / 150.0), dpi=150, facecolor="white")
        ax = fig.add_subplot(111, projection="3d", facecolor="white")
        _draw(ax, mesh, elev, azim)
        if title:
            fig.text(0.5, 0.055, f"{title} — {name}", ha="center", fontsize=11,
                     family="monospace", color=INK)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        p = f"{out_prefix}_{name}.png"
        fig.savefig(p, dpi=150, facecolor="white")
        plt.close(fig)
        paths.append(p)
    return paths


def turntable(mesh, out_dir, frames=120, px=900, elev=22):
    mesh = _load(mesh)
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i in range(frames):
        azim = -180.0 + 360.0 * i / frames
        fig = plt.figure(figsize=(px / 150.0, px / 150.0), dpi=150, facecolor="white")
        ax = fig.add_subplot(111, projection="3d", facecolor="white")
        _draw(ax, mesh, elev, azim)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        p = os.path.join(out_dir, f"f{i:04d}.png")
        fig.savefig(p, dpi=150, facecolor="white")
        plt.close(fig)
        paths.append(p)
    return paths


def encode(frame_dir, out_mp4, fps=30):
    """Encode a frame folder to H.264 with the bundled ffmpeg."""
    import subprocess, imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-framerate", str(fps),
           "-i", os.path.join(frame_dir, "f%04d.png"),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
           "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_mp4


if __name__ == "__main__":
    import sys, time
    t = time.time()
    src = sys.argv[1] if len(sys.argv) > 1 else "_smoke.stl"
    m = _load(src)
    print("faces", len(m.faces), "watertight", m.is_watertight)
    print(render_views(m, "_smoke", views=VIEWS[:2]))
    print(f"{time.time() - t:.1f}s")

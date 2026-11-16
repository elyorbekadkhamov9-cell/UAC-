"""Cover illustrations for news and video cards: ball-and-stick renders from real geometry (Å) on the UAC navy ground."""
import sys, numpy as np
sys.path.insert(0, "/home/claude/cp")  # mol3d.py renderer lives with the reel tools
import mol3d
from mol3d import render, _rx, _ry, _rz
from PIL import Image, ImageDraw, ImageFilter
W, H = 960, 600
C = dict(C=(58,58,60), H=(236,236,236), O=(215,32,24), B=(255,170,170), F=(150,225,90), Cl=(40,205,80), Br=(166,61,41), N=(60,90,240), Xe=(70,160,180), Au=(255,200,64), Fe=(224,102,51))
RD = dict(C=0.34, H=0.22, O=0.37, B=0.40, F=0.33, Cl=0.46, Br=0.52, N=0.36, Xe=0.60, Au=0.62, Fe=0.50)
mol3d.COL.update(C); mol3d.RAD.update(RD)
def atom(e, p, **k): return dict(e=e, p=np.asarray(p, float), col=C[e], r=RD[e], **k)
def bg(glow=(0.62, 0.5)):
    y, x = np.mgrid[0:H, 0:W]; g = np.zeros((H, W, 3)); top = np.array([36, 80, 124.]); bot = np.array([16, 38, 62.])
    t = (y / H)[..., None]; g[:] = top * (1 - t) + bot * t
    d = np.hypot((x - glow[0] * W) / W, (y - glow[1] * H) / W); g += (np.array([62, 155, 216.]) * 0.55)[None, None, :] * np.exp(-(d / 0.26) ** 2)[..., None]
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
def put(base, scene, scale, R, cx, cy, size=900, flip=False):
    im, _ = render(scene, size, scale, R)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); a = im.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35)); sh.putalpha(a)
    base.alpha_composite(sh, (int(cx - size / 2 + 10), int(cy - size / 2 + 22))); base.alpha_composite(im, (int(cx - size / 2), int(cy - size / 2)))
def save(base, name): base.convert("RGB").save(f"assets/c/{name}.jpg", quality=86); print(name)
def tet():  # four tetrahedral unit vectors, first along +z
    a = np.arccos(-1 / 3); return [np.array([0, 0, 1.]), *[np.array([np.sin(a) * np.cos(t), np.sin(a) * np.sin(t), np.cos(a)]) for t in (0, 2 * np.pi / 3, 4 * np.pi / 3)]]

# 1. oxoborane parent H-B≡O (linear; B-H 1.167, B-O 1.201)
A = [atom("H", (-1.167, 0, 0)), atom("B", (0, 0, 0)), atom("O", (1.201, 0, 0))]
Bd = [dict(i=0, j=1, kind="single"), dict(i=1, j=2, kind="double", offset=(0, 0.16, 0), r=0.075, r2=0.075), dict(i=1, j=2, kind="double", offset=(0, -0.16, 0), r=0.075, r2=0.075)]
b = bg(); put(b, dict(atoms=A, bonds=Bd), 190, _ry(-0.5) @ _rx(0.35), W * 0.56, H * 0.5); save(b, "oksoboran")

# 2. mirror-image pair CHFClBr (C-H 1.09, C-F 1.36, C-Cl 1.76, C-Br 1.94)
def chfclbr(mirror):
    v = tet(); L = [("H", 1.09), ("F", 1.36), ("Cl", 1.76), ("Br", 1.94)]
    at = [atom("C", (0, 0, 0))] + [atom(e, v[i] * d * (np.array([-1, 1, 1]) if mirror else 1)) for i, (e, d) in enumerate(L)]
    return dict(atoms=at, bonds=[dict(i=0, j=k, kind="single") for k in range(1, 5)])
b = bg((0.5, 0.5)); R = _rx(-1.15) @ _rz(0.5)
put(b, chfclbr(False), 105, R, W * 0.29, H * 0.52, 700); put(b, chfclbr(False), 105, R, W * 0.71, H * 0.52, 700, flip=True)
d = ImageDraw.Draw(b)
for yy in range(40, H - 40, 22): d.line([(W / 2, yy), (W / 2, yy + 11)], fill=(201, 221, 238, 170), width=3)
save(b, "nobel-2026")

# 3. gold: fcc unit cell, a = 4.078
a = 4.078; pts = [(x, y, z) for x in (0, a) for y in (0, a) for z in (0, a)] + [(a / 2, a / 2, 0), (a / 2, a / 2, a), (a / 2, 0, a / 2), (a / 2, a, a / 2), (0, a / 2, a / 2), (a, a / 2, a / 2)]
at = [atom("Au", np.array(p) - a / 2) for p in pts]
ed = [dict(i=i, j=j, kind="single", r=0.05, col0=(201, 221, 238), col1=(201, 221, 238)) for i in range(8) for j in range(i + 1, 8) if abs(np.linalg.norm(np.array(pts[i]) - np.array(pts[j])) - a) < 1e-6]
b = bg(); put(b, dict(atoms=at, bonds=ed), 78, _rx(0.42) @ _ry(0.62), W * 0.6, H * 0.5); save(b, "oltin")

# 4. ferrocene, eclipsed (Fe-ring 1.66, C-C 1.44, C-H 1.08)
Rc = 1.44 / (2 * np.sin(np.pi / 5)); at = [atom("Fe", (0, 0, 0))]; bd = []
for s in (1, -1):
    base_i = len(at)
    for k in range(5):
        t = 2 * np.pi * k / 5; at.append(atom("C", (Rc * np.cos(t), s * 1.66, Rc * np.sin(t))))
    for k in range(5):
        t = 2 * np.pi * k / 5; at.append(atom("H", ((Rc + 1.08) * np.cos(t), s * 1.66, (Rc + 1.08) * np.sin(t))))
        bd += [dict(i=base_i + k, j=base_i + (k + 1) % 5, kind="single"), dict(i=base_i + k, j=base_i + 5 + k, kind="single"),
               dict(i=0, j=base_i + k, kind="single", r=0.035, col0=(201, 221, 238), col1=(201, 221, 238))]
b = bg(); put(b, dict(atoms=at, bonds=bd), 105, _rx(0.32) @ _ry(0.3), W * 0.6, H * 0.5); save(b, "ferrotsen")

# 5. hexacyanoferrate: octahedral Fe(CN)6 (Fe-C 1.93, C-N 1.15)
at = [atom("Fe", (0, 0, 0))]; bd = []
for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
    v = np.array(v, float); i = len(at); at += [atom("C", v * 1.93), atom("N", v * 3.08)]
    bd += [dict(i=0, j=i, kind="single"), dict(i=i, j=i + 1, kind="single", r=0.15)]
b = bg(); put(b, dict(atoms=at, bonds=bd), 72, _rx(0.5) @ _ry(0.65), W * 0.6, H * 0.5); save(b, "oktaedr")

# 6. XeF4, square planar (Xe-F 1.95)
at = [atom("Xe", (0, 0, 0))] + [atom("F", 1.95 * np.array(v, float)) for v in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
b = bg(); put(b, dict(atoms=at, bonds=[dict(i=0, j=k, kind="single") for k in range(1, 5)]), 120, _rx(0.5) @ _ry(0.6), W * 0.6, H * 0.5); save(b, "xef4")

# 7. carbonate, trigonal planar (C-O 1.28)
at = [atom("C", (0, 0, 0))] + [atom("O", 1.28 * np.array([np.cos(t), np.sin(t), 0])) for t in (np.pi / 2, np.pi / 2 + 2 * np.pi / 3, np.pi / 2 + 4 * np.pi / 3)]
b = bg(); put(b, dict(atoms=at, bonds=[dict(i=0, j=k, kind="single", r=0.15) for k in range(1, 4)]), 170, _rx(-0.45) @ _ry(0.35), W * 0.6, H * 0.5); save(b, "karbonat")

# 8. SN2 approach: HO- behind CH3Br (C-Br 1.94, C-H 1.09, O-H 0.96, O...C 3.0 on the Br-C axis)
v = tet(); Rz = _ry(np.pi / 2); dirs = [Rz @ u for u in v]   # first direction now along +x (Br)
at = [atom("C", (0, 0, 0)), atom("Br", dirs[0] * 1.94)] + [atom("H", u * 1.09) for u in dirs[1:]] + [atom("O", (-3.0, 0, 0)), atom("H", (-3.0 - 0.96 * np.cos(1.1), 0.96 * np.sin(1.1), 0))]
bd = [dict(i=0, j=k, kind="single") for k in range(1, 5)] + [dict(i=5, j=6, kind="single")]
b = bg((0.5, 0.5)); put(b, dict(atoms=at, bonds=bd), 110, _rx(0.3) @ _ry(-0.25), W * 0.56, H * 0.5); save(b, "sn2")

# 9. tert-butyl bromide (C-Br 1.97, C-C 1.52, C-H 1.09): the substrate that goes SN1, not SN2
v = tet(); Rz = _ry(np.pi / 2); dirs = [Rz @ u for u in v]
at = [atom("C", (0, 0, 0)), atom("Br", dirs[0] * 1.97)]; bd = [dict(i=0, j=1, kind="single")]
for u in dirs[1:]:
    ci = len(at); c = u * 1.52; at.append(atom("C", c)); bd.append(dict(i=0, j=ci, kind="single"))
    # three H on each methyl, staggered about the C-C axis
    ax = u / np.linalg.norm(u); p = np.cross(ax, [0, 1, 0.3]); p /= np.linalg.norm(p); q = np.cross(ax, p)
    for t in (0, 2 * np.pi / 3, 4 * np.pi / 3):
        h = c + 1.09 * (np.cos(np.radians(70.5)) * ax + np.sin(np.radians(70.5)) * (np.cos(t) * p + np.sin(t) * q))
        at.append(atom("H", h)); bd.append(dict(i=ci, j=len(at) - 1, kind="single"))
b = bg(); put(b, dict(atoms=at, bonds=bd), 120, _rx(0.35) @ _ry(-0.35), W * 0.58, H * 0.5); save(b, "tbubr")

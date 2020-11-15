import sys
import numpy as np
import axi
from stltools import stl, bbox, utils, vecops, matrix

def vertical_stack(ds, spacing=0):
    result = axi.Drawing()
    y = 0
    for d in ds:
        d = d.origin().translate(-d.width / 2, y)
        result.add(d)
        y += d.height + spacing
    return result

stlfile = "pegaso.stl"

per1 = [('y',90.0),('x',45.0)]
rotationsvector = [ [('z',180),('y',90),('x',110),('y',20),('z',-90)],
                    [('z',180),('y',90),('x',180),('z',-90)],
                    [('z',180),('y',90),('x',45),('z',-90)],
                    [('z',180),('y',90),('z',-120)],]

drawings = []

for rotations in rotationsvector:
    # File load
    vertices, _ = stl.readstl(stlfile, 'utf-8')

    # Rotations
    tl = []
    which = {'x': matrix.rotx, 'y': matrix.roty, 'z': matrix.rotz}
    for axis, rot in rotations:
        tl.append(which[axis](rot))
    tr = matrix.concat(*tl)

    # MAGIC
    origbb = bbox.makebb(vertices)
    facets = vertices.reshape((-1, 3, 3))
    normals = np.array([vecops.normal(a, b, c) for a, b, c in facets])
    vertices = vecops.xform(tr, vertices)
    normals = vecops.xform(tr[0:3, 0:3], normals)
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(vertices)
    width = maxx - minx
    height = maxy - miny
    dx = -(minx + maxx) / 2
    dy = -(miny + maxy) / 2
    dz = -maxz
    m = matrix.trans([dx, dy, dz])
    sf = min(200 / width, 200 / height)
    v = matrix.scale(sf, sf)
    v[0, 3], v[1, 3] = 200 / 2, 200 / 2
    mv = matrix.concat(m, v)
    vertices = vecops.xform(mv, vertices)
    facets = vertices.reshape((-1, 3, 3))
    vf = [(f, n, 0.4 * n[2] + 0.5) for f, n in zip(facets, normals) if n[2] > 0]
    fvs = '{:.2f}% of facets is visible'

    def fkey(t):
        (a, b, c), _, _ = t
        return max(a[2], b[2], c[2])

    vf.sort(key=fkey)
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(vertices)
    # s3 = "{:4.2f} {:4.2f} {:4.2f} c {:.3f} {:.3f} f {:.3f} {:.3f} s {:.3f} {:.3f} t"
    # print("\n".join([s3.format(0, 0, 0, a[0], a[1], b[0], b[1], c[0], c[1]) for (a, b, c), z, i in vf]))

    paths = [[(a[0], a[1]), (b[0], b[1]), (c[0], c[1]),(a[0], a[1])] for (a, b, c), z, i in vf]
    d = axi.Drawing(paths)
    d.deduplicatePaths()
    drawings.append(d)


maxh, maxw = (0,0)
for d in drawings:
    if d.height > maxh: maxh = d.height
    if d.width > maxw: maxw = d.width

final = axi.Drawing()
x = 0
y = 0
margin = max(maxh,maxw)*0.05
for d in drawings:
    final.add(d.translate(x*maxw+x*margin,y*maxh+y*margin))
    x = x + 1
    if x >= 2:
        x = 0
        y = y + 1

final.clean()
final = final.scale_to_fit(256,178)


d1 = axi.Drawing(axi.text("Pegasus", axi.ASTROLOGY))
d1 = d1.scale_to_fit_height(5)

final = vertical_stack([d1, final], 11)


final = final.rotate(-90).scale_to_fit(256,178)

final = final.sort_paths()
final = final.join_paths(0.5)
final = final.simplify_paths(0.1) # Prueba a aumentar esto


final.dump_svg(stlfile+".svg",scale=3.779527559,w=256,h=178)

axi.drawGCODE(final,progress=True,slowpen=True)

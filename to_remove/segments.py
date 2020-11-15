import axi
from noise import snoise2

octaves = 3
paths = []
step = 120
space = 5
for i in range(300):
    print(i)

    for n,octave in enumerate([7,4,3,1]):
        path = []
        for j in range((n-1)*step+(n-1)*space,n*step+(n-1)*space):
            h = 0.1*snoise2(100 + j * 0.01, 100 + i * 0.01, octave)
            path.append((j, 2.4*i + h*200))
        paths.append(path)

    


final = axi.Drawing(paths)

final = final.sort_paths()
final = final.join_paths(3)
final = final.simplify_paths(0.1)
final = final.rotate(90).scale_to_fit(256,178)



final.dump_svg(__file__+".svg",scale=3.779527559,w=256,h=178)

axi.drawGCODE(final,progress=True,slowpen=True)

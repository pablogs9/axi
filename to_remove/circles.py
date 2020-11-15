import sys
import numpy as np
import axi
import math
import random
from math import floor


size = 80.0

class Noise:
    def __init__(self,octaves = 1):
        self.p = [int(random.random()*256*100) & 255 for x in range(512)]
        self.octaves = octaves

    def lerp(self,t,a,b):
        return a + t * (b - a)
    
    def grad2d(self, i, x, y):
        v = x if (i & 1 == 0) else y
        return -v if (i & 2 == 0) else v

    def noise2d(self, x2d, y2d):
        X = floor(x2d) & 255
        Y = floor(y2d) & 255
        x = x2d - floor(x2d)
        y = y2d - floor(y2d)
        fx = (3 - 2 * x) * x * x
        fy = (3 - 2 * y) * y * y

        p0 = self.p[X] + Y
        p1 = self.p[X+1] + Y

        return self.lerp(   fy,
                            self.lerp(
                                fx,
                                self.grad2d(self.p[p0],x,y),
                                self.grad2d(self.p[p1],x - 1,y)
                            ),
                            self.lerp(
                                fx,
                                self.grad2d(self.p[p0 + 1],x,y - 1),
                                self.grad2d(self.p[p1 + 1 ],x - 1,y - 1)
                            )
                        )

    def noise(self, x, y, scale=0.5):
        e = 1
        k = 1
        s = 0
        for i in range(self.octaves):
            e = e * scale
            s = s + e * (1 + self.noise2d(k*x,k*y))/2
            k = k * 2
        return s

perlin = Noise(3)

turtle = axi.Turtle()
turtle.penup()

paths = []

for i in range(2200):
    print(i)
    scale = 300
    path = []
    for j in [x/2 for x in list(range(-200,200))]:
        h = perlin.noise(100 + j * 0.01, 100 + i * 0.01, 0.4)
        
        turtle.goto(j, 0.2 * (i-1000) + h * 300 - 100)

        ax = abs(turtle.x)
        ay = abs(turtle.y)

        if (ax**2 + ay**2) < (size/1.5)**2:
            path.append((j, 0.2 * (i-1000) + h * 300 - 100))
            turtle.pendown()
        elif (ax**2 + ay**2) < (size/1.05)**2:
            paths.append(path)
            path = []
            turtle.penup()
        elif (ax**2 + ay**2) < size**2:
            path.append((j, 0.2 * (i-1000) + h * 300 - 100))
            turtle.pendown()
        else:
            paths.append(path)
            path = []
            turtle.penup()
    turtle.penup()
    paths.append(path)
    path = []


final = turtle.drawing
final = axi.Drawing(paths)

final = final.scale_to_fit(256*0.9,178*0.9)
# final = final.sort_paths()
# final = final.join_paths(0.5)
# final = final.simplify_paths(0.1)

final.dump_svg(__file__+".svg",scale=3.779527559,w=256,h=178)

# axi.drawGCODE(final,progress=True,slowpen=False,insertpen=True)

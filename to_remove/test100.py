import sys
import numpy as np
import axi
import math
import random
from math import floor



turtle = axi.Turtle()

turtle.penup()

turtle.goto(-1,-1)

turtle.pendown()

turtle.goto(-1,1)

turtle.goto(1,1)
turtle.goto(1,-1)
turtle.goto(-1,-1)
turtle.goto(-1,1)

turtle.penup()

print(turtle.paths)


final = turtle.drawing
final = final.scale_to_fit(256*0.9,178*0.9)
# final = final.sort_paths()
# final = final.join_paths(0.5)
# final = final.simplify_paths(0.1)

final.dump_svg(__file__+".svg",scale=3.779527559,w=256,h=178)

# axi.drawGCODE(final,progress=True,slowpen=False,insertpen=True)

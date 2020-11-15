import sys
import numpy as np
import axi
import math



x_freq = 1.1    #min=0, max=10, step=0.1
y_freq = 12.5   #min=0, max=20, step=0.5
x_scale = 150   #min=0, max=200, step=10
y_scale = 25    #min=0, max=200, step=10

turtle = axi.Turtle()

turtle.penup()
turtle.goto(-50,-20)
turtle.pendown()

width=11
height=8.5

cubesPerSide=40
cubeSpacing=width/(cubesPerSide)
cubeSize=width/(cubesPerSide*0.95)
minX=-(width)/2 
minY=-(height)/2

def walk():
    for y in range(cubesPerSide):
        for x in range(cubesPerSide):
            turtle.penup()

            turtle.goto(minX+x*cubeSpacing+cubeSpacing/2,minY+y*cubeSpacing+cubeSpacing/2)
            turtle.setheading(math.sin(x_freq*x/cubesPerSide)*x_scale+math.cos(y_freq*(x+y)/cubesPerSide)*y_scale)
            
            turtle.forward(cubeSize/2) 
            turtle.right(90)
            turtle.pendown()
            turtle.forward(cubeSize/2) 
            turtle.right(90)
            turtle.forward(cubeSize)
            turtle.right(90)
            turtle.forward(cubeSize)
            turtle.right(90)
            turtle.forward(cubeSize)
            turtle.right(90)
            turtle.forward(cubeSize/2) 
    return False

while walk():
    pass


final = turtle.drawing.rotate_and_scale_to_fit(11, 8.5, step=90)

final = final.sort_paths()
final = final.join_paths(0.5)
final = final.simplify_paths(0.1)

final.dump_svg(__file__+".svg",w=11, h=8.5)

# axi.drawGCODE(final,progress=True,slowpen=False,insertpen=True)

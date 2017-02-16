import pnglib
import math
import sys
import random

EPSILON = 0.001

gPngColors = { "blue"      : [0, 0, 0xff, 0xff],
           "red"       : [0xff, 0, 0, 0xff],
           "green"     : [0, 0xff, 0, 0xff],
           "light blue": [0x0, 0xcc, 0xff, 0xff],
           "error-color"     : [0xff, 0, 0xff, 0xff]
}

class Vector(object):

    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z) 

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z) 
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class Ray(object):

    def __init__(self, o = (0,0,0), d = (0, 0, -1)):
        self.o = Vector(o[0], o[1], o[2])
        self.d = Vector(d[0], d[1], d[2])

    def __str__(self):
        return "o" + str(self.o) + ", d" + str(self.d)

class ViewPlane(object):

    def __init__(self, width = 800, height = 600, pixelSize = 1):
        self.width  = width 
        self.height = height 
        self.pixelSize = pixelSize 

class ShadeRecord(object):
    
    def __init__(self): 
        self.normal = Vector(0,0,0) 
        self.t      = 0
        self.tmin   = 0
        self.hitPt  = 0

class Sphere(object):

    def __init__(self, radius = 5, center = (0, 0, 0), color = (1, 0, 0)):
        self.radius = radius
        self.center = Vector(center[0], center[1], center[2])
        self.color  = Vector(color[0], color[1], color[2])

    def hit(self, ray, tmin, sr):
        oc = ray.o - self.center
        a = dot(ray.d, ray.d)
        b = 2.0 * dot(oc, ray.d)
        c = dot(oc, oc) - self.radius*self.radius
        discr = b*b - 4.0 * a * c 
        
        if discr < 0.0:
            return False
        else:
            denom = 1.0/(2.0*a)
            t = -b - math.sqrt(discr)*denom

            if t > EPSILON:
                sr.t = t 
                return True

            t = -b + math.sqrt(discr)*denom
            if t > EPSILON:
                sr.t = t
                return True

            return False

def dot(u, v):
    return u.x*v.x + u.y*v.y + u.z*v.z

def cross(u, v):
    return (u.y*v.z - u.z*v.y) + (u.z*v.x - u.x*v.z) + (u.x*v.y - u.y*v.x)

def compute_image(eye):
    pass

def setup_canvas(vp, color):
    canvas = pnglib.PNGCanvas(vp.width, vp.height) 
    canvas.color = color
    canvas.filledRectangle(0, 0, vp.width-1, vp.height-1)
    return canvas
    
def radiance(ray, spheres, sr):
    sr.tmin = 10000.0

    hit = False 
    sr.tmin = 10000.0 

    for sphere in spheres:
        if sphere.hit(ray, 0, sr) and sr.t < sr.tmin:
            sr.tmin = sr.t
            pixel = sphere.color
            hit = True 

    if not hit:
        pixel = Vector(0, 1, 1) 

    return pixel
    """
    for sphere in spheres:
        if sphere.hit(ray, 0, sr) and sr.t > sr.tmin:
            sr.tmin = sr.t
            return sphere.color
    return Vector(0, 1, 1) 
    """

def write_pixel_at(x, y, pixel, canvas):
    r = int(255*pixel.x)
    g = int(255*pixel.y)
    b = int(255*pixel.z)
    canvas.point(x, y, [r, g, b, 0xff])

def give_spheres_random_colors(spheres):
    for sphere in spheres: 
        r = random.uniform(0, 1) 
        g = random.uniform(0, 1)
        b = random.uniform(0, 1)
        sphere.color = Vector(r, g, b) 

def main():
     
    vp     = ViewPlane()
    canvas = setup_canvas(vp, gPngColors["error-color"])
   
    camRay = Ray((0,0,200), (0,0,-1))
    sr     = ShadeRecord()

    spheres = [ Sphere(200, (0, 150, 50)),
                Sphere(100, (0, -75,-50)),
                Sphere( 50, (40, -90, 0)),
                Sphere( 25, (150, -50, -150)),
    ]
    give_spheres_random_colors(spheres) 

    # Main Loop
    for j in range(vp.height):
        for i in range(vp.width):
            pixel = Vector(0,0,0) 
            x = vp.pixelSize* (i - 0.5 * (vp.width - 0.0))
            y = vp.pixelSize* (j - 0.5 * (vp.height - 0.0))

            camRay.o = Vector(x, y, 25)
            camRay.d = Vector(0, 0, -1)
            
            pixel = radiance(camRay, spheres, sr)      
            
            write_pixel_at(i, j, pixel, canvas)

    f = open('test.png', 'wb')
    f.write(canvas.dump())
    f.close()

if __name__ == "__main__":
    main()

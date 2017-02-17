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

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z) 

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z) 
       
    def __mul__(self, c):
        return Vector(self.x*c, self.y*c, self.z*c)

    def __div__(self, c):
        return Vector(self.x/c, self.y/c, self.z/c)


    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class Ray(object):

    def __init__(self, o = (0.0,0.0,0.0), d = (0.0, 0.0, -1.0)):
        self.o = Vector(o[0], o[1], o[2])
        self.d = Vector(d[0], d[1], d[2])

    def __str__(self):
        return "o" + str(self.o) + ", d" + str(self.d)

class ViewPlane(object):

    def __init__(self, width = 800, height = 600, pixelSize = 1):
        self.width  = width 
        self.height = height 
        self.pixelSize = pixelSize
        self.z = 0

class ShadeRecord(object):
    
    def __init__(self): 
        self.normal = Vector(0.0,0.0,0.0) 
        self.t      = 0
        self.tmin   = 0
        self.hitPt  = 0

class Camera(object):

    def __init__(self, vp = ViewPlane(), ray = Ray()):
        self.vp = vp 
        self.ray = ray 

    def set_ray_dir(self, x, y):
        self.ray.d = normalize(Vector(x, y, self.vp.z) - self.ray.o)

class Sphere(object):

    def __init__(self, radius = 5.0, center = (0.0, 0.0, 0.0), color = (1.0, 0.0, 0.0)):
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
                hp = ray.o + ray.d*t
                sr.normal = hp - self.center 
                return True

            t = -b + math.sqrt(discr)*denom
            if t > EPSILON:
                sr.t = t
                hp = ray.o + ray.d*t
                sr.normal = hp - self.center 
                return True

            return False

class Plane(object):

    def __init__(self, normal = (0.0, 1.0, 0.0), 
            center = (0.0, 0.0, 0.0), color = (1.0, 0.0, 0.0)):
        self.normal = Vector(normal[0], normal[1], normal[2])
        self.center = Vector(center[0], center[1], center[2])
        self.color  = Vector(color[0], color[1], color[2])

    def hit(self, ray, tmin, sr):
        denom = dot(ray.d, self.normal)
        if denom != 0.0:
            t = dot(self.center - ray.o, self.normal)/denom

            if t > EPSILON:
                sr.t = t
                sr.normal = self.normal
                return True

        return False


def random_in_unit_sphere():
    while(True):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        z = random.uniform(0, 1)
        d = magnitude(Vector(x, y, z))
        if d <= 1:
            break
    return Vector(x/d, y/d, z/d) 

def lerp(u, v, t):
    return (1.0 - t)*u + t*v 

def dot(u, v):
    return u.x*v.x + u.y*v.y + u.z*v.z

def cross(u, v):
    return (u.y*v.z - u.z*v.y) + (u.z*v.x - u.x*v.z) + (u.x*v.y - u.y*v.x)

def magnitude(u):
    return math.sqrt(dot(u, u))

def normalize(u):
    return u/magnitude(u)

def setup_png_canvas(vp):
    canvas = pnglib.PNGCanvas(vp.width, vp.height) 
    canvas.color = [0xff, 0, 0xff, 0xff]
    canvas.filledRectangle(0, 0, vp.width-1, vp.height-1)
    return canvas
    
def radiance(ray, geometry, sr):
    hit = False 
    sr.tmin = 10000.0 

    for shape in geometry:
        if shape.hit(ray, 0, sr) and sr.t < sr.tmin:
            sr.tmin = sr.t
            pixel = shape.color
            hit = True 

    if not hit:
        pixel = Vector(0, 1, 1) 

    return pixel


def debug_radiance(ray, geometry, sr):
    hit = False 
    sr.tmin = 10000.0 

    for shape in geometry:
        if shape.hit(ray, 0, sr) and sr.t < sr.tmin:
            sr.tmin = sr.t
            pixel = shape.color
            hit = True 

            oneVec =  Vector(1.0, 1.0, 1.0)
            if sr.normal != 0.0:
                normal = normalize(sr.normal) + oneVec
                normal = normal*0.5
                pixel = normal
    if not hit:
        pixel = Vector(0, 1, 1) 

    return pixel




def write_pixel_at(x, y, pixel, canvas):
    r = int(255*pixel.x)
    g = int(255*pixel.y)
    b = int(255*pixel.z)
    canvas.point(x, y, [r, g, b, 0xff])

def give_geometry_random_colors(geometry):
    for shape in geometry: 
        r = random.uniform(0, 1) 
        g = random.uniform(0, 1)
        b = random.uniform(0, 1)
        shape.color = Vector(r, g, b) 


def main(): 
    camera = Camera()
    camera.vp = ViewPlane()
    camera.ray = Ray((0.0,0.0, 250))
    camera.z = -225

    canvas = setup_png_canvas(camera.vp)

    geometry = [Sphere(200, (0, 150, 0)),
                Sphere(100, (0, -175,-50)),
                Sphere( 50, (40, -90, 0)),
                Sphere( 25, (150, -50, -150)),
                
    ]

    give_geometry_random_colors(geometry)  

    sr = ShadeRecord()
    # Main Loop
    for j in range(camera.vp.height):
        for i in range(camera.vp.width):
            pixel = Vector(0,0,0) 
            x = camera.vp.pixelSize * (i - 0.5 * (camera.vp.width - 0.0))
            y = camera.vp.pixelSize * (j - 0.5 * (camera.vp.height - 0.0))

            camera.set_ray_dir(x, y)
            pixel = radiance(camera.ray, geometry, sr)      
            
            write_pixel_at(i, j, pixel, canvas)

    f = open('test.png', 'wb')
    f.write(canvas.dump())
    f.close()

if __name__ == "__main__":
    main()

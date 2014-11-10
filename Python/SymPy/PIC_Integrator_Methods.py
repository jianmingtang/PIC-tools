from sympy import *

# use ipython (qtconsole) for pretty printing
init_printing()

# Set up Sympy symbols
dt = symbols('dt')
Ex,Ey,Ez = symbols('Ex Ey Ez')
Bx,By,Bz = symbols('Bx By Bz')
Vx,Vy,Vz = symbols('Vx Vy Vz')

# Set up some vectors
I = Matrix.eye(3)
E = Matrix(3,1, [Ex,Ey,Ez])
B = Matrix(3,1, [Bx,By,Bz])
V = Matrix(3,1, [Vx,Vy,Vz])

# Tajima Method
R = Matrix([[0,Bz,-By],[-Bz,0,Bx],[By,-Bx,0]])
M = simplify( (I-R*dt/2).inv() )
A = simplify( M.multiply(I+R*dt/2) )
Av = simplify( A.multiply(V) )
ME = simplify( M.multiply(E) * dt)
vv1 = simplify( Av + ME )
vv1

# Boris Method
vm = V + E*dt/2
bt = B*dt/2
tm = (bt).dot(bt)
u1 = simplify( vm + vm.cross(B*dt/2) )
u2 = simplify( u1.cross(B*dt/(1+tm)) )
vv2 = simplify(vm + u2 + E*dt/2)
vv2

# The two results are identical
simplify( vv1 - vv2 )

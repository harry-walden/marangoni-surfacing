import sys

import numpy as np
import dedalus.public as d3

Ma = float(sys.argv[1])
Ma_index = int(sys.argv[2])

# Parameters
Lr, Lz = 10, 20
Nx, Ny, Nz = 64, 64, 128
ts = 0.1
dealias = 3 / 2
stop_sim_time = 1000.0
timestepper = d3.RK222
init_timestep = 0.0005
max_timestep = 0.01
dtype = np.float64

# Bases
coords = d3.CartesianCoordinates('x', 'y', 'z')
dist = d3.Distributor(coords, dtype=dtype)
xbasis = d3.RealFourier(coords['x'], size=Nx, bounds=(-Lr, Lr), dealias=dealias)
ybasis = d3.RealFourier(coords['y'], size=Ny, bounds=(-Lr, Lr), dealias=dealias)
zbasis = d3.ChebyshevT(coords['z'], size=Nz, bounds=(-Lz, 0), dealias=dealias)

# Fields
c = dist.Field(name='c', bases=(xbasis, ybasis, zbasis))
u = dist.VectorField(coords, name='u', bases=(xbasis, ybasis, zbasis))
p = dist.Field(name='p', bases=(xbasis, ybasis, zbasis))
zb = dist.Field(name='zb', bases=())
source = dist.Field(name='source', bases=(xbasis, ybasis, zbasis))
tau_c = dist.Field(name='tau_c', bases=(xbasis, ybasis))
tau_u = dist.VectorField(coords, name='tau_u', bases=(xbasis, ybasis))
tau_c2 = dist.Field(name='tau_c2', bases=(xbasis, ybasis))
tau_inc = dist.Field(name='tau_inc')
tau_stokes = dist.VectorField(coords, name='tau_stokes', bases=(xbasis, ybasis))
tau_int1 = dist.Field(name='tau_int1', bases=(xbasis, ybasis))
tau_int2 = dist.Field(name='tau_int2', bases=(xbasis, ybasis))

# Substitutions
x, y, z = dist.local_grids(xbasis, ybasis, zbasis)
Z = dist.Field(name='Z', bases=zbasis)
Z['g'] = z

hor_gauss = dist.Field(name='hor_gauss', bases=(xbasis, ybasis))
hor_gauss['g'] = np.exp(-(x * x + y * y) / 2 / ts / ts) / (2 * np.pi * ts * ts)

ex, ey, ez = coords.unit_vector_fields(dist)
dx = lambda A: d3.Differentiate(A, coords['x'])
dy = lambda A: d3.Differentiate(A, coords['y'])
dz = lambda A: d3.Differentiate(A, coords['z'])
ux = u @ ex
uy = u @ ey
uz = u @ ez
lift_basis = zbasis.derivative_basis(1)
lift = lambda A: d3.Lift(A, lift_basis, -1)
grad_c = d3.grad(c) + ez * lift(tau_c)
grad_u = d3.grad(u) + ez * lift(tau_u)
Tx = ez @ grad_u @ ex
Ty = ez @ grad_u @ ey
source = hor_gauss * np.exp(-((Z - zb) * (Z - zb)) / 2 / ts / ts) / np.sqrt(2 * np.pi * ts * ts)

# Problem
problem = d3.IVP([c, u, p, zb, tau_c, tau_u, tau_c2, tau_stokes, tau_inc], namespace=locals())

problem.add_equation("dt(c) - div(grad_c) - lift(tau_c2) = -u @ grad_c + source/integ(source)")
problem.add_equation("dt(zb) = integ(uz * source)/integ(source)")

problem.add_equation("div(grad_u) - grad(p) + lift(tau_stokes) = 0")
problem.add_equation("trace(grad_u) + tau_inc = 0")
problem.add_equation("integ(p) = 0")

problem.add_equation("c(z=-Lz) = 0")
problem.add_equation("ez @ grad_c(z=0) = 0")
problem.add_equation("Tx(z=0) + Ma * ex @ grad_c(z=0) = 0")
problem.add_equation("Ty(z=0) + Ma * ey @ grad_c(z=0) = 0")
problem.add_equation("uz(z=0) = 0")
problem.add_equation("uz(z=-Lz) = 0")
problem.add_equation("ux(z=-Lz) = 0")
problem.add_equation("uy(z=-Lz) = 0")

# Solver
solver = problem.build_solver(timestepper)
solver.stop_sim_time = stop_sim_time

zb['g'] = -1

snapshots = solver.evaluator.add_file_handler('snapshots_cts' + str(Ma_index), iter=1)
snapshots.add_task(zb, name='zb')

CFL = d3.CFL(
    solver,
    initial_dt=init_timestep,
    cadence=1,
    safety=0.1,
    threshold=0.0,
    max_change=1.5,
    min_change=0.0,
    max_dt=max_timestep,
)
CFL.add_velocity(u)

try:
    while solver.proceed:
        timestep = CFL.compute_timestep()
        solver.step(timestep)
        if (solver.iteration - 1) % 50 == 0:
            print(f"{solver.sim_time / stop_sim_time * 100:.1f}% // z: {zb['g'][0, 0, 0]}")
        if zb['g'][0, 0, 0] > 0.1:
            print("Interface reached, triggering end of main loop")
            break
finally:
    solver.log_stats()

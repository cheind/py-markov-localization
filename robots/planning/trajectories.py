import numpy as np
import math


class CubicTrajectory:


    def __init__(self, points, dt, velocities):
        
        self.t = np.zeros(len(dt) + 1, dtype=float)
        self.t[1:] = np.cumsum(dt)

        self.solve_for_axis(points, self.t, velocities)

    def solve_for_axis(self, x, t, v):
        n = len(x)
        s = n - 1

        A = np.zeros((4*s, 4*s))
        b = np.zeros(4*s)

        for i in range(s):
            xi = x[i]; xf = x[i+1]
            vi = v[i]; vf = v[i+1]
            ti = t[i]; tf = t[i+1]

            r = 4 * i
            c = 3 * i

            A[r+0, c:c+4] = [1., ti, ti**2, 1*ti**3]; b[r+0] = xi # qi = c0 + c1*ti + c2*ti**2 + c3*ti**3
            A[r+1, c:c+4] = [1., tf, tf**2, 1*tf**3]; b[r+1] = xf # qf = c0 + c1*tf + c2*tf**2 + c3*tf**3
            A[r+2, c:c+4] = [0., 1., 2*ti, 3*ti**2];  b[r+2] = vi # vi = c1 + c2*2ti + c3*3ti**2
            A[r+3, c:c+4] = [0., 1., 2*tf, 3*tf**2];  b[r+3] = vf # vf = c1 + c2*2tf + c3*3tf**2
            
        print(A)
        print(b.T)

        c = np.linalg.solve(A, b)
        print(c)
        print(c[0])
        print(c[0] + c[1]*1 + c[2]*1 + c[3]*1)


traj = CubicTrajectory(np.array([10, 30]), [1], [0, 0])








# from collections import namedtuple



# class LSPBTrajectory:

#     def __init__(self, viapoints, dt, acc):
#         """
#         Params
#         ------
#         viapoints : MxN array
#             Waypoints of path in configuration space of M dimensions. For Cartesian space provide a 2xN array.
#         dt: float or 1x(N-1) array
#             Time between two waypoints.
#         acc: float or 1xN array
#             Default magnitude of accelerations in distance units / s**2.

#         References
#         ----------
#         Kunz, Tobias, and Mike Stilman. Turning paths into trajectories using parabolic blends. Georgia Institute of Technology, 2011.
#         https://smartech.gatech.edu/bitstream/handle/1853/41948/ParabolicBlends.pdf    
#         """

#         self.pos = np.atleast_2d(viapoints).astype(float)
#         self.n = self.pos.shape[1]

#         if np.isscalar(dt):
#             dt = np.repeat(dt, self.n-1)
#         else:            
#             assert len(dt) == self.n-1
#             dt = np.copy(dt)

#         if np.isscalar(acc):
#             acc = np.tile([acc], self.pos.shape)
#         else:
#             acc = np.asarray(acc)
#             assert acc.shape == self.pos.shape
            
#         self.v = np.zeros((self.pos.shape[0], self.n-1))
#         self.lt = np.zeros((self.pos.shape[0], self.n-1))
#         self.a = np.zeros(self.pos.shape)
#         self.bt = np.zeros(self.pos.shape)
        
#         for i in range(self.pos.shape[0]): # For each axis
#             print(self.pos[i, :])
#             r = self.lspb(self.pos[i, :], dt, acc[i, :])
#             print(self.pos[i, :])
#             self.v[i, :] = r.v
#             self.a[i, :] = r.a
#             self.bt[i, :] = r.bt
#             self.lt[i, :] = r.lt


#         self.total_time = np.sum(dt)
#         self.t = np.zeros(len(dt) + 1)
#         self.t[1:] = np.cumsum(dt)

#     LSPBResult = namedtuple('LSPBResult', 'v, a, bt, lt')
#     def lspb(self, pos, dt, acc):
#         n = len(pos)

#         v = np.zeros(n-1, dtype=float)
#         a = np.zeros(n, dtype=float)
#         bt = np.zeros(n, dtype=float)
#         lt = np.zeros(n-1, dtype=float)


#         dpos = np.diff(pos)
#         aa = np.abs(acc)

#         # First segment
#         a[0] = np.sign(dpos[0]) * aa[0]
#         if a[0] != 0.:
#             bt[0] = dt[0] - math.sqrt(dt[0]**2 - (2. * dpos[0]) / a[0]) # what if a == 0?            
#         v[0] = dpos[0] / (dt[0] - 0.5 * bt[0])

#         # Last segment
#         a[-1] = np.sign(-dpos[-1]) * aa[-1]
#         if a[-1] != 0.:
#             bt[-1] = dt[-1] - math.sqrt(dt[-1]**2 + (2. * dpos[-1]) / a[-1])
#         v[-1] = dpos[-1] / (dt[-1] - 0.5 * bt[-1])

#         # Inner segments
#         v[1:-1] = dpos[1:-1] / dt[1:-1]
#         a[1:-1] = np.sign(np.diff(v)) * aa[1:-1]

#         with np.errstate(all='ignore'):
#             mask = a[1:-1] == 0.
#             bt[1:-1] = np.select([mask, ~mask], [0., np.diff(v) / a[1:-1]]) * 0.5

#         # Linear timings
#         lt[:] = dt - bt[:-1] - bt[1:]

#         return LSPBTrajectory.LSPBResult(v=v, a=a, bt=bt, lt=lt)


#     def __call__(self, t):
#         torig = t
#         t = np.atleast_1d(t)
#         assert (t >= 0.).all() and (t <= self.total_time).all()

#         # Find interval associated with t
        
#         #https://github.com/jhu-cisst/cisst/blob/2e90a6b69ac141a0ac386a933ad53d83327d448b/cisstRobot/code/robLSPB.cpp
#         #http://www.ee.nmt.edu/~wedeward/EE570/SP09/gentraj.html
#         i = np.digitize(t, self.t) - 1
#         tf = self.t[i+1] - self.t[i]
#         t = t - self.t[i]
        
#         # Only one of the following will be true for each axis
#         isacc = t < self.bt[:, i]
#         isdeacc = t >= (tf - self.bt[:, i+1])
#         islinear = np.logical_and(~isacc, ~isdeacc)

#         p = (self.pos[:, i] + 0.5 * self.a[:, i] * t**2) * isacc + \
#             (self.pos[:, i] + self.v[:, i] * (t - self.bt[:, i]/2)) * islinear + \
#             (self.pos[:, i+1] + self.a[:, i+1] * (tf-t)**2) * isdeacc

#         """
#         acct = np.minimum(t, self.bt[:, i])
#         lint = np.clip(t - self.bt[:, i], 0., self.lt[:, i])
#         dacct = np.clip(t - (tf - self.bt[:, i+1]), 0., self.bt[:, i+1])

#         # http://www-lar.deis.unibo.it/people/cmelchiorri/Files_Robotica/FIR_07_Traj_1.pdf
 
#         p = self.pos[:, i] + \
#             0.5 * self.a[:, i] * acct**2 + \
#             self.v[:, i] * lint + \
#             self.v[:, i] * dacct + 0.5 * self.a[:, i+1] * dacct**2
#         """
#         return p

# """
# traj = LSPBTrajectory(np.array([
#     [10, 35, 25, 10],
#     [0, 0, 0, 0]
# ]), [2, 1, 3], 50)
# """

# traj = LSPBTrajectory(np.array([10, 35, 25, 10]), [2, 1, 3], 50)


# import matplotlib.pyplot as plt
# t = np.arange(0, 2, 0.01)
# p = traj(t)

# fig, (ax1, ax2) = plt.subplots(2, 1)
# ax1.plot(t, p[0])
# ax2.plot(t[1:], np.diff(p[0]) * 0.01)
# #ax2.plot(t[2:], np.diff(p[0], 2) / 0.01**2)
# plt.show()
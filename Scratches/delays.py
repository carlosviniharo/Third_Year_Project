from robustcontrol.utils import InternalDelay,tf
import matplotlib.pyplot as plt
import numpy as np

s = tf([1, 0], 1)
G = 1/(s + 1)
Q = 1 + 2/s
H = tf(1, 1, deadtime=0.1)
G = InternalDelay(G)
Q = InternalDelay(Q)
H = InternalDelay(H)
one = InternalDelay(tf(1, 1))

M = Q*G/(one + Q*G)
Mdelay = Q*G/(one + Q*G*H)

t = np.linspace(0, 10, 5000)

y = M.simulate(lambda t: [1], t)
ydelay = Mdelay.simulate(lambda t: [1], t)

plt.plot(t, y, t, ydelay)
plt.legend(['Delay-free', 'Delay=0.1s'])
plt.axhline(1)
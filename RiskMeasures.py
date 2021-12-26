import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


np.random.seed(111)

mu = 0
sigma = 1

xLB = -3
xUB = 3

plt.grid()
plt.xlim(xLB,xUB)
plt.ylim(0,0.45)

x = np.linspace(mu + xLB * sigma, mu + xUB * sigma, 100)
normalcurve=stats.norm(mu,sigma)
plt.plot(x,normalcurve.pdf(x),'b')

alpha = 0.95

# Compute alpha VaR
VaR = stats.norm.ppf(alpha, loc = mu, scale = sigma)
print("%s VaR = %s" % (alpha,round(VaR,3)))

# Compute alpha CVaR
CVaR = mu + sigma * stats.norm.pdf(VaR) / (1-alpha)

print("%s CVaR = %s" % (alpha,round(CVaR,3)))

shadedarea=np.arange(VaR,xUB,0.01)
plt.fill_between(shadedarea,normalcurve.pdf(shadedarea),color='r')
plt.axvline(x=CVaR,ymin=0, ymax=0.3, linestyle='dashed', linewidth=3, color='g')
plt.show()

'''
# Generate the random standard normal data
a = np.random.randn(1000)
# Plot its histogram
plt.hist(a, bins=50)
plt.gca().set(title='Histogram');
plt.show()
'''

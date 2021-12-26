# From https://www.quantopian.com/posts/the-efficient-frontier-markowitz-portfolio-optimization-in-python

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(111)

## NUMBER OF ASSETS
n_assets = 4

## NUMBER OF OBSERVATIONS
n_obs = 1000

return_vec = np.random.randn(n_assets, n_obs)

def rand_weights(n):
        ''' Produces n random weights that sum to 1 '''
        k = np.random.rand(n)
        return k / sum(k)

def random_portfolio(returns):
    '''
    Returns the mean and standard deviation of returns for a random portfolio
    '''

    p = np.asmatrix(np.mean(returns, axis=1))
    w = np.asmatrix(rand_weights(returns.shape[0]))
    C = np.asmatrix(np.cov(returns))
    mu = w * p.T
    sigma = np.sqrt(w * C * w.T)
    # This recursion reduces outliers to keep plots pretty
    if sigma > 2:
        return random_portfolio(returns)
    return mu, sigma

# Generate the mean returns and risk for random portfolios:
n_portfolios = 1000
means, stds = np.column_stack([random_portfolio(return_vec) for _ in range(n_portfolios)])

# Plot the frontier
plt.plot(stds, means, 'o', markersize=5)
plt.xlabel('Standard Deviation')
plt.ylabel('Mean')
plt.title('Mean and standard deviation of returns of randomly generated portfolios')
plt.show()

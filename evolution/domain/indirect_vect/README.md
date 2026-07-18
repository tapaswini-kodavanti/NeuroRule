# Indirect Encoding for Vector Optimization

This domain performs vector optimization by encoding the candidates as neural networks with higher dimensionality than the solution space,
to allow the evolutionary process to adapt its operators over time.

The domain has been run on several suites of configs: `default`, `weak_select`, and `gp_mutate`.

`gp_mutate` is the most optimized, so further experiments can use this as a starting point.

For each suite, there are configs for a range of (network depth, network width) pairs, to explore how NN architecture affects performance.

No statistical properties are known yet about the expected convergence.

Most notably, `gp_mutate_1_128.hocon` was able to solve the problem, i.e., achieve fitness of 64 in less than 300 generations.
It is likely that it got lucky.

Ideally, with some minor tuning, a config could be found that always solves the problem in around this much time. 
Then a test could be created to verify that this behavior is preserved.

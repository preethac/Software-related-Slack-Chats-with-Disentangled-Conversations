"""Potentially useful functions for probability, statistics, and machine
learning.  All entropies in this are base 2 unless otherwise specified."""
from __future__ import division

import math
from random import uniform, random, randint
from AIMA import normalize

__all__ = ['log2', 'xlog2x', 'jittered_probs',
    'sample_simplex', 'entropy', 'entropy_of_multinomial',
    'kl_divergence', 'variation_of_information', 'mutual_information',
    'conditional_entropy_X_Given_Y', 'conditional_entropy_Y_Given_X',
    'cumulative_density_function', 'sample_multinomial',
    'sample_log_multinomial']

def log2(x):
    """Returns log base 2 of a number."""
    return math.log(x, 2)

def xlog2x(x):
    """Returns x*log2(x) handling the case where x is 0 correctly."""
    if x == 0:
        return 0
    else:
        return x * log2(x)

def jittered_probs(count, max_jitter=1e-10):
    """Return count jittered probabilities.  This is useful for randomly
    initializing a multinomial over count items when you want the
    probabilities to be almost uniform but a little noise to break ties.
    max_jitter is the maximum (unnormalized) jitter each probability
    can have."""
    weights = [1 + uniform(-max_jitter, max_jitter) for x in range(count)]
    weights_sum = sum(weights)
    return [weight / weights_sum for weight in weights]

def sample_simplex(n):
    """Sample probabilities from an n-simplex uniformly at random.  This,
    like jittered_probs is useful for initializing a multinomial over n
    items, except that the probabilities will be totally random instead
    of more or less uniform."""
    parts = [-math.log(1 - random()) for x in range(n)]
    s = sum(parts)
    return [part / s for part in parts]

def entropy(probabilities):
    """Returns the entropy of a discrete random variable with given 
    probabilities.
    
    Examples:
    >>> entropy((0.5, 0.5))
    1.0
    >>> entropy((0.75, 0.25))
    0.81127812445913283
    >>> entropy((0.1, 0.1, 0.8))
    0.92192809488736227
    """
    entropy = 0
    for prob in probabilities:
        entropy -= xlog2x(prob)
    return entropy

def entropy_of_multinomial(count_seq):
    """Returns the entropy of a multinomial with given event counts.
    
    Examples:
    >>> entropy_of_multinomial((1, 1))
    1.0
    >>> entropy_of_multinomial((1, 2))
    0.91829583405448956
    >>> entropy_of_multinomial((2, 1))
    0.91829583405448956
    >>> entropy_of_multinomial((1, 1, 1))
    1.5849625007211561
    >>> entropy_of_multinomial((1, 1, 1, 1))
    2.0
    >>> entropy_of_multinomial((1, 1, 1, 2))
    1.9219280948873623
    """
    return entropy(normalize(count_seq))

def kl_divergence(p, q):
    """Return the Kullback-Leibler distance between discrete probability
    distributions p and q: D(p || q).  p and q are sequences of floats,
    each summing to 1."""
    bits = 0
    for prob_p, prob_q in zip(p, q):
        if prob_q > 0:
            bits -= prob_p * log2(prob_p / prob_q)
        else:
            raise ValueError("KL divergence isn't well defined if q sequence contains a 0.")
    return bits

def variation_of_information(confusion_dict):
    """VI(X, Y) = H(X | Y) + H(Y | X)
                = H(X) - I(X; Y) + H(Y) - I(X; Y)
                = H(X) + H(Y) - 2I(X; Y)
                = H(X) + H(Y) - 2[H(X) + H(Y) - H(X, Y)]
                = 2H(X, Y) - H(X) - H(Y)"""
    # TODO document better
    from AIMA import DefaultDict
    count_x = DefaultDict(0)
    count_y = DefaultDict(0)
    for (x_key, y_key), count in confusion_dict.items():
        count_x[x_key] += count
        count_y[y_key] += count

    return (2 * entropy_of_multinomial(confusion_dict.values())) - \
           entropy_of_multinomial(count_x.values()) - \
           entropy_of_multinomial(count_y.values())

def mutual_information(confusion_dict):
    """I(X; Y) = H(X) + H(Y) - H(X, Y)"""
    # TODO document
    from AIMA import DefaultDict
    count_x = DefaultDict(0)
    count_y = DefaultDict(0)
    for (x_key, y_key), count in confusion_dict.items():
        count_x[x_key] += count
        count_y[y_key] += count
    return entropy_of_multinomial(count_x.values()) + \
           entropy_of_multinomial(count_y.values()) - \
           entropy_of_multinomial(confusion_dict.values())

def conditional_entropy_X_Given_Y(confusion_dict):
    """H(X|Y) = H(X) - I(X;Y)
              = H(X) - [H(Y)+H(X)-H(Y,X)]
              = H(Y,X) - H(Y)"""
    from AIMA import DefaultDict
    count_y = DefaultDict(0)
    for (x_key, y_key), count in confusion_dict.items():
        count_y[y_key] += count

    return (entropy_of_multinomial(confusion_dict.values())) - \
           entropy_of_multinomial(count_y.values()) 

def conditional_entropy_Y_Given_X(confusion_dict):
    """H(Y|X) = H(Y) - I(Y;X)
              = H(Y) - [H(X)+H(Y)-H(X,Y)]
              = H(X,Y) - H(X)"""
    from AIMA import DefaultDict
    count_x = DefaultDict(0)
    count_y = DefaultDict(0)
    for (x_key, y_key), count in confusion_dict.items():
        count_x[x_key] += count
        count_y[y_key] += count
    joint = entropy_of_multinomial(confusion_dict.values())
    return joint - entropy_of_multinomial(count_x.values())

def cumulative_density_function(probs):
    """Calculates the cumulative densities (the total density up to a
    certain point in the distribution).
    
    >>> cumulative_density_function([0.2, 0.8])
    [0.20000000000000001, 1.0]
    >>> cumulative_density_function([0.2, 0.1, 0.1, 0.6])
    [0.20000000000000001, 0.30000000000000004, 0.40000000000000002, 1.0]
    >>> cumulative_density_function([1.0, 0.0])
    [1.0, 1.0]
    >>> cumulative_density_function([0.0, 1.0])
    [0.0, 1.0]
    """
    totals = []
    total = 0
    for prob in probs:
        total += prob
        totals.append(total)
    return totals

def sample_multinomial(probs):
    """Gives a random sample from the unnormalized multinomial distribution
    probs, returned as the index of the sampled element."""
    norm = sum(probs)
    if norm == 0:
        return randint(0, len(probs) - 1)

    sample = random()
    total = 0.0
    for x, prob in enumerate(probs):
        total += prob / norm
        if sample < total:
            return x
    raise ValueError("Failed to sample from %s, sample was %s, norm was %s" % \
        (probs, sample, norm))

def sample_log_multinomial(probs):
    """Gives a random sample from the unnormalized multinomial distribution
    whose natural logarithm is probs, returned as the index of the sampled
    element."""

    maxElt = max(probs)
    expProbs = [math.exp(p - maxElt) for p in probs]
    return sample_multinomial(expProbs)

if __name__ == "__main__":
    dist = [1, 3, 5]
    print "Sampling from distribution:", dist

    hist = {1:0, 3:0, 5:0}
    samples = 5000
    for x in range(samples):
        hist[dist[sample_multinomial(dist)]] += 1

    normdist = sum(dist)
    for d in dist:
        print "True frequency:", d/normdist, \
              "sampled frequency", hist[d]/samples

    dist = [.8, .2, .5]
    logdist = [math.log(x) for x in dist]
    print "Sampling from logarithmic distribution:", logdist
    hist = dict([(x,0) for x in dist])
    samples = 5000
    for x in range(samples):
        hist[dist[sample_multinomial(dist)]] += 1

    normdist = sum(dist)
    for d in dist:
        print "True frequency:", d/normdist, \
              "sampled frequency", hist[d]/samples
        

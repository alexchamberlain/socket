# Copyright (c) Alex Chamberlain 2012
from __future__ import print_function, division
import random
from math import ceil

def soliton(N, seed):
  prng = random.Random()
  prng.seed(seed)
  while 1:
    x = random.random() # Uniform values in [0, 1)
    i = int(ceil(1/x))       # Modified soliton distribution
    yield i if i <= N else 1 # Correct extreme values to 1

if __name__ == '__main__':
  N = 10
  T = 10 ** 5 # Number of trials
  s = soliton(N, random.randint(0, 2 ** 32 - 1)) # soliton generator
  f = [0]*N                       # frequency counter
  for j in range(T):
    i = next(s)
    f[i-1] += 1

  print("k\tFreq.\tExpected Prob\tObserved Prob\n");

  print("{:d}\t{:d}\t{:f}\t{:f}".format(1, f[0], 1/N, f[0]/T))
  for k in range(2, N+1):
    print("{:d}\t{:d}\t{:f}\t{:f}".format(k, f[k-1], 1/(k*(k-1)), f[k-1]/T))

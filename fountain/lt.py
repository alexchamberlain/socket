# Copyright (c) Alex Chamberlain 2012
from soliton import soliton
import random
from math import ceil, floor
import sys
from pprint import pprint as pp

def lt_encode(source, blocksize=1024):
  prng = random.Random()
  n = len(source)
  N = int(ceil(n/blocksize))
  #print(n)
  #print(N)
  s = soliton(N, prng.randint(0, 2 ** 32 - 1))
  while 1:
    d = next(s)
    seed = prng.randint(0, 2 ** 32 - 1)
    rng  = random.Random(seed)
    r = bytearray(blocksize)
    for k in rng.sample(range(N), d):
      #sys.stdout.write("{:d}\t".format(k))
      offset = k*blocksize
      j      = 0
      end    = min(offset + blocksize, n)
      while offset < end:
        r[j] ^= source[offset]
        offset += 1
        j      += 1
    
    #sys.stdout.write("\n");
    yield {"degree": d, "seed": seed, "data": r}

def pop(s):
  while len(s):
    yield s.pop()

def pop_edges(s):
  while len(s.edges):
    e = s.edges.pop()
    e.edges.remove(s)
    yield e

class node_original:
  def __init__(self, parent, original, i, blocksize=1024):
    self.parent    = parent
    self.known     = False
    self.i         = i
    self.edges     = set() # Set of droplets associated with this block
    self.blocksize = blocksize

    offset         = i*blocksize
    end            = offset + blocksize if offset + blocksize <= parent.n else parent.n
    self.data      = memoryview(original)[i*blocksize:(i+1)*blocksize]
  
  def pop_edges(self):
    while len(self.edges):
      e = self.edges.pop()
      e.edges.remove(self)
      yield e

  def process(self):
    assert(self.known)
    for d in pop_edges(self): # d is for droplet
      for j in range(self.blocksize):
        d.data[j] ^= self.data[j][0]
      if len(d.edges) == 1:
        d.process()

class node_droplet:
  def __init__(self, parent, original_nodes, N, blocksize, degree, seed, data):
    self.parent = parent
    self.seed   = seed
    self.data   = bytearray(data)
    self.edges  = set()

    rng = random.Random(seed)

    for k in rng.sample(range(N), degree):
      #sys.stdout.write("{:d}\t".format(k));
      if not original_nodes[k].known:
        self.edges.add(original_nodes[k])
        original_nodes[k].edges.add(self)
      else:
        for j in range(blocksize):
          self.data[j] ^= original_nodes[k].data[j][0]

    # assert(len(self.edges) == degree) - This isn't true for recurring indices.

    #sys.stdout.write("\n");

    #for e in self.edges:
      #sys.stdout.write("{:d}\t".format(e.i))

    #sys.stdout.write("\n");

    if len(self.edges) == 1:
      self.process()

  def process(self):
    #print(len(self.edges))
    assert(len(self.edges) == 1)
    #print("Processing node {:d}...".format(self.seed))
    e = self.edges.pop() # Reference to original
    e.edges.remove(self)
    if not e.known:
      e.data[:] = self.data
      e.known   = True
      self.parent.unknown_blocks -= 1
      e.process()


class lt_decode:
  def __init__(self, n, blocksize=1024):
    self.N         = int(ceil(n/blocksize))
    self.blocksize = blocksize
    self.n         = n
    self.original  = bytearray(self.N*self.blocksize)
    self.unknown_blocks = self.N
    self.original_nodes = []
    #self.droplets  = []

    for i in range(self.N):
      self.original_nodes.append(node_original(self, self.original, i, blocksize))

  def catch(self, droplet):
    n = node_droplet(self, self.original_nodes, self.N, self.blocksize,
                     droplet['degree'], droplet['seed'], droplet['data'])
    #self.droplets.append(node_droplet(self, self.original_nodes, self.N, self.blocksize,
    #                                  droplet['degree'], droplet['seed'],
    #                                  droplet['data']))

if __name__ == "__main__":
  #from pprint import pprint as pp
  #with open('hello.bin', 'rb') as f:
  with open('testfile.bin', 'rb') as f:
    buf = f.read()

  fountain = lt_encode(buf)
  bucket   = lt_decode(len(buf))

  i = 0
  while bucket.unknown_blocks > 0:
    i += 1
    bucket.catch(next(fountain))
    print("Caught {:d} droplets. There are {:d} unknown blocks.".format(i, bucket.unknown_blocks),
          end='\r')

  assert(bucket.original == buf)
  print("Decoded message of {:d} blocks using {:d} droplets ({:f}%).".format(bucket.N, i, (i*100)/bucket.N))

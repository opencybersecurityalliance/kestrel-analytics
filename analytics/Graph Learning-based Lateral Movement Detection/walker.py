import itertools
import math
import random

import pandas as pd
from joblib import Parallel, delayed

def partition_num(num, workers): 
    if num % workers == 0: 
        return [num // workers] * workers  
    else:
        return [num // workers] * workers + [num % workers]  



class RandomWalker:  
    def __init__(self, G):
        self.G = G
    def deepwalk_walk(self, walk_length, start_node): 
        walk = [start_node]
        while len(walk) < walk_length: 
            cur = walk[-1]  
            cur_nbrs = list(self.G.neighbors(cur))  
            if len(cur_nbrs) > 0:
                walk.append(random.choice(cur_nbrs))  
            else:
                break
        return walk
    def simulate_walks(self, num_walks, walk_length, workers=1, verbose=0):  

        G = self.G

        nodes = list(G.nodes())
        print(nodes)
        results = Parallel(n_jobs=workers, verbose=verbose, )(delayed(self._simulate_walks)(nodes, num, walk_length) for num in
            partition_num(num_walks, workers))

        walks = list(itertools.chain(*results)) 

        print("---------------------")
        print(walks)
        return walks

    def _simulate_walks(self, nodes, num_walks, walk_length, ): 
        walks = []
        for _ in range(num_walks):
            random.shuffle(nodes) 
            for v in nodes:
                walks.append(self.deepwalk_walk(walk_length=walk_length, start_node=v))

        return walks

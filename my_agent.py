from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
from agt_server.agents.test_agents.lsvm.min_bidder.my_agent import MinBidAgent
from agt_server.agents.test_agents.lsvm.jump_bidder.jump_bidder import JumpBidder
from agt_server.agents.test_agents.lsvm.truthful_bidder.my_agent import TruthfulBidder
import time
import os
import random
import gzip
import json
from path_utils import path_from_local_root

from itertools import combinations


NAME = "256-82-5206" # TODO: Please give your agent a NAME

class MyAgent(MyLSVMAgent):
    def setup(self):
        #TODO: Fill out with anything you want to initialize each auction
        self.pref_goods = self.get_goods_in_proximity()
        all_goods = self.get_goods()
        self.good_valuations = self.get_valuations(self.pref_goods)

        self.highest_seen_bid = {g: 0 for g in all_goods}
        self.competition = {g: 0 for g in all_goods}
    
    def national_bidder_strategy(self): 
        # TODO: Fill out with your national bidder strategy
        vals = self.get_valuations()
        min_bids = self.get_min_bids()
        bids = {}
        bundle = [g for g in vals if vals[g] >= min_bids[g]]
        improved = True
        while improved:
            improved = False
            current_util = self.calc_total_utility(bundle)

            for g in list(bundle):
                new_bundle = [x for x in bundle if x != g]
                new_util = self.calc_total_utility(new_bundle)

                if new_util > current_util:
                    bundle.remove(g)
                    improved = True
                    current_util = new_util
        all_goods = self.get_goods()
        current_util = self.calc_total_utility(bundle)

        for g in all_goods:
            if g not in bundle:
                if min_bids[g] > vals[g]:
                    continue

                new_bundle = bundle + [g]
                new_util = self.calc_total_utility(new_bundle)

                if new_util > current_util:
                    bundle.append(g)
                    current_util = new_util
        for g in bundle:
            if min_bids[g] <= vals[g]:
                bids[g] = min_bids[g]

        return self.clip_bids(bids)
    

    def regional_bidder_strategy(self): 
        # TODO: Fill out with your regional bidder strategy
        # Strategy: bid on preferred good and then on the next 6 highest utility adjacent goods
        # # OUR OLD STRATEGY BELOW:
        # min_bids = self.get_min_bids(self.pref_goods)

        # valuations = self.get_valuations(self.pref_goods)
        # bids = {}
        # sketchy_goods = []
        # for good in self.pref_goods:
        #     if(self.get_valuation(good) < min_bids[good]): # always bid when val >= min bid
        #         sketchy_goods.append(good)

        # sketchy_vals = self.get_valuations(sketchy_goods)
        # top_sketchy_goods = sorted(sketchy_vals.keys(), key=lambda g: sketchy_vals[g], reverse=True)
        # if(len(top_sketchy_goods) > 4):
        #     self.pref_goods = [e for e in self.pref_goods if e not in top_sketchy_goods[4:]]
        #     top_sketchy_goods = top_sketchy_goods[:4] # take only top 4
        # combinations_of_sketchy = []
        # for r in range(len(top_sketchy_goods)):
        #     combinations_of_sketchy.extend(list(combinations(top_sketchy_goods, r)))

        # bundle_vals = {}
        # for bundle in combinations_of_sketchy:
        #     new_goods = [e for e in self.pref_goods if e not in bundle]
        #     bundle_vals[bundle] = self.calc_total_utility(new_goods)
        # if(bundle_vals):
        #     best_bundle = max(bundle_vals, key=bundle_vals.get)
        #     #print(best_bundle)
        # else:
        #     best_bundle = []
        
        # self.pref_goods = [e for e in self.pref_goods if e not in best_bundle]

        # # NEW PART: try adding goods in proximity that increase utility
        # goods_to_idx = self.get_goods_to_index()
        # full_proximity = self.get_goods_in_proximity()
        # all_min_bids = self.get_min_bids()

        # current_utility = self.calc_total_utility(self.pref_goods)
        # def are_adjacent(g1, g2):
        #     (x1, y1) = goods_to_idx[g1]
        #     (x2, y2) = goods_to_idx[g2]
        #     return abs(x1 - x2) + abs(y1 - y2) == 1
        # def is_connected_to_some_cluster(bundle, g):
        #     for h in bundle:
        #         if are_adjacent(g, h):
        #             return True
        #     return False
        # for g in full_proximity:
        #     if g not in self.pref_goods:
        #         if not is_connected_to_some_cluster(self.pref_goods, g):
        #             continue

        #         new_bundle = self.pref_goods + [g]
        #         new_utility = self.calc_total_utility(new_bundle)

        #         if new_utility > current_utility:
        #             self.pref_goods.append(g)
        #             current_utility = new_utility

        # for good in self.pref_goods:
        #     bids[good] = all_min_bids[good]


        # # for good in self.pref_goods:
        # #     bids[good] = min_bids[good]

        # # print(self.get_goods_in_proximity())
        # # print(self.pref_goods)
        # # print("----------------------------------------------")
        # #pref_good = self.get_regional_good()
        # #self.proximity()
        # #self.get_goods_to_index()



        #     # else:     
        #     #     print("AAAAAAAAAAAAAAAA")                                      # => someone else wants good
        #     #     new_goods = self.pref_goods.copy().remove(good)
        #     #     if(self.calc_total_utility(self.pref_goods) >= self.calc_total_utility(new_goods)):
        #     #         bids[good] = min_bids[good]
        #     #     else:
        #     #         self.pref_goods.remove(good)
        # return self.clip_bids(bids)

        # # NEW STRATEGY IMPLEMENTATION:
        # min_bids = self.get_min_bids(self.pref_goods)
        # valuations = self.get_valuations(self.pref_goods)
        # bids = {}

        # sketchy_goods = [g for g in self.pref_goods if valuations[g] < min_bids[g]]
        # sketchy_vals = self.get_valuations(sketchy_goods)
        # top_sketchy_goods = sorted(sketchy_vals.keys(), key=lambda g: sketchy_vals[g], reverse=True)
        # if len(top_sketchy_goods) > 4:
        #     top_sketchy_goods = top_sketchy_goods[:4]

        # combinations_of_sketchy = []
        # for r in range(len(top_sketchy_goods) + 1):
        #     combinations_of_sketchy.extend(list(combinations(top_sketchy_goods, r)))

        # bundle_vals = {}
        # for bundle in combinations_of_sketchy:
        #     new_goods = [g for g in self.pref_goods if g not in bundle]
        #     bundle_vals[bundle] = self.calc_total_utility(new_goods)

        # best_bundle = max(bundle_vals, key=bundle_vals.get) if bundle_vals else []
        # self.pref_goods = [g for g in self.pref_goods if g not in best_bundle]

        # if len(self.pref_goods) < 4:
        #     return {}

        # if len(self.pref_goods) >= 6:
        #     return self.clip_bids({
        #         g: min(self.get_min_bids()[g], self.get_valuation(g))
        #         for g in self.pref_goods
        #         if self.get_valuation(g) >= self.get_min_bids()[g] 
        #     })

        # goods_to_idx = self.get_goods_to_index()
        # full_proximity = self.get_goods_in_proximity()
        # all_min_bids = self.get_min_bids()
        # all_vals = self.get_valuations()

        # current_utility = self.calc_total_utility(self.pref_goods)

        # def are_adjacent(g1, g2):
        #     (x1, y1) = goods_to_idx[g1]
        #     (x2, y2) = goods_to_idx[g2]
        #     return abs(x1 - x2) + abs(y1 - y2) == 1

        # def is_connected(bundle, g):
        #     return any(are_adjacent(g, h) for h in bundle)

        # for g in full_proximity:
        #     if g in self.pref_goods:
        #         continue

        #     if all_vals[g] < all_min_bids[g]:
        #         continue

        #     if not is_connected(self.pref_goods, g):
        #         continue

        #     if len(self.pref_goods) >= 6:
        #         break
        #     new_bundle = self.pref_goods + [g]
        #     new_utility = self.calc_total_utility(new_bundle)

        #     if new_utility > current_utility:
        #         self.pref_goods.append(g)
        #         current_utility = new_utility
        # for g in self.pref_goods:
        #     if all_vals[g] >= all_min_bids[g]:
        #         bids[g] = all_min_bids[g]

        # return self.clip_bids(bids)

        # # JUMP BIDDING STRATEGY:
        # if self.get_current_round() == 1:
        #     vals = self.get_valuations()
        #     min_bids = self.get_min_bids()
        #     bids = {}

        #     for g in self.pref_goods:
        #         jump_price = int(vals[g] * random.uniform(0.75, 1.05))
        #         jump_price = max(jump_price, min_bids[g])

        #         bids[g] = jump_price
        #     # print("JUMP BIDDING:", bids)

        #     return self.clip_bids(bids)

        # losing_goods = [g for g in self.pref_goods if self.competition[g] >= 2]
        # self.pref_goods = [g for g in self.pref_goods if g not in losing_goods]

        # vals = self.get_valuations()
        # min_bids = self.get_min_bids()
        # bids = {}

        # if len(self.pref_goods) < 4:
        #     return {}
        # if len(self.pref_goods) >= 6:
        #     for g in self.pref_goods:
        #         if vals[g] >= min_bids[g]:
        #             bids[g] = min_bids[g]
        #     return self.clip_bids(bids)

        # goods_to_idx = self.get_goods_to_index()
        # proximity = self.get_goods_in_proximity()

        # def adjacent(g1, g2):
        #     (x1, y1) = goods_to_idx[g1]
        #     (x2, y2) = goods_to_idx[g2]
        #     return abs(x1 - x2) + abs(y1 - y2) == 1

        # def touches_cluster(g):
        #     return any(adjacent(g, h) for h in self.pref_goods)

        # current_util = self.calc_total_utility(self.pref_goods)

        # for g in proximity:
        #     if g in self.pref_goods:
        #         continue
        #     if vals[g] < min_bids[g]:
        #         continue
        #     if not touches_cluster(g):
        #         continue

        #     if len(self.pref_goods) >= 6:
        #         break

        #     new_goods = self.pref_goods + [g]
        #     new_util = self.calc_total_utility(new_goods)

        #     if new_util > current_util:
        #         self.pref_goods.append(g)
        #         current_util = new_util

        # for g in self.pref_goods:
        #     if vals[g] >= min_bids[g]:
        #         bids[g] = min_bids[g]

        # return self.clip_bids(bids)

# # OTHER STRATEGY -----------------------------------
#         vals = self.get_valuations()
#         min_bids = self.get_min_bids()
#         goods_to_idx = self.get_goods_to_index()
#         all_goods = self.get_goods()

#         scores = {}
#         for g in all_goods:
#             scores[g] = vals[g] - min_bids[g]

#         ranked = sorted(all_goods, key=lambda g: scores[g], reverse=True)

#         candidates = ranked[:10]

#         def adjacent(a, b):
#             (x1, y1) = goods_to_idx[a]
#             (x2, y2) = goods_to_idx[b]
#             return abs(x1 - x2) + abs(y1 - y2) == 1

#         cluster = [candidates[0]]  # best good first

#         def connected_to_cluster(g):
#             return any(adjacent(g, h) for h in cluster)

#         for g in candidates[1:]:
#             if connected_to_cluster(g):
#                 cluster.append(g)
#             if len(cluster) == 10:
#                 break

#         final_bundle = []
#         for g in cluster:
#             if vals[g] >= min_bids[g]:
#                 final_bundle.append(g)
#         bids = {g: min_bids[g] for g in final_bundle}
#         return self.clip_bids(bids)



# MARGINAL VALUES STRATEGY
        bids = {}
        min_bids = self.get_min_bids()

        total_utility = self.calc_total_utility(self.pref_goods)
        for good in self.pref_goods:
            new_goods = self.pref_goods.copy().remove(good)
            marginal_utility = total_utility - self.calc_total_utility(new_goods)
            # print(marginal_utility)
            # print(self.get_valuation(good))
            # print("----------------------------------")
            self.good_valuations[good] = max(marginal_utility, self.get_valuation(good))

        # for good in self.pref_goods:
            if self.good_valuations[good] >= min_bids[good]:
                bids[good] = min_bids[good]
            else:
                self.pref_goods.remove(good)
        return self.clip_bids(bids)

    # def local_bid(self, n, alpha):
    #     total_utility = self.calc_total_utility(self.pref_goods)

    #     for good in self.pref_goods:
    #         for i in range(n):
    #             new_goods = self.pref_goods.copy().remove(good)
    #             marginal_utility = total_utility - self.calc_total_utility(new_goods)
    #             print(marginal_utility)
    #             print(self.get_valuation(good))
    #             print("----------------------------------")
    #             self.good_valuations[good] =  max(marginal_utility, self.get_valuation(good))


        
    def get_bids(self):
        if self.is_national_bidder(): 
            return self.national_bidder_strategy()
        else: 
            return self.regional_bidder_strategy()
    
    def update(self):
        #TODO: Fill out with anything you want to update each round
        min_bids = self.get_min_bids()

        for g, price in min_bids.items():
            if g not in self.highest_seen_bid:
                self.highest_seen_bid[g] = price
            else:
                if price > self.highest_seen_bid[g]:
                    self.highest_seen_bid[g] = price
                    self.competition[g] += 1
        # pass 

    def teardown(self):
        #TODO: Fill out with anything you want to run at the end of each auction
        print(self.get_goods_in_proximity())
        print(self.pref_goods)
        print("----------------------------------------------")

################### SUBMISSION #####################
my_agent_submission = MyAgent(NAME)
####################################################


def process_saved_game(filepath): 
    """ 
    Here is some example code to load in a saved game in the format of a json.gz and to work with it
    """
    print(f"Processing: {filepath}")
    
    # NOTE: Data is a dictionary mapping 
    with gzip.open(filepath, 'rt', encoding='UTF-8') as f:
        game_data = json.load(f)
        for agent, agent_data in game_data.items(): 
            if agent_data['valuations'] is not None: 
                # agent is the name of the agent whose data is being processed 
                agent = agent 
                
                # bid_history is the bidding history of the agent as a list of maps from good to bid
                bid_history = agent_data['bid_history']
                
                # price_history is the price history of the agent as a list of maps from good to price
                price_history = agent_data['price_history']
                
                # util_history is the history of the agent's previous utilities 
                util_history = agent_data['util_history']
                
                # util_history is the history of the previous tentative winners of all goods as a list of maps from good to winner
                winner_history = agent_data['winner_history']
                
                # elo is the agent's elo as a string
                elo = agent_data['elo']
                
                # is_national_bidder is a boolean indicating whether or not the agent is a national bidder in this game 
                is_national_bidder = agent_data['is_national_bidder']
                
                # valuations is the valuations the agent recieved for each good as a map from good to valuation
                valuations = agent_data['valuations']
                
                # regional_good is the regional good assigned to the agent 
                # This is None in the case that the bidder is a national bidder 
                regional_good = agent_data['regional_good']
            
            # TODO: If you are planning on learning from previously saved games enter your code below. 
            
            
        
def process_saved_dir(dirpath): 
    """ 
     Here is some example code to load in all saved game in the format of a json.gz in a directory and to work with it
    """
    for filename in os.listdir(dirpath):
        if filename.endswith('.json.gz'):
            filepath = os.path.join(dirpath, filename)
            process_saved_game(filepath)
            

if __name__ == "__main__":
    
    # Heres an example of how to process a singular file 
    # process_saved_game(path_from_local_root("saved_games/2024-04-08_17-36-34.json.gz"))
    # or every file in a directory 
    # process_saved_dir(path_from_local_root("saved_games"))
    
    ### DO NOT TOUCH THIS #####
    agent = MyAgent(NAME)
    arena = LSVMArena(
        num_cycles_per_player = 3,
        timeout=1,
        local_save_path="saved_games",
        players=[
            agent,
            MyAgent("CP - MyAgent"),
            MyAgent("CP2 - MyAgent"),
            MyAgent("CP3 - MyAgent"),
            MinBidAgent("Min Bidder"), 
            JumpBidder("Jump Bidder"), 
            TruthfulBidder("Truthful Bidder"), 
        ]
    )
    
    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")

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
         
    
    def national_bidder_strategy(self): 
        # TODO: Fill out with your national bidder strategy
        # Strategy: Target the 6 highest-valued goods and bid just above min_bid + epsilon if valuation > min_bid
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        bids = {} 
        top_goods = sorted(valuations.keys(), key=lambda g: valuations[g], reverse=True)
        targets = top_goods[:6]
        current_bundle = self.get_tentative_allocation()
        current_bundle_val = [valuations[g] for g in current_bundle]
        total_val = sum(current_bundle_val)
        mean_val = total_val / len(current_bundle) if len(current_bundle) > 0 else 0

        # for g in targets:
        #     val = valuations[g]
        #     min_bid = min_bids[g]
        #     bon = 0.3 * mean_val
            
        #     if bon + val > min_bid:
        #         bids[g] = max(min_bid + 0.6 * (bon + val - min_bid), min_bid)
        # bids = self.clip_bids(bids)
        # return bids

        for good in top_goods:
            if(self.get_valuation(good) >= min_bids[good]):
                bids[good] = min_bids[good]
        return self.clip_bids(bids)

    def regional_bidder_strategy(self): 
        # TODO: Fill out with your regional bidder strategy
        # Strategy: bid on preferred good and then on the next 6 highest utility adjacent goods
        min_bids = self.get_min_bids(self.pref_goods)

        valuations = self.get_valuations(self.pref_goods)
        bids = {}
        sketchy_goods = []
        for good in self.pref_goods:
            if(self.get_valuation(good) < min_bids[good]): # always bid when val >= min bid
                sketchy_goods.append(good)

        sketchy_vals = self.get_valuations(sketchy_goods)
        top_sketchy_goods = sorted(sketchy_vals.keys(), key=lambda g: sketchy_vals[g], reverse=True)
        if(len(top_sketchy_goods) > 4):
            self.pref_goods = [e for e in self.pref_goods if e not in top_sketchy_goods[4:]]
            top_sketchy_goods = top_sketchy_goods[:4] # take only top 4
        combinations_of_sketchy = []
        for r in range(len(top_sketchy_goods)):
            combinations_of_sketchy.extend(list(combinations(top_sketchy_goods, r)))

        bundle_vals = {}
        for bundle in combinations_of_sketchy:
            new_goods = [e for e in self.pref_goods if e not in bundle]
            bundle_vals[bundle] = self.calc_total_utility(new_goods)
        if(bundle_vals):
            best_bundle = max(bundle_vals, key=bundle_vals.get)
            #print(best_bundle)
        else:
            best_bundle = []
        
        self.pref_goods = [e for e in self.pref_goods if e not in best_bundle]

        for good in self.pref_goods:
            bids[good] = min_bids[good]

        # print(self.get_goods_in_proximity())
        # print(self.pref_goods)
        # print("----------------------------------------------")
        #pref_good = self.get_regional_good()
        #self.proximity()
        #self.get_goods_to_index()



            # else:     
            #     print("AAAAAAAAAAAAAAAA")                                      # => someone else wants good
            #     new_goods = self.pref_goods.copy().remove(good)
            #     if(self.calc_total_utility(self.pref_goods) >= self.calc_total_utility(new_goods)):
            #         bids[good] = min_bids[good]
            #     else:
            #         self.pref_goods.remove(good)
        return self.clip_bids(bids)

    def get_bids(self):
        if self.is_national_bidder(): 
            return self.national_bidder_strategy()
        else: 
            return self.regional_bidder_strategy()
    
    def update(self):
        #TODO: Fill out with anything you want to update each round
        pass 

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

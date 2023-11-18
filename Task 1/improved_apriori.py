from itertools import combinations
from tqdm import tqdm
import time 
import collections
# Implementation of the paper AN IMPROVED APRIORI ALGORITHM FOR ASSOCIATION RULES with modifications
class Improved_Apriori:
    def __init__(self, data, min_support, min_confidence=1, verbose=0):
        self.data = data
        # Support is the the ratio of the number of transactions that contain an itemset.
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.verbose = verbose
 

    # Generate the frequent 1-itemset
    def generate_L1_transaction_dict(self):
        
        # This is equivalent to the item frequency which >= min_support 
        L1 = {}
        transaction_id_dict = collections.defaultdict(list)
        """
        Assumptions on dataset is such that

        Transaction ID : Items
        
        where data is a dictionary. Key is transaction id and items is a list
        """
        
        for transaction_id in self.data:
            # In a transaction set, an item only appears once in a itemsets
            transaction_set = set(self.data[transaction_id])
            for item in transaction_set:
                item_tuple = (item,)
                L1[item_tuple] = L1.get(item_tuple, 0) + 1
                transaction_id_dict[item_tuple].append(transaction_id)
        # Based on the minimum support value, we filter to form the frequent itemset
        if(self.verbose > 0):
            print(f"Found {len(L1)} candidate itemsets from 1st Level")
        L1 = {item: freq for item, freq in L1.items() if freq/len(self.data) >= self.min_support}
        L1 = {k: L1[k] for k in sorted(L1)}

        # Filter transaction_id_dict
        transaction_id_dict = {item: transaction_ids for item, transaction_ids in transaction_id_dict.items() if item in L1}

        return L1, transaction_id_dict
    
    def generate_L2_candidates(self, L1, k):
        """
        This function generate the 2-itemset candidates set from the 1 item frequent itemset
        """
        # print(f'L1: {L1}')
        candidate_sets = list(combinations(L1, k))
   
        return candidate_sets

    def generate_candidates(self, Lk_minus_one, k):

        """
        This function generate the k-item candidates set from k-1 frequent itemset. 
        Explained in lecture
        
        """
        candidate_sets = []
     
        item_counts = {}

        for frequent_itemset in Lk_minus_one:
            for item in frequent_itemset:
                item_counts[item] = item_counts.get(item, 0)+1
     
        len_Lk_minus_one = len(Lk_minus_one)
        # For each itemset in Lk_minus_one, join it with every other itemset
        for i in range(0, len_Lk_minus_one):
            for j in range(i+1, len_Lk_minus_one):
                # Only combine sets if their first item from k-1 itemset are equal
                if Lk_minus_one[i][:-1] == Lk_minus_one[j][:-1]:
                    candidate = tuple(sorted(Lk_minus_one[i] + Lk_minus_one[j][-1:]))
                    candidate_sets.append(candidate)
        
        return candidate_sets
    
    def prune_candidates(self, Lk_minus_one, candidate_sets):
        """
        This functions upholds Apriori Property 
        
        """
        pruned_candidate_sets = []
        for candidate in candidate_sets:
    
            for i in range(len(candidate) - 2):
                removed = candidate[:i] + candidate[i + 1 :]
                if removed not in Lk_minus_one:
                    break
            else:
                pruned_candidate_sets.append(candidate)

        return pruned_candidate_sets
    
    def determine_frequent_itemset(self, candidate_set, L1, transaction_ids_dict):

        """
        This approach greatly reduces the amount of transactions required to compute the support count.
        Mainly, we just need to get the transaction IDs where all the items in a candidate is presents
        """
        transaction_ids = set(transaction_ids_dict[((candidate_set[0],))])
        for i in range(1,len(candidate_set)):
            # We are only interested in the transactions where all the items in the candidate set are present
            # This reduces the time taken to compute the count of the itemset
            # Overlap strategy 
            transaction_ids = transaction_ids.intersection(set(transaction_ids_dict[((candidate_set[i],))]))

        if(len(transaction_ids)/len(self.data) < self.min_support):
            return False, None

        return True, transaction_ids
    

    def apriori(self):
        # Retrieve the transaction ids once 
        L1, transaction_ids_dict = self.generate_L1_transaction_dict()
        if(self.verbose > 0):
            print(f"Found {len(L1)} frequent itemsets from 1th item candidate sets")
        #print(f'Transaction ID Dictionary: {transaction_ids_dict}')
        L = [L1]
        L1_str = [item[0] for item in L1.keys()]
        # Kth-frequent itemset
        k = 2
        
        while len(L[k-2]) > 0:
            start_time = time.time()
            if(k==2):
                candidate_sets = self.generate_L2_candidates(L1_str, k)
            else:
                #Generate candidates based of k-1 frequent itemsets instead of L1
                not_pruned_candidate_sets = self.generate_candidates(list(L[k-2].keys()),k)
                candidate_sets = self.prune_candidates(list(L[k-2].keys()),not_pruned_candidate_sets)
            if(self.verbose > 0):
                print(f"Found {len(candidate_sets)} candidates for {k}th item candidate sets")
                #print(f'Candidate Sets for {k}th itemset : {candidate_sets}')
            end_time = time.time()

            counts = {}

            if(self.verbose > 0):
                print(f"Time taken to find {k}th item candidate sets: {end_time-start_time}")

            for candidate in tqdm(candidate_sets):
                above_min, ids = self.determine_frequent_itemset(candidate,L1, transaction_ids_dict)
                if(above_min):
                    counts[candidate] = len(ids)


            # The bottleneck is here, unsure if there is a way to get the count of the itemset fast
            # for idx, itemset in enumerate(tqdm(candidate_sets)):
            #     if idx < len(transaction_ids):
            #         transactions = transaction_ids[idx]
            #         for transaction in transactions:
            #             if(set(itemset).issubset(set(self.data[transaction]))):
            #                 counts[itemset] = counts.get(itemset, 0) + 1


            # print(f"Counts at {k}: {counts}")

            Lk = {itemset: count for itemset, count in counts.items() if count/len(self.data) >= self.min_support}
            #print(Lk)
            if(self.verbose > 0):
                print(f"Found {len(Lk)} frequent itemsets from {k}th item candidate sets")
                #print(f'Frequent Itemsets for {k}th itemset : {Lk}')
            L.append(Lk)
            k += 1
        

        
        frequent_itemset_dict = {}
        for level in range(len(L[:-1])): 
            frequent_itemset_dict[level+1] = L[level]
        return frequent_itemset_dict




    



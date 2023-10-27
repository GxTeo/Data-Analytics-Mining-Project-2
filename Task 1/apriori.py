from itertools import combinations
from tqdm import tqdm

class Apriori:
    def __init__(self, data, min_support, min_confidence):
        self.data = data
        # Support is the the ratio of the number of transactions that contain an itemset.
        self.min_support = min_support
        self.min_confidence = min_confidence

    # Generate support count of each item in dataset (Candidate Set 1)
    def item_frequency(self):
        # Dictionary to store Item: Frequency 
        items_freq = {}
        """
        Assumptions on dataset is such that

        Transaction ID : Items
        
        where data is a dictionary. Key is transaction id and items is a list
        """
        for transaction_id in self.data:
            for item in self.data[transaction_id]:
                item_tuple = (item,)
                items_freq[item_tuple] = items_freq.get(item_tuple, 0) + 1
        # Based on the minimum support value, we filter the candidate set
        return {item: freq for item, freq in items_freq.items() if freq/len(self.data) >= self.min_support}
    
    
    def apriori_property(self, previous_candidates, subsets):
        """
        Apriori property states that all non-empty subsets of a frequent itemsets must also be frequent.
        Implemented this to reduce computational expenses instead of brute force
        """
        for subset in subsets:
            if subset not in previous_candidates:
                return False
        return True

    # Reduce transaction that has less than n items for nth level
    def transaction_reduction(self, frequent_items):
        """
        This function reduces the number of transactions by removing 
        the transactions that do not contain any frequent items.
        """
        # Dictionary to store the reduced transactions
        reduced_transactions = {}
        print(f'Frequent Items {frequent_items}')
        for transaction_id, items in self.data.items():
            # Convert items to a set for faster intersection operation
            items_set = set(items)
            
            # Check if the transaction contains any frequent item
            for item in items_set:
                for candidate_set in frequent_items:
                    if(item in candidate_set):
                        # If it does, add it to the reduced transactions
                        reduced_transactions[transaction_id] = items
                        break
        return reduced_transactions

    # Generate candidate sets which is the pairs/groups of item based on previous candidates set
    def generate_candidate_sets(self, previous_candidates, count):
        candidate_final_sets = []
        candidate_sets_freq = {}

        # Form the candidate sets
        # print(f"Previous Candidate at level {count-1}: ", previous_candidates)
        candidate_sets = []
        for i in range(len(previous_candidates)):
            for j in range(i+1, len(previous_candidates)):
                if previous_candidates[i][:-1] == previous_candidates[j][:-1]:
                    candidate_sets.append(previous_candidates[i] + (previous_candidates[j][-1],))

        # print(f"Candidate Sets at level {count}: ",candidate_sets)
        for itemset in candidate_sets:
            subsets = list(combinations(itemset, count-1))
            # Check for Apriori property where all non-empty subsets of a frequent itemset must also be frequent
            check = self.apriori_property(previous_candidates, subsets)
            if(check == True):
                candidate_final_sets.append(itemset)
        if(len(candidate_final_sets) == 0):
            return None
        
        # Now we calculate the suppport and filter against min_support
        for itemset in tqdm(candidate_final_sets):
            for transaction_id in self.data:
                if set(itemset).issubset(self.data[transaction_id]):  
                    candidate_sets_freq[itemset] = candidate_sets_freq.get(itemset, 0) + 1

        return  {item: freq for item, freq in candidate_sets_freq.items() if freq/len(self.data) >= self.min_support}

    def generate_itemsets(self):
        items_set_freq = {}
        candidates = []
        # Number of items in a set, we start from 1
        count = 1
        while True:
            # If count equals to 1, it is just the items frequency table
            if(count == 1):
                candidate_set_1 = self.item_frequency()
                if not candidate_set_1 :
                    print("No frequent itemset found")
                    return None
                items_set_freq[count] = candidate_set_1
                candidates.append(list(candidate_set_1.keys()))
                #candidates.append([key[0] for key in candidate_set_1.keys()]) 
            else:
                 # Generate the next candidate itemsets based on previous candidate set
                 candidate_itemsets = self.generate_candidate_sets(candidates[-1], count)
                 if not candidate_itemsets:
                     print("No more frequent itemsets are further found")
                     break
                 items_set_freq[count] = candidate_itemsets
                 candidates.append(list(candidate_itemsets.keys()))
                 #self.data = self.transaction_reduction(list(candidate_itemsets.keys()))
            count+=1
            
        return items_set_freq

    # Run the algorithm
    def run_apriori(self):
        itemsets_freq = self.generate_itemsets()
        return itemsets_freq
    
    # Generating strong association rules
    # Measure of how likely is Itemset Y purchased when Itemset X is purchased
    def calculate_confidence(self,  item_set_freq):

        # Flatten the item_set_freq dictionary
        flattened_item_set_freq = {}
        for key in item_set_freq:
            for subkey in item_set_freq[key]:
                flattened_item_set_freq [subkey] = item_set_freq[key][subkey]

        # print(f"Flattened Dictionary: {flattened_item_set_freq}")
        confidences = {}

        for itemset in flattened_item_set_freq:
            if(len(itemset)==1):
                continue
            for item in itemset:
                association_rules = (frozenset([item]), itemset.difference([item]))
                confidences[association_rules] = flattened_item_set_freq[itemset] / flattened_item_set_freq[frozenset([item])]

        return {rules: confidence for rules, confidence in confidences.items() if confidence >= self.min_confidence}

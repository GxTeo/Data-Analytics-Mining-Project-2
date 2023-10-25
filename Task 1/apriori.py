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
                item_tuple = frozenset((item,))
                items_freq[item_tuple] = items_freq.get(item_tuple, 0) + 1
        # Based on the minimum support value, we filter the candidate set
        return {item: freq for item, freq in items_freq.items() if freq/len(self.data) >= self.min_support}

  

    # Generate candidate sets which is the pairs/groups of item based on previous candidates set
    def generate_candidate_sets(self, previous_candidates, count):
        candidate_sets = []
        candidate_sets_freq = {}

        # Form the candidate sets
        for candidate1 in previous_candidates:
            #print("Candidate 1: ", set(candidate1))
            for candidate2 in previous_candidates:
                if candidate1 != candidate2:
                    union_set = frozenset(candidate1).union(frozenset(candidate2))
                    if len(union_set) == count and union_set not in candidate_sets:
                        # Have to use frozenset so that it can be a dictionary key
                        candidate_sets.append(union_set)

        # Now we prune it based on dataset and min_support
        for itemset in tqdm(candidate_sets):
            #print(f"Item Set: {itemset}")
            for transaction_id in self.data:
                transaction_set = set(self.data[transaction_id])
                if itemset <= transaction_set:  
                    candidate_sets_freq[itemset] = candidate_sets_freq.get(itemset, 0) + 1

        return  {item: freq for item, freq in candidate_sets_freq.items() if freq/len(self.data) >= self.min_support}

    def generate_itemsets(self, items_freq):
        items_set_freq = {}
        candidates = []

        if not items_freq :
            return "No frequent itemset found"

        # Number of items in a set, we start from 1
        count = 1
        while True:
            # If count equals to 1, it is just the items frequency table
            if(count == 1):
                items_set_freq[count] = items_freq
                candidates.append(items_freq) 
            else:
                 # Generate the next candidate itemsets based on previous candidate set
                 candidate_itemsets = self.generate_candidate_sets(candidates[-1], count)
                 if not candidate_itemsets:
                     print("No more frequent itemsets are further found")
                     break
                 candidates.append(candidate_itemsets)
                 items_set_freq[count] = candidate_itemsets
            count+=1
        
        return items_set_freq

    # Run the algorithm
    def run_apriori(self):
        items_freq = self.item_frequency()
        itemsets_freq = self.generate_itemsets(items_freq)
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

from itertools import combinations
from tqdm import tqdm

# Implementation of the paper AN IMPROVED APRIORI ALGORITHM FOR ASSOCIATION RULES with modifications
class Improved_Apriori:
    def __init__(self, data, min_support, min_confidence):
        self.data = data
        # Support is the the ratio of the number of transactions that contain an itemset.
        self.min_support = min_support
        self.min_confidence = min_confidence

    # Generate the frequent 1-itemset
    def generate_L1_itemsets(self):
        
        # This is equivalent to the item frequency which >= min_support 
        L1 = {}
        """
        Assumptions on dataset is such that

        Transaction ID : Items
        
        where data is a dictionary. Key is transaction id and items is a list
        """
        for transaction_id in self.data:
            for item in self.data[transaction_id]:
                item_tuple = (item,)
                L1[item_tuple] = L1.get(item_tuple, 0) + 1
        # Based on the minimum support value, we filter to form the frequent itemset
        return {item: freq for item, freq in L1.items() if freq/len(self.data) >= self.min_support}

    def generate_L2_candidates(self, L1, k):
        # print(f'L1: {L1}')
        candidate_sets = list(combinations(L1, k))
        """
        This function generate the 2-itemset candidates set from the 1 item frequent itemset
        """
        return candidate_sets

    def generate_candidates(self, Lk_minus_one):

        """
        This function generate the k-item candidates set from k-1 frequent itemset. This upholds Apriori property.
        
        Explained in lecture
        
        """
        candidate_sets = []
        len_Lk_minus_one = len(Lk_minus_one)
        
        # For each itemset in Lk_minus_one, join it with every other itemset
        for i in range(len_Lk_minus_one):
            for j in range(i+1, len_Lk_minus_one):
                # Only combine sets if their first k-2 items are equal
                if Lk_minus_one[i][:-1] == Lk_minus_one[j][:-1]:
                    candidate_sets.append(Lk_minus_one[i] + Lk_minus_one[j][-1:])
                    
        return candidate_sets

    
    def get_item_min_support(self, candidate_set, L1):
        """
        This function gets the lowest support item in a given itemset

        """
        min_items = []
        for itemset in candidate_set:
            min_sup = float('inf')
            min_item = None
            for item in itemset:
                sup = L1[(item,)]

                if(sup < min_sup):
                    min_sup = sup
                    min_item = item
            min_items.append(min_item)
        return min_items

    def get_transaction_ids_dict(self, L1):
        """
        For this algorithm, instead of searching the entire database, we only have to search the transactions that contain the item with the lowest support
        
        """
        transaction_id_dict = {}
        for item in L1:
            transaction_ids = []
            for transaction_id in self.data:
                if(item in self.data[transaction_id]):
                    transaction_ids.append(transaction_id)
            transaction_id_dict[item] = transaction_ids
        return transaction_id_dict

    def get_transaction_ids(self, transaction_id_dict, min_support_items):
        transaction_ids = []
        for min_support_item in min_support_items:
            transaction_ids.append(transaction_id_dict[min_support_item])
        return transaction_ids

    # Measure of how likely is Itemset Y purchased when Itemset X is purchased
    def get_confidence(self, frequent_itemset):
        confidences = {}
        for k in range(0, len(frequent_itemset)):
            for itemset in frequent_itemset[k]:
                num_itemset = frequent_itemset[k][itemset]

                # For each subset 
                for i in range(1, len(itemset)):
                    for subset in combinations(itemset, i):
                        num_subset = frequent_itemset[len(subset)-1][subset]

                        confidence = num_itemset/num_subset if num_subset > 0 else 0

                        confidences[(subset, tuple(item for item in itemset if item not in subset))] = confidence
                        


        return {rules: confidence for rules, confidence in confidences.items() if confidence >= self.min_confidence}




    def apriori(self):
        L1 = self.generate_L1_itemsets()
        L = [L1]
        L1_str = [item[0] for item in L1.keys()]
        # Nth-frequent itemset
        k = 2
        # Retrieve the transaction ids once 
        transaction_ids_dict = self.get_transaction_ids_dict(L1_str)
        while len(L[k-2]) > 0:
            if(k==2):
                candidate_sets = self.generate_L2_candidates(L1_str, k)
            else:
                # print(list(L[k-2].keys()))
                # Generate candidates based of k-1 frequent itemsets instead of L1
                candidate_sets = self.generate_candidates(list(L[k-2].keys()))
                # print(f"Candidate Sets: {candidate_sets}")

            # Get the lowest support item in an itemset
            min_support_items = self.get_item_min_support(candidate_sets, L1)
            # print(f"Min Support Items: {min_support_items}")
            transaction_ids = self.get_transaction_ids(transaction_ids_dict, min_support_items)
            # print(f'Transaction IDs at K = {k}: {transaction_ids} ')
            counts = {}

            # The bottleneck is here, unsure if there is a way to get the count of the itemset fast
            for idx, itemset in enumerate(tqdm(candidate_sets)):
                if idx < len(transaction_ids):
                    transactions = transaction_ids[idx]
                    for transaction in transactions:
                        if(set(itemset).issubset(set(self.data[transaction]))):
                            counts[itemset] = counts.get(itemset, 0) + 1


            # print(f"Counts at {k}: {counts}")
            Lk = {itemset: count for itemset, count in counts.items() if count/len(self.data) >= self.min_support}
            L.append(Lk)
            k += 1

        return L[:-1]




    



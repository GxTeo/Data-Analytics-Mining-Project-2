class Apriori:
    def __init__(self, data, min_support):
        self.data = data
        self.min_support = min_support

    # Generate support count of each item in dataset (Candidate Set 1)
    def item_frequency(self):
        # Dictionary to store Item: Frequency 
        items_freq = {}

        """
        Assumptions on dataset is such that

        Transaction ID : Items
        
        """
        for transaction_id in self.data:
            for item in transaction_id:
                if item in items_freq:
                    items_freq[item] += 1
                else:
                    items_freq[item] = 1

        # Based on the minimum support value, we filter the candidate set
        return {item: freq for item, freq in items_freq.items() if freq/len(self.data) >= self.min_support}
    
    # Generate candidate set 2 which is the pairs of item set that are 'frequent' > minimum support
    def item_pairs_frequency(self, items_freq):
        item_pairs = {}

        # Create the item pairings
        for item1 in items_freq:
            for item2 in items_freq:
                if item1 != item2:
                    # Prevent duplicate pairs like where (item1, item2) and (item2, item1)
                    item_pairing = tuple(sorted([item1, item2]))
                    item_pairs[item_pairing ] = 0

        
        for transaction_id in self.data:
            for item_pairing  in item_pairs:
                # check if item pair is a subset of transaction set
                if(set(item_pairing).issubset(transaction_id)):
                    item_pairs[item_pairing] +=1
        # Based on the minimum support value, we filter the candidate set
        return {item_pairing: freq for item_pairing, freq in item_pairs.items() if freq/len(self.data) >= self.min_support}


    def run_algo(self):

        items_freq = self.item_frequency()

        item_pairs = self.item_pairs_frequency(items_freq)


        return item_pairs
"""ClusterMetrics: a metric ****** of cluster metrics!"""
from __future__ import division
from Probably import variation_of_information as vi, \
    mutual_information as mi, log2, conditional_entropy_X_Given_Y
from waterworks.Tools import ondemand
from AIMA import DefaultDict

class ConfusionMatrix(object):
    def __init__(self):
        """Creates an empty confusion matrix.  You'll need to call the add()
        method to populate it."""
        # test : { gold : count }
        self.by_test = DefaultDict(DefaultDict(0))
        self._all_gold = None

    def __repr__(self):
        return "<ConfusionMatrix (%s test tags, %s gold tags)>" % \
            (len(self.all_test), len(self.all_gold))

    def all_gold():
        doc = "Set of all gold tags.  Calculated on demand."
        def fget(self):
            if self._all_gold is None:
                self._all_gold = set()
                for gold_dict in self.by_test.values():
                    self._all_gold.update(gold_dict.keys())
            return self._all_gold
        return locals()
    all_gold = property(**all_gold())

    def all_test():
        doc = "Set of all test tags."
        def fget(self):
            return self.by_test.keys()
        return locals()
    all_test = property(**all_test())

    def add(self, gold, test, count=1):
        """Add count joint occurrences of gold and test."""
        self.by_test[test][gold] += count
        # invalidate cache
        self._all_gold = None
    def as_confusion_items(self):
        """Yields ((gold, test), count) items."""
        for test, gold_dict in self.by_test.items():
            for gold, count in gold_dict.items():
                yield (gold, test), count
    def as_confusion_matrix(self, mapping_method='one_to_one_optimal_mapping'):
        """Returns this as a confusion matrix (list of lists)."""
        all_test = set()
        all_gold = set()
        for (gold, test), count in self.as_confusion_items():
            all_test.add(test)
            all_gold.add(gold)
        all_gold = sorted(all_gold)

        mapping_method = getattr(self, mapping_method)
        mapping = mapping_method()
        def sorter(test):
            key = mapping.get(test)
            return (key, -self.by_test[test][key])

        all_test = sorted(all_test, key=sorter)
        
        rows = []
        for gold in all_gold:
            row = [self.by_test[test][gold] for test in all_test]
            rows.append(row)

        return rows, all_gold, all_test

    def as_latex_confusion_matrix(self, normalize='gold'):
        """Returns the table as a LaTeX formatted confusion matrix.
        You will need to include the LaTeX package colortbl:

            \usepackage{colortbl}
        """
        assert normalize == 'gold', "Only supports gold normalization for now."

        from TeXTable import make_tex_bitmap
        rows, gold_labels, test_labels = self.as_confusion_matrix()

        header = [''] + test_labels
        def escape_label(label):
            label = label.replace('$', r'\$')
            label = label.replace('#', r'\#')
            label = label.replace('%', r'\%')
            return label

        def process_row(row, label):
            total = sum(row)
            return [escape_label(label)] + [1 - (cell / total) for cell in row]
        rows = [header] + [process_row(row, gold_label)
            for gold_label, row in zip(gold_labels, rows)]
        return make_tex_bitmap(rows, has_header=True)

    def pylab_pcolor(self, mapping_method='one_to_one_greedy_mapping',
                     normalize='gold'):

        assert normalize in ('total', 'gold', 'test')

        import pylab, numpy
        rows, gold_labels, test_labels = \
            self.as_confusion_matrix(mapping_method=mapping_method)

        def normalize_row_by_total(row):
            total = self.total_points
            return [1 - (cell / total) for cell in row]

        def normalize_row_by_row(row):
            total = sum(row)
            return [1 - (cell / total) for cell in row]

        if normalize == 'total':
            normalize = normalize_row_by_total
        elif normalize == 'gold':
            normalize = normalize_row_by_row
        else: # test
            from AIMA import vector_add
            column_totals = reduce(vector_add, rows)
            def normalize(row):
                return [1 - (cell / total) 
                    for cell, total in zip(row, column_totals)]

        rows = [normalize(row)
            for gold_label, row in zip(gold_labels, rows)]
        rows = numpy.array(rows)
        pylab.pcolor(rows)

    def one_to_one_greedy_mapping(self):
        """Computes the one-to-one greedy mapping.  The mapping returned
        is a dictionary of {test : gold}"""
        one_to_one_mapping = {} # test : gold
        confusion_by_count = sorted((-count, (gold, test))
            for (gold, test), count in self.as_confusion_items())

        for count, (gold, test) in confusion_by_count:
            if test in one_to_one_mapping.keys() or \
               gold in one_to_one_mapping.values():
                continue
            else:
                one_to_one_mapping[test] = gold
        return one_to_one_mapping
    def one_to_one_greedy(self, verbose=True):
        """Computes and evaluates the one-to-one greedy mapping.
        Returns a score between 0.0 and 1.0 (higher is better)."""
        return self.eval_mapping(self.one_to_one_greedy_mapping(),
                                 verbose=verbose)
    def one_to_one_optimal_mapping(self):
        """Computes the one-to-one optimal mapping using the Hungarian 
        algorithm.  The mapping returned is a dictionary of {test : gold}"""
        import pyung
        all_gold = set()
        for (gold, test), count in self.as_confusion_items():
            all_gold.add(gold)
        all_gold = sorted(list(all_gold))
        neg_confusion_array = []
        all_test = []
        for test, gold_counts in self.by_test.items():
            counts = [-gold_counts.get(gold, 0) for gold in all_gold]
            neg_confusion_array.append(counts)
            all_test.append(test)

        for x in range(len(all_gold) - len(all_test)):
            neg_confusion_array.append([0] * len(all_gold))

        mapping = pyung.hungarian_method(neg_confusion_array)
        mapping_dict = {}
        for test_index, gold_index in mapping:
            try:
                test = all_test[test_index]
            except IndexError:
                continue
            mapping_dict[test] = all_gold[gold_index]
        return mapping_dict
    def one_to_one_optimal(self, verbose=True):
        """Computes and evaluates the one-to-one optimal mapping.
        Returns a score between 0.0 and 1.0 (higher is better)."""
        return self.eval_mapping(self.one_to_one_optimal_mapping(),
                                 verbose=verbose)
    def many_to_one_mapping(self):
        """Computes the many-to-one mapping.  The mapping returned is
        a dictionary of {test : gold}"""
        many_to_one_mapping = {} # test tag : gold tag
        for test, gold_counts in self.by_test.items():
            by_count = ((v, k) for k, v in gold_counts.items())
            top_count, top = max(by_count)
            many_to_one_mapping[test] = top
        return many_to_one_mapping
    def many_to_one(self, verbose=True):
        """Computes and evaluates the many-to-one mapping.  Returns a
        score between 0.0 and 1.0 (higher is better)."""
        return self.eval_mapping(self.many_to_one_mapping(),
                                 verbose=verbose)

    def eval_mapping(self, mapping, verbose=True):
        """Evaluates a mapping (dictionary of assignments between test and
        gold).  Returns a score between 0.0 and 1.0 (higher is better).
        
        If verbose is true, the mapping will be printed before being
        evaluated."""
        if verbose:
            print "Mapping", mapping
        right = 0
        wrong = 0
        for (gold, test), count in self.as_confusion_items():
            if mapping.get(test) == gold:
                right += count
            else:
                wrong += count
        return right, wrong, right / (right + wrong)
    def variation_of_information(self):
        """Calculates the variation of information between the test and gold.  
        Lower is better, minimum is 0.0"""
        return vi(dict(self.as_confusion_items()))
    def mutual_information(self):
        """Calculates the mutual information between the test and gold.  
        Higher is better, minimum is 0.0"""
        return mi(dict(self.as_confusion_items()))

    def conditional_entropy_gold_given_test(self):
        """Calculates the conditional entropy of the gold given the test.  
        lower is better, minimum is 0.0"""
        return conditional_entropy_X_Given_Y(dict(self.as_confusion_items()))

    def _total_points(self):
        total = sum(count for (gold, test), count in self.as_confusion_items())
        return total
    total_points = ondemand(_total_points)

    def _pairwise_statistics(self):
        items = []
        for (gold, test), count in self.as_confusion_items():
            items.extend((((gold, test),) * count))

        N00 = 0
        N01 = 0
        N10 = 0
        N11 = 0
        for index1, i1 in enumerate(items):
            for index2, i2 in enumerate(items):
                if index2 <= index1:
                    continue
                # print index1, index2, i1, i2
                if i1[0] != i2[0] and i1[1] != i2[1]:
                    N00 += 1
                if i1 == i2:
                    N11 += 1
                if i1[0] == i2[0] and i1[1] != i2[1]:
                    N10 += 1
                if i1[0] != i2[0] and i1[1] == i2[1]:
                    N01 += 1

        return N00, N11, N01, N10
    pairwise_statistics = ondemand(_pairwise_statistics)

if __name__ == "__main__":
    cm = ConfusionMatrix()
    cm.add('B', 1, 0)
    cm.add('A', 1, 9)
    cm.add('B', 2, 9)
    cm.add('A', 2, 10)
    print cm.one_to_one_greedy()
    print cm.eval_mapping(cm.many_to_one_mapping())
    print cm.variation_of_information()
    print cm.mutual_information()
    print cm.one_to_one_optimal_mapping()
    print cm.one_to_one_optimal()

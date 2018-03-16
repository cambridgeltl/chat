####################
#   FileName:    significance.py
#   Author:      Simon Baker
#   Affiliation: University of Cambridge
#                Computer Laboratory and Language Technology Laboratory
#   Contact:     simon.baker.gen@gmail.com
#                simon.baker@cl.cam.ac.uk
#
#   Description: This file performs the functionality of statistical significance testing for CHAT.

import numpy as np
from scipy.stats import chi2_contingency,fisher_exact

FISHER_EXACT_THRESHOLD = 5

def useFisherExact(contTable):
    #Table looks like this:
    # q1+ q2+
    # q1- q2-

    #calculate expected frequency for each cell in the table

    pos = contTable[0][0] + contTable[0][1]
    neg = contTable[1][0] + contTable[1][1]
    q1 = contTable[0][0] + contTable[1][0]
    q2 = contTable[0][1] + contTable[1][1]
    tot = np.sum(contTable)
    expectedValues = np.array([q1*pos, q2*pos,q1*neg,q2*neg])/float(tot)
    # return true if any of the expected values is less than the threshold (5 is the expected norm)
    for item in expectedValues:
        if item <= FISHER_EXACT_THRESHOLD:
            return True
    return False

    return expectedValues

def run_test(q1_pos, q2_pos, q1_neg,q2_neg):
    '''
    this method takes four parallel arrays representing a 2X2 contingency table.
    the length of these parallel arrays denotes the number of tests that will be run,
    either a chi-squared test or an fisher-exact test are run, epending whether the requriments for a
    reliable chi-squared test are satisifed.

    Bonferroni correction is then applied by adjusting the p-values for all of the tests

    We return two parellel arrays, the first array is the p-values of for the tests, the second array is the test value
    e.g. the chi-squared value or the fisher-exact oddsratio.

    '''

    input = [q1_pos, q2_pos, q1_neg,q2_neg]
    n = len(input[0])
    if not all(len(x) == n for x in  input):
        raise BaseException ("length of input lists must be of same length")

    pvalues = []
    test_values = []

    for i in range(0,n):

        obs = np.array([ [input[0][i],input[1][i]],[input[2][i],input[3][i]] ])
        if useFisherExact(obs):
            p = fisher_exact(obs)[1]
            t = fisher_exact(obs)[0]
        else:
            p = chi2_contingency(obs)[1]
            t = chi2_contingency(obs)[0]

        pvalues.append(p)
        test_values.append(t)
    #applying Bonferroni correction
    adjustedPValues = [ float(p)/float(n) for p in pvalues]
    return [adjustedPValues, test_values]

def term_significance(term_counts):
    """Return dict of dicts with metric values for each term.

    Args:
        term_counts (dict): Dict of dicts, outer keyed by term (str),
            inner by hallmark (str), values are counts. Totals are
            keyed by None; e.g. term_counts[term][None] is the total
            term count.
    """
    if len(term_counts.keys()) != 2:
        raise Exception("There should be exactly 2 query terms in the term_counts dictionary argument, given {0}: {1}".format(len(term_counts.keys()), str(term_counts.keys())))

    [q1,q2] = term_counts.keys()
    q1_count = term_counts[q1][None]
    q2_count = term_counts[q2][None]
    hm_list = [x for x in term_counts[q1] if x != None]
    q1_pos = [term_counts[q1][hm] for hm in hm_list]
    q2_pos = [term_counts[q2][hm] for hm in hm_list]
    q1_neg = [(q1_count - term_counts[q1][hm]) for hm in hm_list]
    q2_neg = [(q2_count - term_counts[q2][hm]) for hm in hm_list]
    [pvalues,chi2values] = run_test(q1_pos, q2_pos, q1_neg,q2_neg)
    return{"pvalue":{hm_list[i]:pvalues[i] for i in range((len(hm_list)))},
    "chi2":{hm_list[i]:chi2values[i] for i in range((len(hm_list)))}}

if __name__ == '__main__':
    q1= {"hm1":22,"hm2":16,"hm3":2,"hm4":122, None:262}
    q2= {"hm1":12,"hm2":16,"hm3":27,"hm4":82, None:237}
    print(str(term_significance({"q1":q1, "q2":q2})))

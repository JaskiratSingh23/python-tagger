# HiddenMarkovModel.py
# Using Python 2.7.11

import math
from cs_model import CodeSModel

class HiddenMarkovModel:
    """Represents a Hidden Markov Model. The Hidden Markov Model, or HMM
        is a statistical Markov Model made to observe a Markov process
        where the results are known, but the state of the process is not.

    Args:
        words (list<str>): list of words
        tag_set (list<str>): list of tags
        transi_matrix (dict<str -> dict<str -> float>>): transition matrix.
            See the method in eval.py. As of now, is a 2x2 matrix.
        cs_model (CodeSModel): The code switched language model of the
            corpus.

    Properties:
        words (list<str>): list of words
        tag_set (list<str>): list of tags
        transi_matrix (dict<str -> dict<str -> float>>): transition matrix.
            See the method in eval.py. As of now, is a 2x2 matrix.
        cs_model (CodeSModel): The code switched language model of the
            corpus.
        v (list<list<HMMNode>>): A series of nodes representiing the provided words.
            This will be filled with useful info once the method viterbi is
            called, and the data processed. There is one set of nodes for each word,
            and each of these sets carry one node for every language tag.

    """

    def __init__(self, words, tag_set, transi_matrix, cs_model):
        self.words = words
        self.tag_set = tag_set
        self.transi_matrix = transi_matrix
        self.cs_model = cs_model
        self.v = [[HMMNode(0, 0) for __ in xrange(len(tag_set))]
            for __ in xrange(len(words))]

    def gen_tags(self):
        """Generate the tags of the language using the viterbi alogrithm to
            determine the probabilities, and then determining most likely tags.

        Return:
            list<str>: A list of tags generated by the retrace method
        """
        self.viterbi()
        return self.retrace()

    def em(self, lang, word):
        """Find the emission property, or how likely it a certain observable
            state has been generated from a state.

        Here, the observable state is the word, and the hidden state is the
            context language.

        Args:
            lang (str): Which language to match the word to
            word (str): Which word to check the likelihood of belonging to a
                language

        Return:
            The probability for a word to exist, given a context
        """
        return self.cs_model.prob(ctx, word)

    def tr(self, ctx, tag):
        """Determines the transmission probability of a node.

        The transmission probability is the likelihood of a single state
            to transition to another state. That state can be either the
            same or different from the original state.

        Args:
            ctx (str): the source state
            tag (str): the target state

        Return:
            float: probability of transitioning from the given state to the
                new state.
        """
        return self.transi_matrix[ctx][tag]

    def viterbi(self):
        """Runs the viterbi algorithm on the setup of the hidden Markov model.

        The following is a description of the algorithm:
            in the first node set, for each language, assume a base possibility
            for each word
                for each language node
                    craft the set of possible nodes (previous to current state)
                determine the most likely previous node for each current node
                save the node with a reference to the most likely past node

        At the end of the Viterbi algorithm, the most likely paths
            from the available bases should be generated.
        """
        for k, tag in enumerate(self.tag_set):
            self.v[0][k] = HMMNode(math.log(0.5), -1)

        for wordi, word in enumerate(self.words):
            if wordi == 0:
                pass
            for tagi, next_tag in enumerate(self.tag_set):
                # Using loop
                tran_prob = []
                for old_tagi, prev_tag in enumerate(self.tag_set):
                    tran_prob.append(HMMNode(self.v[wordi - 1][old_tagi].prob
                        + self.tr(prev_tag, next_tag), old_tagi))

                nextnode = reduce( # Looks for the node with highest prob
                    lambda n1, n2: n1 if n1.prob > n2.prob else n2,
                    tran_prob)
                em_prob = self.em(self.tag_set[tagi], self.words[wordi])
                self.v[wordi][tagi] = HMMNode(em_prob + nextnode.prob,
                    nextnode.p_tag)

    def retrace(self): # CHANGED. ensure it works
        """Reverse traverses the graph generated by the viterbi algorithm to
            find the best path (the one with the highest probability)

        Returns:
            list<str>: the most likely tag combinations
        """
        tags = []

        # Find most probable final tag and add it
        last = reduce(lambda x, y: x if self.v[len(self.words) - 1][x].prob >
            self.v[len(self.words) - 1][y].prob else y,
            xrange(len(self.tag_set)))

        # Follow backpointers to most probable previous tags
        prev = self.v[-1][last]
        while prev != -1:
            tags.append(self.tag_set[prev])
            prev = self.v[k][prev].p_tag
        # Return the reversed traversal
        return tags.reverse()


class HMMNode:
    """A class for use with the hidden Markov model, specifically made for
        use with the viterbi algorithm.

    Args:
        prob (float): Probability of reaching the current node from the
            provided previous tag
        p_tag (int): The tag that most likely led to this node. Is the
            index of the tag in the tag_set of the HMM this node belongs
            to.
    Properties:
        prob (float): Probability of reaching the current node
        p_tag (int): The tag that most likely led to this node. Is the
            index of the tag in the tag_set of the HMM this node belongs
            to.
    """
    def __init__(self, prob, p_tag):
        self.prob = prob
        self.p_tag = p_tag


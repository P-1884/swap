
import swap.db.classifications as db


class Score:
    def __init__(self, id_, gold, p):
        self.id = id_
        self.gold = gold
        self.p = p

    def dict(self):
        return {'id': self.id, 'gold': self.gold, 'p': self.p}

    def __str__(self):
        return 'id: %d gold: %d p: %.3f' % (self.id, self.gold, self.p)

    def __repr__(self):
        return '{%s}' % self.__str__()


class ScoreExport:
    def __init__(self, scores, new_golds=True):
        if new_golds:
            scores = self._init_golds(scores)
        self.scores = scores

    def _init_golds(self, scores):
        golds = self.get_real_golds()
        for score in scores:
            score.gold = golds[score.id]
        return scores

    def get_real_golds(self):
        return db.getAllGolds()

    def counts(self, threshold):
        n = {-1: 0, 0: 0, 1: 0}
        for score in self.scores.values():
            if score.p >= threshold:
                n[score.gold] += 1
        return n

    def composition(self, threshold):
        n = self.counts(threshold)

        total = sum(n.values())
        for i in n:
            n[i] = n[i] / total

        return n

    def purity(self, threshold):
        return self.composition(threshold)[1]

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return iter(self.scores)

    def roc(self, labels=None):
        def func(score):
            return score.gold, score.p

        def isgold(score):
            return score.gold in [0, 1]

        scores = self.scores

        if labels is None:
            return ScoreIterator(scores, func, isgold)
        else:
            def cond(score):
                return isgold(score) and score.id in labels
            return ScoreIterator(scores, func, cond)

    def full(self):
        def func(score):
            return (score.id, score.gold, score.p)
        return ScoreIterator(self.scores, func)


class ScoreIterator:
    def __init__(self, scores, func, cond=None):
        if type(scores) is dict:
            scores = list(scores.values())
        if type(scores) is not list:
            raise TypeError('scores type %s not valid!' % str(type(scores)))

        self.scores = scores
        self.func = func
        if cond is None:
            self.cond = lambda item: True
        else:
            self.cond = cond
        self.i = 0

    def next(self):
        if self.i >= len(self):
            raise StopIteration

        score = self.scores[self.i]
        self.i += 1

        if self.cond(score):
            obj = self.func(score)
            return obj
        else:
            return self.next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.scores)

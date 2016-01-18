def parse(filename, n_trials=100):
    f = open(filename, 'r')
    n_fail = 0
    for _ in xrange(n_trials):
        for _ in xrange(3):
            next(f)
        line = next(f)
        if 'not' in line.split():
            n_fail += 1
    failRate = n_fail * 1. / n_trials * 100
    print "Number of failure: {}, success rate: {}%.".format(n_fail,
                                                             100 - failRate)

if __name__ == '__main__':
    parse("./(0.5,0.5).txt")

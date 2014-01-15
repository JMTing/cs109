import numpy as np

from mrjob.job import MRJob
from itertools import combinations, permutations

from scipy.stats.stats import pearsonr


class RestaurantSimilarities(MRJob):

    def steps(self):
        "the steps in the map-reduce process"
        thesteps = [
            self.mr(mapper=self.line_mapper, reducer=self.users_items_collector),
            self.mr(mapper=self.pair_items_mapper, reducer=self.calc_sim_collector)
        ]
        return thesteps

    def line_mapper(self,_,line):
        "this is the complete implementation"
        user_id,business_id,stars,business_avg,user_avg=line.split(',')
        yield user_id, (business_id,stars,business_avg,user_avg)


    def users_items_collector(self, user_id, values):
        """
        #iterate over the list of tuples yielded in the previous mapper
        #and append them to an array of rating information
        """
        rating_info = list(values)
        business_id = [x[0] for x in rating_info]
        stars = [x[1] for x in rating_info]
        business_avg = [x[2] for x in rating_info]
        user_avg = [x[3] for x in rating_info]

        yield user_id, [business_id, stars, business_avg, user_avg]

    def pair_items_mapper(self, user_id, values):
        """
        ignoring the user_id key, take all combinations of business pairs
        and yield as key the pair id, and as value the pair rating information
        """
        business_id = values[:][0]
        stars = values[:][1]
        business_avg = values[:][2]
        user_avg = values[:][3]

        for i in range(len(business_id)):
            for j in range(i + 1,len(business_id)):
                if business_id[i] < business_id[j]:
                    yield (business_id[i], business_id[j]), ([stars[i],business_avg[i],user_avg[i]],[stars[j],business_avg[j],user_avg[j]])
                else:
                    yield (business_id[j], business_id[i]), ([stars[j],business_avg[j],user_avg[j]],[stars[i],business_avg[i],user_avg[i]])

    def calc_sim_collector(self, key, values):
        """
        Pick up the information from the previous yield as shown. Compute
        the pearson correlation and yield the final information as in the
        last line here.
        """
        (rest1, rest2), common_ratings = key, list(values)
        diff1, diff2 = [], []
        n_common = len(common_ratings)

        for i in common_ratings:
            diff1.append(float(i[0][0]) - float(i[0][2]))
            diff2.append(float(i[1][0]) - float(i[1][2]))

        rho = pearsonr(diff1, diff2)[0]
        if rho != rho:
            rho = 0

        yield (rest1, rest2), (rho, n_common)


#Below MUST be there for things to work
if __name__ == '__main__':
    RestaurantSimilarities.run()
    
import pandas as pd
import sys
import random
import math
from operator import itemgetter
from copy import deepcopy
import numpy as np


def greedy(query_bidders, bidder_totals, queries):
	bidding = 0.0
	for query in queries:
		max_bid = 0
		# get all the advertiser ids for a max_bid value for which at least one advertiser has budget left
		max_bidder = []

		for bidder, value in sorted(query_bidders[query].items(), key=itemgetter(1), reverse=True):
			# only if the bidder has budget left for this ad	
			if bidder_totals[bidder] >= value:
				# the value would be greater than max_bid for the first iteration and then we only check for all the equal values
				# as query_bidders is iterated in descending order of bid values, else break.
				if value >= max_bid:
					max_bid = value
					max_bidder.append(bidder)
				else:
					break

		if max_bidder:
			bidding += max_bid
			bidder_totals[min(max_bidder)] -= max_bid
	
	return bidding


def balance(query_bidders, bidder_totals, queries):
	bidding = 0.0
	for query in queries:
		max_bidder = -1
		max_bidder_total = 0
		max_bid = 0
		
		# sorted based on advertiser id to tackle tie-breaker condition
		for bidder, value in sorted(list(query_bidders[query].items())):
			# only if advertiser has budget for this ad
			if bidder_totals[bidder] >= value:
				if bidder_totals[bidder] > max_bidder_total:
					max_bidder = bidder
					max_bidder_total = bidder_totals[max_bidder]
					max_bid = value

		if max_bid != 0:
			bidding += max_bid
			bidder_totals[max_bidder] -= max_bid

	return bidding


def msvv(query_bidders, bidder_totals, queries):
	bidding = 0.0
	for query in queries:
		max_bid = 0
		neighbours = list(query_bidders[query].items())
		max_bidder = -1
		max_bidder_psi = 0

		# sorted based on advertiser id to tackle tie-breaker condition
		for bidder, value in sorted(list(query_bidders[query].items())):
			# only if advertiser has budget for this ad
			if bidder_totals[bidder] >= value:
				if value*bidder_psi_val(bidder, bidder_totals) > max_bidder_psi:
					max_bidder = bidder
					max_bid = value
					max_bidder_psi = max_bid*bidder_psi_val(bidder, bidder_totals)

		if max_bid != 0:
			bidding += max_bid
			bidder_totals[max_bidder] -= max_bid

	return bidding


def bidder_psi_val(bidder, bidder_totals):
	return 1 - np.exp((bidder_budgets[bidder]-bidder_totals[bidder])/bidder_budgets[bidder] - 1)


def revenue_estimation(query_bidders, bidder_budgets, queries, algo):
	adword_func = {'greedy':greedy, 'balance':balance, 'msvv':msvv}
	random.seed(0)
	# optimal sum of budgets 
	opt = sum(bidder_budgets.values())
	# revenue without shuffling
	bidding = adword_func[algo](query_bidders, deepcopy(bidder_budgets), queries)
	# storing revenue on shuffling queries
	bidding_shuffle = 0
	
	for i in range(100):
		random.shuffle(queries)
		bidding_shuffle += (adword_func[algo](query_bidders, deepcopy(bidder_budgets), queries))

	avg = bidding_shuffle/100
	return bidding, avg, avg/opt 


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Wrong algorithm")
		sys.exit(1)

	algo = sys.argv[1]

	# reading data from csv file
	bidder_csv = pd.read_csv('bidder_dataset.csv')
	# reading all queries in a list
	queries = [query.strip() for query in open('queries.txt')]

	# storing advertisers and their bids for a particalar query in the form {query1:{advertiser1:bid1, advertiser2:bid2,...}, query2:{advertiser2:bid2,...},...}
	query_bidders = {}
	# storing advertisers and their total budget that can be spent in the form {advertiser1: total_budget1,...}
	bidder_budgets = {}

	for row in bidder_csv.itertuples():
		advertiser, keyword, value, budget = row[1], row[2], row[3], row[4]
		if not math.isnan(budget):
			bidder_budgets[advertiser] = budget
		query_bidders.setdefault(keyword, {}).update({advertiser:value})

	# returning all 3 values: revenue without shuffling, average revenue for 100 shuffles, and competitive ratio
	revenue, revenue_shuffled, comp_ratio = revenue_estimation(query_bidders, bidder_budgets, queries, algo)

	# printing only non-shuffled revenue instead of average shuffled revenue to match the answers in the pdf description
	print (round(revenue, 2))
	print (round(comp_ratio, 2))

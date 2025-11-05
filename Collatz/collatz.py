#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visualization of the Collatz conjecture

@autor: Han de Jong
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

tree = nx.Graph()

def step(A):
	"""
	Function that calculates the next step
	"""

	if A%2==0:
		return int(A/2)
	else:
		return int(A*3+1)


def add_to_tree(X, tree=tree):
	"""
	Runs 3n+1 untill we lock into the tree
	"""
	counter = 0
	old_X = X

	not_done = True
	while not_done:
		new_X = step(X)
		if new_X in tree.nodes:
			not_done = False
		tree.add_edge(X, new_X)
		X = new_X
		counter += 1

	print(f'Added {old_X} to the tree in {counter} steps.')

	return counter

def fill_tree(itterations=1, tree=tree):
	"""
	Connect something to every node which has only 1 or 2 degrees

	"""
	
	for i in range(itterations):
		nodes = [node for node in tree.nodes]

		for node in nodes:
			if nx.degree(tree, node)<3:

				# Node form halving
				tree.add_edge(node, int(node*2))

				# Node from 3n+1
				temp = (node-1)/3
				if temp % 2 == 1:
					tree.add_edge(node, int(temp))



def draw_tree(tree=tree, labels=False):
	"""
	Drawing and formatting of the tree.
	"""

	# Remove the end of the loop
	#tree.remove_edge(1, 4)

	# Calculate the distance to 1
	distances = [len(nx.shortest_path(tree, node, 1)) for node in tree.nodes]

	# Figure
	fig = plt.figure()

	# Graph
	pos = nx.kamada_kawai_layout(tree)

	# Drawing
	nx.draw_networkx_edges(tree, pos, width=0.1)
	nx.draw_networkx_nodes(tree, pos, node_size=5, node_color = distances)

	# Labels if requested
	if labels:
		nx.draw_networkx_labels(tree, pos)

	# Formatting
	ax = plt.gca()
	ax.axis('off')

	# Finish up
	plt.tight_layout()
	plt.show()


# Run program if run from terminal
if __name__ == '__main__':
	for i in range(1, 26):
		add_to_tree(i)

	# Draw tree
	draw_tree()
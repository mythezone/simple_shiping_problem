import numpy as np 
import collections

def evolutionary_framework_local(generation, population, generator, sorter, fitness,
                                 acceptable, selector, mutation, crossover):
    population_lst = generator(population)
    population_lst = [(item, fitness(item)) for item in population_lst]
    population_lst = sorter(population_lst)
    for i in range(generation):
        child_lst = list()
        for single_item in population_lst:
            if selector(single_item, population_lst):
                if mutation is not None:
                    result_item = mutation(single_item)
                    if isinstance(result_item, collections.Iterable):
                        child_lst += result_item
                    else:
                        child_lst.append(result_item)
                if crossover is not None:
                    result_item=crossover(single_item,population_lst)
                    if isinstance(result_item, collections.Iterable):
                        child_lst += result_item
                    else:
                        child_lst.append(result_item)
        child_lst = [(item, fitness(item)) for item in child_lst]
        population_lst += child_lst
        population_lst = sorter(population_lst)
        # if population_lst[0][1] == population_lst[-1][1]:
        #     np.random.shuffle(population_lst)
        population_lst = population_lst[: population]
        print("In " + str(i) + " generation: ")
        print(population_lst)
        if acceptable is not None and acceptable(population_lst):
            return population_lst[0], i
    return population_lst[0], generation
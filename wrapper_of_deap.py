import numpy as np
import pandas as pd
from itertools import repeat
import random
import math
from deap import base, creator, tools


# Generate initial individual
def generate_init_ind(icls, more_params):
    genome = [random.uniform(more_params[i][0],more_params[i][1]) for i in range(len(more_params))]
    return icls(genome)

# Evaluation function
def evalfunc_wrapper(ests):
    def evalfunc(individual):
        individual_array = np.array(individual).reshape(1,-1)
        
        prs = []
        for i in range(len(ests)):
            pr = ests[i].predict(individual_array)
            prs.append(pr[0])

        return prs
    return evalfunc

def fix_input(minmax_list, int_mask, categorical_indexes, composition_index):
    categorical_indexes_inner = categorical_indexes
    len_categorical_indexes = len(categorical_indexes)

    categorical_indexes_num = []
    for categorical_index in categorical_indexes:
        temp = []
        for i, index in enumerate(categorical_index):
            if index:
                temp.append(i)
        categorical_indexes_num.append(temp)

    composition_index_num = []
    for i, index in enumerate(composition_index):
        if index:
            composition_index_num.append(i)

    def decorator(func):
        def wrappper(*args, **kargs):
            children = func(*args, **kargs)

            category_sum_list = [0 for i in range(len_categorical_indexes)]
            composition_sum = 0

            for child in children:
                for i in range(len(child)):
                    if math.isnan(child[i]):
                        child[i] = 0
                    if child[i] > minmax_list[i][1]:
                        child[i] = minmax_list[i][1]
                    elif child[i] < minmax_list[i][0]:
                        child[i] = minmax_list[i][0]
                        
                    if sum(int_mask) == 0:
                        pass
                    else:
                        if int_mask[i]:
                            child[i] = int(child[i])

                    if sum(sum(categorical_indexes_inner, [])) != 0:
                        for j, categorical_index in enumerate(categorical_indexes_inner):
                            if categorical_index[i]:
                                category_sum_list[j] += child[i]

                    if sum(composition_index) != 0:
                        if composition_index[i]:
                            composition_sum += child[i]
            
                if sum(sum(categorical_indexes_inner, [])) != 0:
                    for i, temp in enumerate(categorical_indexes_num):
                        if category_sum_list[i] != 1:
                            for index in temp:
                                child[index] = 0
                            index = random.choice(temp)
                            child[index] = 1
                
                if sum(composition_index) != 0 and int(composition_sum) != 100:
                    for index in composition_index_num:
                        child[index] /= composition_sum/100

            return children
        return wrappper
    return decorator

class GenericAlgorithm:
    def __init__(self, x_df, constraints_df, ests, categorical_indexes, int_index, composition_index, weights):
        self._input, self.cols = self.set_x_df(x_df)
        self._lims = self.set_constraints_df(constraints_df)
        self.ests = ests
        self._categorical_indexes = self.set_categorical_indexes(categorical_indexes)
        self._int_mask= self.set_int_index(int_index)
        self.composition_index = self.set_composition_index(composition_index)
        self.weights = weights
    
    def set_x_df(self, value):
        return np.array(value.values, dtype=float), list(value.columns)

    def set_categorical_indexes(self, value):
        bool_list = []
        for index in value:
            temp = [True if i in index else False for i in self.cols]
            bool_list.append(temp)

        return bool_list

    def set_constraints_df(self, value):
        temp = value.values.T
        lims = []
        for i in range(temp.shape[0]):
            lims.append(temp[i,:])

        return lims

    def set_int_index(self, value):
        return [True if i in value else False for i in self.cols]

    def set_composition_index(self, value):
        return [True if i in value else False for i in self.cols]

    def create(self):
        creator.create("Fitness", base.Fitness, weights=self.weights)
        creator.create("Individual", list, fitness=creator.Fitness)

    def register_decorate(self):
        toolbox = base.Toolbox()
        toolbox.register("individual", generate_init_ind, creator.Individual, self._lims)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", evalfunc_wrapper(self.ests))

        # Functions for evolution 
        lims_low = [t[0] for t in self._lims]
        lims_up = [t[1] for t in self._lims]
        toolbox.register("mate", tools.cxSimulatedBinaryBounded,low=lims_low, up=lims_up, eta=0.7)
        toolbox.register("mutate", tools.mutPolynomialBounded, low=lims_low, up=lims_up, eta=0.7, indpb=0.03)
        toolbox.register("select", tools.selNSGA2)

        # Decorate MinMax and Fix_Param
        toolbox.decorate("population",fix_input(self._lims, self._int_mask, self._categorical_indexes, self.composition_index))
        toolbox.decorate("mate",fix_input(self._lims, self._int_mask, self._categorical_indexes, self.composition_index))
        toolbox.decorate("mutate",fix_input(self._lims, self._int_mask, self._categorical_indexes, self.composition_index))

        # Multiprocessing 
        # pool = multiprocessing.Pool(processes=12)
        # toolbox.register("map", pool.map)

        return toolbox

    def initial_pop(self, toolbox, popn):
        inputs = self._input.tolist()
        pop_inputs = list(map(creator.Individual,inputs))

        fitnesses = list(map(toolbox.evaluate, pop_inputs))
        for ind, fit in zip(pop_inputs, fitnesses):
            ind.fitness.values = fit    

        if len(pop_inputs) <= popn:
            pop = toolbox.population(n=popn-len(inputs))
            # evaluatation of initial population
            fitnesses = list(map(toolbox.evaluate, pop))
            for ind, fit in zip(pop, fitnesses):
               ind.fitness.values = fit

            print("  Evaluated %i random individuals" % len(pop))
            pop = pop_inputs + pop

        else:
            pop = random.sample(pop_inputs, popn)

        result = [list(ind)+[val for val in ind.fitness.values] for ind in pop]

        return pop, result

    def evolute(self, gens, popn=100, cxpb=0.5, mutpb=0.5):
        self.create()
        toolbox = self.register_decorate()
        pop, result = self.initial_pop(toolbox, popn)

        # Start of evolutionary computation
        g = 0
        while g < gens:
            g += 1
        
            print("optimize_log", "-- Generation %i --" % g)
            
            offspring = random.sample(list(map(toolbox.clone, pop)),len(pop))
        
            # Mate
            for child1,child2 in zip(offspring[::2],offspring[1::2]):
                if random.random() < cxpb:
                    toolbox.mate(child1,child2)
                    del child1.fitness.values
                    del child2.fitness.values
        
            # Mutate
            for mutant in offspring:
                if random.random() < mutpb:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
        
            # 適応度を削除した個体について適応度の再評価を行う
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            result += [list(ind)+[val for val in ind.fitness.values] for ind in invalid_ind]

            # Generate individual
            random_ind = toolbox.population(len(offspring)-len(invalid_ind)) 
            fitnesses = map(toolbox.evaluate, random_ind)
            for ind, fit in zip(random_ind, fitnesses):
                ind.fitness.values = fit
            result += [list(ind)+[val for val in ind.fitness.values] for ind in random_ind]

            pop = toolbox.select(invalid_ind+random_ind+pop, k=len(offspring))

        # Output DataFrame 
        cols = self.cols + list(range(len(self.weights)))
        result_df = pd.DataFrame(result, columns=cols)

        return result_df







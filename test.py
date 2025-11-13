import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
import math


instance_01 = pd.read_csv("instances/instance_01.csv")
vehicules = pd.read_csv("instances/vehicles.csv")


#model 
model = ConcreteModel()

#index
longueur_instance = len(instance_01)
longueur_vehicules = len(vehicules)

dico = dict(zip(instance_01['id'], instance_01['latitude']))

print(dico)
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory

instance_01 = pd.read_csv("instances/instance_01.csv")
vehicules = pd.read_csv("instances/vehicles.csv")
print(vehicules.head())


#model 
model = ConcreteModel()

#index
longueur_instance = len(instance_01)
longueur_vehicules = len(vehicules)

model.set_F = Set(initialize = vehicules['family'])
model.set_w_capacity = Set(initialize = vehicules['max_capacity'])
model.set_c_rental = Set(initialize = vehicules['rental_cost'])
model.set_c_fuel = Set(initialize = vehicules['fuel_cost'])
model.set_c_radius = Set(initialize = vehicules['radius_cost'])
model.set_s = Set(initialize = vehicules['speed'])
model.set_p = Set(initialize = vehicules['parking_time'])
model.set_a_0 = Set(initialize = vehicules['fourier_cos_0'])
model.set_a_1 = Set(initialize = vehicules['fourier_cos_1'])
model.set_a_2 = Set(initialize = vehicules['fourier_cos_2'])
model.set_a_3 = Set(initialize = vehicules['fourier_cos_3'])
model.set_b_0 = Set(initialize = vehicules['fourier_sin_0'])
model.set_b_1 = Set(initialize = vehicules['fourier_sin_1'])
model.set_b_2 = Set(initialize = vehicules['fourier_sin_2'])
model.set_b_3 = Set(initialize = vehicules['fourier_sin_3'])

model.set_V = Set(initialize = [0] + instance_01['id'])

model.w_capacity =  Param(initialize = vehicules['max_capacity'])
model.c_renta =  Param(initialize = vehicules['rental_cost'])
model.c_fuel =  Param(initialize = vehicules['fuel_cost'])
model.s =  Param(initialize = vehicules['speed'])
model.p =  Param(initialize = vehicules['parking_time'])
model.a_0 =  Param(initialize = vehicules['fourier_cos_0'])
model.a_1 =  Param(initialize = vehicules['fourier_cos_1'])
model.a_2 =  Param(initialize = vehicules['fourier_cos_2'])
model.a_3 =  Param(initialize = vehicules['fourier_cos_3'])
model.b_0 =  Param(initialize = vehicules['fourier_sin_0'])
model.b_1 =  Param(initialize = vehicules['fourier_sin_1'])
model.b_2 =  Param(initialize = vehicules['fourier_sin_2'])
model.b_3 =  Param(initialize = vehicules['fourier_sin_3'])

model.phi =  Param(initialize = instance_01['latitude'])
model.lamb =  Param(initialize = instance_01['longitude'])
model.w =  Param(initialize = instance_01['order_weight'])
model.i =  Param(initialize = instance_01['id'])
model.t_min =  Param(initialize = instance_01['window_start'])
model.t_max =  Param(initialize = instance_01['window_end'])
model.l = Param(initialize = instance_01['delivery_duration'])

model.x = Var(model.set_V, model.set_V, model.set_F, within = Binary)

model.x.pprint()

#couts


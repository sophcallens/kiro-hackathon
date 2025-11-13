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

model.set_V = Set(initialize = [0] + instance_01['id'])
model.set_f = Set(initialize = vehicules['family'])
model.set_i = Set(initialize = instance_01['id'])


#paramètres

model.w_capacity = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['max_capacity'])))
model.c_rental = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['rental_cost'])))
model.c_fuel = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fuel_cost'])))
model.s = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['speed'])))
model.p = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['parking_time'])))
model.a_0 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_cos_0'])))
model.a_1 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_cos_1'])))
model.a_2 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_cos_2'])))
model.a_3 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_cos_3'])))
model.b_0 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_sin_0'])))
model.b_1 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_sin_1'])))
model.b_2 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_sin_2'])))
model.b_3 = Param(model.set_f, initialize = dict(zip(vehicules['family'], vehicules['fourier_sin_3'])))

model.phi =  Param(model.set_i, initialize = dict(zip(instance_01['id'], instance_01['latitude'])))
model.lamb =  Param(initialize = dict(zip(instance_01['id'],instance_01['longitude'])))
model.w =  Param(initialize = dict(zip(instance_01['id'],instance_01['order_weight'])))
model.t_min =  Param(initialize = dict(zip(instance_01['id'],instance_01['window_start'])))
model.t_max =  Param(initialize = dict(zip(instance_01['id'],instance_01['window_end'])))
model.l = Param(initialize = dict(zip(instance_01['id'],instance_01['delivery_duration'])))

#variable

model.x = Var(model.set_V, model.set_V, model.set_f, within = Binary)


#distances

T = 86400
pi = math.pi
cos = math.cos
sin = math.sin
sqrt = math.sqrt
rho = 6.371e6
omega = 2*pi/T

def delta_M(i, j):
    delta_y = rho*2*pi/360*(model.phi[i]-model.phi[j])
    delta_x = rho*(cos(22*pi/360*model.phi[0]))*2*pi/360*(model.lamb[i]-model.lamb[j])
    return abs(delta_x) + abs(delta_y)

def delta_E(i,j) :
    delta_y = rho*2*pi/360*(model.phi[i]-model.phi[j])
    delta_x = rho*(cos(22*pi/360*model.phi[0]))*2*pi/360*(model.lamb[i]-model.lamb[j])
    return sqrt((delta_x)**2 + abs(delta_y)**2)

def travel_times (f,i,j,t) :
    tau_f = delta_M(i,j) / model.s[f] + model.p[f]
    gama_f = model.a_0[f] + model.a_1[f]*cos(omega*t) + model.b_1[f]*sin(omega*t) + model.a_2[f]*cos(2*omega*t) + model.b_2[f]*sin(2*omega*t) + model.a_3[f]*cos(3*omega*t) + model.b_3[f]*sin(3*omega*t)
    return tau_f*gama_f


#couts

def cout_rental(model):
    return sum(model.c_rental[f] * model.x[0,j,f] 
               for j in model.set_i
               for f in model.set_f)

def cout_fuel(model):
    return sum(model.c_fuel[f] * delta_M(i,j) * model.x[i,j,f]
               for i in model.set_i
               for j in model.set_i
               for f in model.set_f)

def cout_radius(model):
    total = 0
    r = 0
    sommet_visite = list(range(longueur_instance))
    while sommet_visite:
        j = sommet_visite.pop(0)
        de_max = 0
        # trouver la famille f correspondant au sommet j
        f_trouve = None
        for f in model.set_f:
            if model.x[0, j, f] == 1:
                f_trouve = f
                break
        if f_trouve is None:
            continue

        # construire la chaîne pour cette famille
        chaine = [0]
        sommet = j
        while sommet != 0:
            chaine.append(sommet)
            next_sommet = None
            for visite in range(longueur_instance):
                if model.x[sommet, visite, f_trouve] == 1:
                    next_sommet = visite
                    break
            if next_sommet is None:
                break
            sommet = next_sommet  
        while chaine != [] :
            i_1 = chaine.pop(0) 
            for i_2 in chaine :
                de = delta_E(i_1,i_2)
                if de > de_max :
                    de_max = de
        total += model.c_radius[f] * (1/2) * de_max
        r += 1
    return total

def cout_total(model) :
    return cout_rental(model) + cout_fuel(model) + cout_radius(model)


#fonction objectif

model.obj = Objective(rule = cout_total, sense = minimize)


#création df
def creation_csv(model):
    df = pd.DataFrame()
    r = 0
    sommet_visite = list(range(longueur_instance))

    while sommet_visite:
        j = sommet_visite.pop(0)

        # trouver la famille f correspondant au sommet j
        f_trouve = None
        for f in model.set_f:
            if model.x[0, j, f].value == 1:
                f_trouve = f
                break
        if f_trouve is None:
            continue

        # construire la chaîne pour cette famille
        chaine = []
        sommet = j
        while sommet != 0:
            chaine.append(sommet)
            next_sommet = None
            for visite in range(longueur_instance):
                if model.x[sommet, visite, f_trouve].value == 1:
                    next_sommet = visite
                    break
            if next_sommet is None:
                break
            sommet = next_sommet

        # créer les lignes dynamiquement selon la longueur de la chaîne
        lignes = ['family'] + [f'order_{k}' for k in range(len(chaine))]
        df = df.reindex(lignes)  # ajuste le DataFrame pour avoir exactement ces lignes

        # ajouter la colonne pour cette famille
        df[f'r_{r}'] = None
        df.loc['family', f'r_{r}'] = f_trouve
        for k, sommet in enumerate(chaine):
            df.loc[f'order_{k}', f'r_{r}'] = sommet

        r += 1

    return df                    

print(creation_csv(model))
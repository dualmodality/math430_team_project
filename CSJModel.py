import numpy as np
import random

#This is the class/template we can use to create different species of plants. Each Plant object holds the variables/parameters
#that are related to how the species behaves

class Plant:
    
    def __init__(self, name, growth_rate, ideal_sat, sat_alpha, percent_root_biomass, sensitivity_sigma):
        self.name = str(name)
        self.base_growth_rate = growth_rate
        self.ideal_soil_sat = ideal_sat
        self.ideal_sat_alpha = sat_alpha
        self.percent_root_biomass = percent_root_biomass
        self.sensitivity = sensitivity_sigma
        self.biomass = 0
        
    def growth_rate(self, soil_sat):
        return ((-1 * self.ideal_sat_alpha * (soil_sat - self.ideal_soil_sat) ** 4 + 1) * self.base_growth_rate)

#This is a list of 8 plant species that will be used to populate the test plots

def make_plant(param_dict, init_biomass, comp_sigma):
    plant = Plant(param_dict['name'], param_dict['growth_rate'], param_dict['ideal_sat'], param_dict['sat_alpha'], param_dict['percent_root'], comp_sigma)
    plant.biomass = init_biomass
    return plant

#This class implements a "Plot" container that represents an area/habitat for various plant species.
#The class has a list that [should] contain different species of plant, and keeps track the current
#soil saturation, its carrying capacity, and the soil's base saturation rate. There are also methods that returns
#the total biomass, root biomass, and leaf biomass of all plants in the plot, a method to cause the plot to dry out a little, and a method
#to re-hydrate the plot up to a given saturation level (capped at 1.0)

class Plot:
    
    def __init__(self, species_list, cap, sat, h2o_base_rate):
        self.plant_list = species_list
        self.capacity = cap
        self.soil_saturation = sat
        self.base_saturation_rate = h2o_base_rate
    
    def add_sat(self, sat):
        self.soil_saturation = min(self.soil_saturation + sat, 1.0)
    
    def total_biomass(self):
        total = 0
        for plant in self.plant_list:
            total += max(plant.biomass, 0)
        return total
    
    def root_biomass(self):
        total = 0
        for plant in self.plant_list:
            total += max(plant.biomass * plant.percent_root_biomass, 0)
        return total
    
    def leaf_biomass(self):
        total = 0
        for plant in self.plant_list:
            total += max(plant.biomass * (1 - plant.percent_root_biomass), 0)
        return total
    
    def set_sat(self, transpiration, retention, rain_sat):
        delta_sat = -(self.base_saturation_rate + self.leaf_biomass() * transpiration) * (self.soil_saturation - self.root_biomass() * retention) + rain_sat
        self.soil_saturation += delta_sat
        if self.soil_saturation < 0.0:
            self.soil_saturation = 0.0
        elif self.soil_saturation > 1.0:
            self.soil_saturation = 1.0

#This method runs a single trial and returns time series dicts for all plots

def run_trial(trial_num, model_params, plant_params, plot_combos, comp_sigma, rain_freq, freq_std, rain_amt, amt_std):
    datapoint_list = []
    
    #Construct the plots
    plot_list = []
    for combo in plot_combos:
        try:
            init_biomass = model_params['initial_plot_biomass']/len(combo)
        except:
            init_biomass = model_params['initial_plot_biomass']
        my_plants = []
        for index in combo:
            my_plants.append(make_plant(plant_params[index], init_biomass, comp_sigma))
        plot_list.append(Plot(my_plants, model_params['plot_capacity'], model_params['initial_sat'], model_params['base_drainage_rate']))
            
            
    for day in range(model_params['n_days']):
        #Determine the day's weather
        chance_of_rain = np.random.normal(rain_freq, freq_std) * 100
        if chance_of_rain > 100.0:
            chance_of_rain = 100.0
        elif chance_of_rain < 0:
            chance_of_rain = 0.0
        if random.randint(0, 100) <= chance_of_rain:
            rain_sat = np.random.normal(rain_amt, amt_std)
            if rain_sat < 0:
                rain_sat = 0.0
        else:
            rain_sat = 0.0
    
    
        for plot_index in range(len(plot_list)):
            point = {'plot_index': plot_index, 'trial': trial_num, 'day': day}
            #Adjust the day's soil_sat
            plot_list[plot_index].set_sat(model_params['transpiration_rate'], model_params['root_retention'], rain_sat)
            point['soil_sat'] = plot_list[plot_index].soil_saturation

            #Let the plants grow or die and add biomass data to datapoint
            total_biomass = 0
            for i in range(len(plot_list[plot_index].plant_list)):
                other_biomass = 0
                for j in range(len(plot_list[plot_index].plant_list)):
                    if j != i:
                        other_biomass += max(plot_list[plot_index].plant_list[j].biomass, 0)
                delta_biomass = plot_list[plot_index].plant_list[i].growth_rate(plot_list[plot_index].soil_saturation) * plot_list[plot_index].plant_list[i].biomass * (1 - (plot_list[plot_index].plant_list[i].biomass/(plot_list[plot_index].capacity - comp_sigma * other_biomass)))
                plot_list[plot_index].plant_list[i].biomass += delta_biomass
                if plot_list[plot_index].plant_list[i].biomass < 0:
                    plot_list[plot_index].plant_list[i].biomass = 0
                point[plot_list[plot_index].plant_list[i].name + '_biomass'] = plot_list[plot_index].plant_list[i].biomass
                total_biomass += plot_list[plot_index].plant_list[i].biomass

            point['total_biomass'] = total_biomass
            #Append the datapoint to the datapoint list
            datapoint_list.append(point)

    return datapoint_list
                   
#This is the class/template we can use to create different species of plants. Each Plant object holds the variables/parameters
#that are related to how the species behaves

class Plant:
    
    def __init__(self, name, rate, k, alpha, mass, percent_root_biomass):
        self.name = str(name)
        self.base_growth_rate = rate
        self.ideal_soil_sat = k
        self.ideal_sat_alpha = alpha
        self.biomass = mass
        self.biomass = percent_root_biomass
    
    def growth_rate(self, soil_sat):
        return (-1 * self.ideal_sat_alpha * (soil_sat - self.ideal_soil_sat) ** 4 + 1) * self.base_growth_rate


#This class implements a "Plot" container that represents an area/habitat for various plant species.
#The class has a list that [should] contain different species of plant, and keeps track the current
#soil saturation, its carrying capacity, and the soil's base saturation rate. There is also a method that returns
#the total biomass of all plants in the plot, a method to cause the plot to dry out a little, and a method
#to re-hydrate the plot up to a given saturation level (capped at 1.0)

class Plot:
    
    def __init__(self, iden, plant_list, cap, sat, h2o_base_rate, leaf_trans, root_ret):
        self.plot_id = iden
        self.species_list = plant_list
        self.capacity = cap
        self.soil_saturation = sat
        self.base_saturation_rate = h2o_base_rate
        self.leaf_transpiration = leaf_trans
        self.root_retention = root_ret
    
    def dry(self):
        self.soil_saturation -= (self.base_saturation_rate + (self.leaf_biomass * self.leaf_transpiration)) * (self.soil_saturation - (self.root_biomass * self.root_retention))
    
    def wet(self, sat):
        self.soil_saturation = min(self.soil_saturation + sat, 1.0)
        
    def total_biomass(self):
        total = 0
        for plant in self.species_list:
            total += plant.biomass
        return total
    
    def root_biomass(self):
        total = 0
        for plant in self.species_list:
            total += plant.biomass * plant.percent_root_biomass
        return total
    
    def leaf_biomass(self):
        total = 0
        for plant in self.species_list:
            total += plant.biomass * (1 - plant.percent_root_biomass)
        return total
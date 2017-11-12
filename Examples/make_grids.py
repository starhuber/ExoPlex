

#**********************************************************************#
'''
This scipt will be for making data files showing a parameter space and
solutions found by ExoPlex
'''
#*********************************************************************



import os
import sys
import numpy as np
import matplotlib.pyplot as plt
# hack to allow scripts to be placed in subdirectories next to burnman:
if not os.path.exists('ExoPlex') and os.path.exists('../ExoPlex'):
    sys.path.insert(1, os.path.abspath('..'))


import ExoPlex as exo
import PREM.prem as p
from params import *
import pdb

################################################################




####
# Fe/Mg and Si/Mg will vary while rest of composition parameters are fixed
# Fe_ox = flEl_c = 0, pure Fe core and no Fe in mantle
####

FeMg = np.arange(0.5, 2.0, 0.1)
SiMg = np.arange(0.5, 2.0, 0.1)
CaMg       = 0. # 0.0656565
AlMg       = 0. #0.09090909
Fe_ox      = 0.0

wt_h2o     = [0.0] # [0.0, 0.05, 0.10, 0.15]

wt_Sic = 0.0
wt_Oc  = 0.0
wt_Sc  = 0.0

Mass = np.arange(0.8, 4.1, 0.2)


#####################################################################


def file_names(mass):
    mass_string = repr(round(mass,2)).replace('.', ',')
    name = 'Dat/'+mass_string+'_noH2O'+'.dat'

    return name


def plot_rho(Planet):
    depth_ep = (Planet['radius'][-1]-Planet['radius'])/1e3
    rho_ep = Planet['density']/1e3

    #setup plots
    fig, ax =  plt.subplots(figsize = (15,10))

    #plotting parameters, can change
    plt.rc('font', family='serif')
    lab_size = 23
    tic_size = 18
    ax.set_xlim(0., max(depth_ep))
    #ax.set_ylim(.90, 4)

    ax.set_ylabel("Density (g/cm$^3$)", fontsize = lab_size )
    ax.set_xlabel("Depth (km)", fontsize = lab_size)
    ax.tick_params(direction='in', length=6, labelsize = tic_size)
    ax.grid(color='grey', linestyle='-', alpha = 0.4, linewidth=.7)

    ax.plot(depth_ep, rho_ep, label = 'ExoPlex', lw = 4, color = 'magenta')

    plt.legend(loc = 'lower right', fontsize = tic_size)

    plt.show()




def grid_make():


    grid_size = int((len(FeMg))*(len(SiMg))*len(wt_h2o))
    #arrays to store code output for plotting and other nonsense
    mass_grid     = np.zeros(grid_size)
    femg_grid     = np.zeros(grid_size)
    simg_grid     = np.zeros(grid_size)
    h2o_grid      = np.zeros(grid_size)
    CMF_grid      = np.zeros(grid_size)
    CRF_grid      = np.zeros(grid_size)
    rad_grid      = np.zeros(grid_size)
    bulk_rho_grid = np.zeros(grid_size)

    fix_core = False
    num_mantle_layers = 2000
    num_core_layers   = 2000
    number_h2o_layers = 200

    Mantle_potential_temp = 1800


    #sample exoplex for all these cases
    for m in range(len(Mass)):
        #file name, each mass gets its own file
        f_name = file_names(Mass[m])
        if os.path.exists(f_name):
            continue
        elif Mass[m]>= 2.5:
            Mantle_potential_temp = 1700.

        n = 0
        for i in range(len(FeMg)):

            for j in range(len(SiMg)):

                for k in range(len(wt_h2o)):


                    #print 'FeMg = {0}\tSiMg = {1}'.format(femg_grid[i+j], simg_grid[i+j])
                    #continue
                    compositional_params = [wt_h2o[k],FeMg[i],SiMg[j],CaMg,AlMg,Fe_ox ,wt_Sic, \
                                  wt_Oc , wt_Sc]

                    structure_params =  [Pressure_range_mantle_UM,Temperature_range_mantle_UM,resolution_UM,
                                 Pressure_range_mantle_LM, Temperature_range_mantle_LM, resolution_LM,
                                 Core_rad_frac_guess,Mantle_potential_temp, h20_radfrac_guess, T_surface_h2o]

                    layers = [num_mantle_layers,num_core_layers,number_h2o_layers]

                    sol_filename = 'Star_Boy37'

                    Planet = exo.run_planet_mass(Mass[m], compositional_params,structure_params,layers,sol_filename, fix_core)

                    mass_grid[n]     = Mass[m]
                    femg_grid[n]     = FeMg[i]
                    simg_grid[n]     = SiMg[j]
                    h2o_grid[n]      = wt_h2o[k]
                    CMF_grid[n]      = Planet['mass'][num_core_layers]/Planet['mass'][-1]
                    CRF_grid[n]      = Planet['radius'][num_core_layers]/Planet['radius'][-1]
                    rad_grid[n]      = (Planet['radius'][-1]/1000.)/REarth #R_Earth units
                    bulk_rho_grid[n] = Planet['mass'][-1]/(4./3 *np.pi*(np.power(Planet['radius'][-1],3)))
                    n+=1


        data_file = open(f_name, 'w')

        dat_row_header = '{0:15}{1:15}{2:15}{3:15}{4:15}{5:15}{6:15}{7:15}'.format('Mass', 'Radius','Fe/Mg', \
                        'Si/Mg', 'wt%+h2o', 'Bulk density', 'core_wt%', 'core_rad%')
        np.savetxt(f_name, np.transpose([mass_grid,rad_grid, femg_grid, simg_grid, h2o_grid,bulk_rho_grid, CMF_grid, CRF_grid]), \
                    delimiter = '    ',  fmt = '%-10.5f', header = dat_row_header)



    return


grid_make()

#######################################################################
'''
produce core, mantle, and water, planets here
'''
#######################################################################



def grid_make_special(i_file):

    fix_core = {'fix_man': True, 'wtCore': 0.0000000000000000001}

    wt_h2o =    0.9999999999999999


    f_name = ['pure_h2o.dat', 'mantle_only.dat', 'core_only.dat']

    num_mantle_layers = 200
    num_core_layers = 200
    number_h2o_layers = 4000

    FeMg = 1.0
    SiMg = 1.0
    AlMg = 0.#0.090909090
    CaMg = 0.#0.06666
    grid_size = len(Mass)

    mass_grid     = np.zeros(grid_size)
    CMF_grid      = np.zeros(grid_size)
    CRF_grid      = np.zeros(grid_size)
    rad_grid      = np.zeros(grid_size)
    bulk_rho_grid = np.zeros(grid_size)


    data_file = open(f_name[i_file], 'w')

    dat_row_header = '{0:13}{1:13}{2:13}{3:13}{4:13}'.format('Mass', 'Radius',\
            'Bulk density', 'core_wt%', 'core_rad%')

    for m in range(len(Mass)):
        if Mass[m] > 2.0 and i_file == 0:
            Mantle_potential_temp = 2600
        else:
            Mantle_potential_temp = 1800

        compositional_params = [wt_h2o,FeMg,SiMg,CaMg,AlMg,0. ,wt_Sic, \
                                  wt_Oc , wt_Sc]

        structure_params =  [Pressure_range_mantle_UM,Temperature_range_mantle_UM,resolution_UM,
                     Pressure_range_mantle_LM, Temperature_range_mantle_LM, resolution_LM,
                     Core_rad_frac_guess,Mantle_potential_temp, h20_radfrac_guess, T_surface_h2o]

        layers = [num_mantle_layers,num_core_layers,number_h2o_layers]

        sol_filename = 'Star_Boy37'

        Planet = exo.run_planet_mass(Mass[m], compositional_params,structure_params,layers,sol_filename, fix_core)
        mass_grid[m]     = Mass[m]
        CMF_grid[m]      = Planet['mass'][num_core_layers]/Planet['mass'][-1]
        CRF_grid[m]      = Planet['radius'][num_core_layers]/Planet['radius'][-1]
        rad_grid[m]      = (Planet['radius'][-1]/1000.)/REarth #R_Earth units
        bulk_rho_grid[m] = Planet['mass'][-1]/(4./3 *np.pi*(np.power(Planet['radius'][-1],3)))

        #plot_rho(Planet)
        #sys.exit()

    np.savetxt(f_name[i_file], np.transpose([mass_grid,rad_grid, bulk_rho_grid, CMF_grid, CRF_grid]), \
                delimiter = '    ',  fmt = '%-10.4f', header = dat_row_header)

    return








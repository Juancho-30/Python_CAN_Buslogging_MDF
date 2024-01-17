import numpy as np
import pandas as pd
from asammdf import MDF, Signal, blocks
import matplotlib.pyplot as plt
import matplotlib.font_manager
from styleframe import StyleFrame, Styler, utils
from scipy.stats import norm 
import statistics 


path = 'C:/Users/VWK3W84/Documents/files/Merged_filtered_files/20230829_15_46_CANLogger_RwandaTractorMDF.mf4'
# print(path_filename)


def linear_interpolation_3D(x1, y1, z1, x2, y2, x3, y3, z3):
    # Perform linear interpolation to find z2 (Value of torque in df_82 and df_100)
    z2 = z1 + ((x2 - x1) / (x3 - x1)) * (z3 - z1) + ((y2 - y1) / (y3 - y1)) * (z3 - z1)
    return z2

def linear_interpolation(x1, y1, x2, y2, x):
    # Perform linear interpolation to find y (Exact value of torque for x voltage)
    # Check if x is outside the range [x1, x2]
    if x < x1 or x > x2:
        raise ValueError("x is outside the range [x1, x2]")

    # Calculate the slope (m) of the line between (x1, y1) and (x2, y2)
    m = (y2 - y1) / (x2 - x1)

    # Use the equation of a line to interpolate the value of y at x
    y = y1 + m * (x - x1)

    return y

def map_values(num_rpm, num_idc, df):
    # Extract column and index value for mapping lower, upper x,y and mapping torque z
    i = 0
    j = 0
    # df.columns is a iterable object which gives all the values of each column head
    for column_value in  df.columns: 
        if column_value >= num_idc:
            i = i+1
            upper_x = column_value
            lower_x = df.columns[i]    
    # df.index is a iterable object which gives all the values of each index
    for index_value in  df.index:
        if index_value <= num_rpm:
            j = j+1
            lower_y = index_value 
            upper_y = df.index[j]
            #print([lower_y,upper_y]) 

    # Map Torque value for lower, upper column, index values of idc and rpm

    lower_z = df.at[lower_y, lower_x]
    upper_z = df.at[upper_y, upper_x]

    #Return values for 3d interpolation
    return lower_x, lower_y, upper_x, upper_y, lower_z, upper_z 

required_channels = [
        'BMS_U_Batt',
        'BMS_SOC',
        'BMS_I_Batt', 
        'Cell_T_max',
        'Controller_Temperature',
        'Motor_Temperature',
        'Aussentemperatur',
        'GPS_Speed', 
        'Capacitor_Voltage',
        'Motor_RPM', 
        'Current_RMS'
        ]

mdf_res = MDF(path,required_channels)
mdf_starttime = mdf_res.start_time
date_string = (f"{mdf_res.start_time:%b,%d,%Y}")
seconds = int(f"{mdf_res.start_time:%H:%M:%S}"[6:])
minutes = int(f"{mdf_res.start_time:%H:%M:%S}"[3:5])
hours = int(f"{mdf_res.start_time:%H:%M:%S}"[0:2])

# Generate Dataframe and manipulate columns
mdf_df = mdf_res.to_dataframe(channels=required_channels)
mdf_df.index.names = ['Time[s]']
mdf_df = mdf_df.rename(columns={'BMS_U_Batt': "BMS_U_Batt\nBattery voltage [V]",
                                'BMS_I_Batt': "BMS_I_Batt\nBattery current [A]", 
                                'BMS_SOC': "BMS_SOC\nBattery SOC [%]",
                                'Cell_T_max': "Cell_T_max\nBattery temperature [°C]",
                                'Controller_Temperature': "Controller_Temperature\nMotor controller temperature [°C]",
                                'Motor_Temperature': "Motor_Temperature\nElectric motor temperature [°C]",
                                'Aussentemperatur': "Aussentemperatur\nAmbient air temperature [°C]",
                                'GPS_Speed': "GPS_Speed\nGPS speed [m/s]",
                                'Capacitor_Voltage': "Capacitor_Voltage\nElectric motor dc voltage [V]",
                                'Motor_RPM': "Motor_RPM\nElectric motor speed [rpm]",
                                'Current_RMS': "Current_RMS\nElectric motor phase current [A]",
                                              })


# New Empty list object, to append all the interpolated torques and after getting torque calculate every efficiency item
torque_list = []
efficiency_list = []
timestamps = []
timestamps_plot = []
uncertainty_list = []
p_el_list = []
p_el_median_list = []
p_el_q_75_list = []
p_el_q_25_list = []
p_el_max_list = []
p_el_min_list = []
dyn_subset_pel = []
dyn_subset_pmec = []
p_mec_list = []
p_mec_median_list = []
p_mec_q_75_list = []
p_mec_q_25_list = []
p_mec_max_list = []
p_mec_min_list = []
dyn_subset_pel = []
dyn_subset_pmec = []
i = 0

sampling_rate = int(len(mdf_df)/80) # 80 samples per plot

# Import from excel file and store it.
xls = pd.ExcelFile('C:/Users/VWK3W84/Documents/mapdata.xlsx')

# Parse Excel sheet into df_82, df_100 Dataframes respectively.
df_82 = xls.parse('4Q_82V')
df_100 = xls.parse('4Q_100V')

#Set column named "idc-rpm" as index of dataframe.
df_82.set_index("rpm - idc", inplace=True)
df_100.set_index("rpm - idc", inplace=True)

# for num_rpm, num_idc in each row of the dataframe as iterator object.
for index,series in mdf_df.iterrows():

    num_rpm = series["Motor_RPM\nElectric motor speed [rpm]"]
    num_idc = series["BMS_I_Batt\nBattery current [A]"]
    voltage = series["BMS_U_Batt\nBattery voltage [V]"]

    value = num_rpm
    if num_rpm > 4000:
        num_rpm = 3999.999999

    #Map the value from df_82 and df_100 for idc and rpm as X, Y extract them and map torque as Z
    lower_x, lower_y, upper_x, upper_y, lower_z, upper_z = map_values(num_rpm, num_idc, df_82)
    lower_x1, lower_y1, upper_x1, upper_y1, lower_z1, upper_z1 = map_values(num_rpm, num_idc, df_100)

    # Input data for 3D linear interpolation df_82
    x1, y1, z1 = lower_x, lower_y, lower_z  # Known lower point
    x2, y2, z2 = num_idc, num_rpm, None   # Point to interpolate (z2 is unknown)
    x3, y3, z3 = upper_x, upper_y, upper_z  # Known upper point

    # Input data for 3D linear interpolation df_100
    x11, y11, z11 = lower_x1, lower_y1, lower_z1  # Known lower point
    x22, y22, z22 = num_idc, num_rpm, None   # Point to interpolate (z22 is unknown)
    x33, y33, z33 = upper_x1, upper_y1, upper_z1  # Known upper point

    # Perform interpolation df_82 (x1, y1, z1, x2, y2, x3, y3, z3)
    z2 = linear_interpolation_3D(x1, y1, z1, x2, y2, x3, y3, z3)

    # Perform interpolation df_100
    z22 = linear_interpolation_3D(x11, y11, z11, x22, y22, x33, y33, z33)

    # Perform a 2d interpolation between df_82 and df_100
    x1 = 82         # Constant 82V
    y1 = z2         # Torque value from 3d Interpolation on df_82
    x2 = 100        # Constant 100V
    y2 = z22        # Torque value from 3d Interpolation on df_100
    x = voltage     # Actual Voltage to be interpolated in 2d Linear interpolation

    torque = linear_interpolation(x1, y1, x2, y2, x)
    if num_idc > 0: # Motor mode
        efficiency = abs(((np.pi/30*num_rpm) * (torque))/(num_idc*voltage))
    else:           # Generating Mode
        if num_rpm != 0 and torque != 0:
            efficiency = abs((num_idc*voltage) / ((np.pi/30*num_rpm) * (torque)))
        elif num_rpm == 0:
            num_rpm = 10 ** -30                     # Number really close to zero
            efficiency = abs((num_idc*voltage) / ((np.pi/30*num_rpm) * (torque)))    

    # Pout/Pin, Pout = Torque * w; w = 2pi/60 *rpm, Pin = Vin * Iin

    if efficiency <= 0:
        if value <= 4000:
            uncertainty_list.append("efficiency <= 0")
        else:
            uncertainty_list.append("efficiency <= 0 and rpm > 4000")

    elif efficiency >= 1:
        efficiency = 1
        if value <= 4000:
            uncertainty_list.append("efficiency >= 1")
        else:
            uncertainty_list.append("efficiency >= 1 and rpm > 4000")

    elif efficiency < 1  and efficiency > 0:
        if value <= 4000:
            uncertainty_list.append("-")
        else:
            uncertainty_list.append("- rpm > 4000")

    seconds = seconds + 1
    if seconds == 60:
        minutes = minutes + 1
        seconds = 0
        if minutes == 60:
            hours = hours + 1
            minutes = 0

    p_el = voltage * num_idc
    p_mec = (np.pi * torque * num_rpm) / 30

    timestamps.append(f"{hours}:{minutes}:{seconds}")
    torque_list.append(torque) # Append current torque to the torque list
    dyn_subset_pel.append(p_el)
    p_mec_list.append(p_mec)
    p_el_list.append(p_el)
    dyn_subset_pmec.append(p_mec)
    efficiency_list.append(efficiency) # Append current efficiency to the torque list
    
    if len(dyn_subset_pel) == sampling_rate:
        p_el_median_list.append(np.quantile(dyn_subset_pel,.50)) # median
        timestamps_plot.append(timestamps[i])
        p_el_q_75_list.append(np.quantile(dyn_subset_pel,.75)) # 75% quantile
        p_el_q_25_list.append(np.quantile(dyn_subset_pel,.25)) # 25% quantile
        p_el_max_list.append(np.max(dyn_subset_pel)) # max
        p_el_min_list.append(np.min(dyn_subset_pel)) # min
        i = i + (sampling_rate)
        dyn_subset_pel = []  

    if len(dyn_subset_pmec) == sampling_rate:
        p_mec_median_list.append(np.quantile(dyn_subset_pmec,.50))
        p_mec_q_75_list.append(np.quantile(dyn_subset_pmec,.75)) # 75% quantile
        p_mec_q_25_list.append(np.quantile(dyn_subset_pmec,.25)) # 25% quantile
        p_mec_max_list.append(np.max(dyn_subset_pmec)) # max
        p_mec_min_list.append(np.min(dyn_subset_pmec)) # min
        dyn_subset_pmec = [] 

# Insert list as column in dataframe
mdf_df.insert(mdf_df.columns.size, "Torque [Nm]", torque_list, allow_duplicates=True)
mdf_df.insert(mdf_df.columns.size, "Efficiency [Pout/Pin]", efficiency_list, allow_duplicates=True)
mdf_df.insert(0, "Timestamps [H:M:S]", timestamps)

activity = input("Enter the activity for that day ")


# Median sampled
df_power = pd.DataFrame({'p_el': p_el_median_list, 'p_el_max':p_el_max_list, 
'p_el_75':p_el_q_75_list,'p_el_25':p_el_q_25_list, 'p_el_min':p_el_min_list,
'p_mec':p_mec_median_list, 'p_mec_max':p_mec_max_list, 
'p_mec_75':p_mec_q_75_list,'p_mec_25':p_mec_q_25_list, 'p_mec_min':p_mec_min_list})
df_power.insert(0, "Timestamps [H:M:S]", timestamps_plot)

# Power/Energy Diagrams
fig,axs = plt.subplots(2,2, figsize=(30, 20), layout='constrained', label = "Power/Energy Diagrams" )
fig.suptitle("Power - Energy Diagrams", fontsize=22, fontname = 'arial')

# Diagram 1: Mechanical Power
axs[0,0].plot(df_power["Timestamps [H:M:S]"], df_power['p_mec_max'], color='lightgrey', label = 'P_Mec_Max')
axs[0,0].grid(visible = True)
axs[0,0].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_mec_75'], df_power['p_mec_max'], facecolor = "lightcoral")
axs[0,0].plot(df_power["Timestamps [H:M:S]"], df_power['p_mec_75'], color='grey', label = 'P_Mec_75%')
axs[0,0].plot(df_power["Timestamps [H:M:S]"], df_power['p_mec'], color='black', label = 'P_Mec_50%')
axs[0,0].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_mec_25'], df_power['p_mec_75'], facecolor = "indianred")
axs[0,0].plot(df_power["Timestamps [H:M:S]"], df_power['p_mec_25'], color='silver', label = 'P_Mec_25%')
axs[0,0].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_mec_min'], df_power['p_mec_25'], facecolor = "lightcoral")
axs[0,0].plot(df_power["Timestamps [H:M:S]"], df_power['p_mec_min'], color='lightgrey', label = 'P_Mec_Min')
axs[0,0].set_title('Electric Machine_Mechanical Power', fontname = 'arial')
axs[0,0].set_xlabel("Timestamps [H:M:S]")
axs[0,0].set_ylabel("Power [W]")
axs[0,0].set_ylim(ymin = (min(p_mec_list) - (max(p_mec_list)/10/100)), ymax = max(p_el_list) - (max(p_el_list)/10/100))
axs[0,0].legend()
every_nth = 5
for n, label in enumerate(axs[0,0].xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)

# Diagram 2:Electric Power
axs[0,1].plot(df_power["Timestamps [H:M:S]"], df_power['p_el_max'], color='lightgrey', label = 'P_Elec_Max')
axs[0,1].grid(visible = True)
axs[0,1].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_el_75'], df_power['p_el_max'], facecolor = "skyblue")
axs[0,1].plot(df_power["Timestamps [H:M:S]"], df_power['p_el_75'], color='grey', label = 'P_Elec_75%')
axs[0,1].plot(df_power["Timestamps [H:M:S]"], df_power['p_el'], color='black', label = 'P_Elec_50%')
axs[0,1].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_el_25'], df_power['p_el_75'], facecolor = "cadetblue")
axs[0,1].plot(df_power["Timestamps [H:M:S]"], df_power['p_el_25'], color='grey', label = 'P_Elec_25%')
axs[0,1].fill_between(df_power["Timestamps [H:M:S]"], df_power['p_el_min'], df_power['p_el_25'], facecolor = "skyblue")
axs[0,1].plot(df_power["Timestamps [H:M:S]"], df_power['p_el_min'], color='lightgrey', label = 'P_Elec_Min')
axs[0,1].set_title('Battery Output Power', fontname = 'arial')
axs[0,1].set_xlabel("Timestamps [H:M:S]")
axs[0,1].set_ylabel("Power [W]")
axs[0,1].set_ylim(ymin = (min(p_mec_list) - (max(p_mec_list)/10/100)), ymax = max(p_el_list) + (max(p_el_list)/10/100))
axs[0,1].legend()
for n, label in enumerate(axs[0,1].xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)

# Diagram 3: Battery Power Histogram
n, b, p = axs[1,0].hist(p_mec_list, bins = 25, histtype = 'step', color = 'indianred', label = 'Histogram Electric Machine: Mechanical Power')
axs[1,0].grid(visible = True)
axs[1,0].set_title('Histogram: Electric Machine_Mechanical Power', fontname = 'arial')
axs[1,0].set_xlabel("Power [W]")
axs[1,0].set_ylabel("Frequency")
axs[1,0].vlines(np.percentile(p_mec_list,0), ymin = 0, ymax = max(n), label = f"0% = {round(np.percentile(p_mec_list,0),3)}", color = "steelblue")
axs[1,0].vlines(np.percentile(p_mec_list,25), ymin = 0, ymax = max(n), label = f"25% = {round(np.percentile(p_mec_list,25),3)}", color = "steelblue")
axs[1,0].vlines(np.percentile(p_mec_list,50), ymin = 0, ymax = max(n), label = f"50% = {round(np.percentile(p_mec_list,50),3)}", color = "steelblue")
axs[1,0].vlines(np.percentile(p_mec_list,75), ymin = 0, ymax = max(n), label = f"75% = {round(np.percentile(p_mec_list,75),3)}", color = "steelblue")
axs[1,0].vlines(np.percentile(p_mec_list,100), ymin = 0, ymax = max(n), label = f"100% = {round(np.percentile(p_mec_list,100),3)}", color = "steelblue")
axs[1,0].legend()
axs[1,0].set_xlim(xmin = (min(p_mec_list) - (max(p_mec_list)/10/100)), xmax = max(p_el_list) + (max(p_el_list)/10/100))

n, b, p = axs[1,1].hist(p_el_list, bins = 25, histtype = 'step', color = 'navy', label = 'Histogram Battery Output Power')
axs[1,1].grid(visible = True)
axs[1,1].set_title('Histogram Battery Output Power', fontname = 'arial')
axs[1,1].set_xlabel("Power [W]")
axs[1,1].set_ylabel("Frequency")
axs[1,1].vlines(np.percentile(p_el_list,0), ymin = 0, ymax = max(n), label = f"0% = {round(np.percentile(p_el_list,0),3)}", color = "steelblue")
axs[1,1].vlines(np.percentile(p_el_list,25), ymin = 0, ymax = max(n), label = f"25% = {round(np.percentile(p_el_list,25),3)}", color = "steelblue")
axs[1,1].vlines(np.percentile(p_el_list,50), ymin = 0, ymax = max(n), label = f"50% = {round(np.percentile(p_el_list,50),3)}", color = "steelblue")
axs[1,1].vlines(np.percentile(p_el_list,75), ymin = 0, ymax = max(n), label = f"75% = {round(np.percentile(p_el_list,75),3)}", color = "steelblue")
axs[1,1].vlines(np.percentile(p_el_list,100), ymin = 0, ymax = max(n), label = f"100% = {round(np.percentile(p_el_list,100),3)}", color = "steelblue")
axs[1,1].legend()
axs[1,1].set_xlim(xmin = (min(p_mec_list) - (max(p_mec_list)/10/100)), xmax = max(p_el_list) + (max(p_el_list)/10/100))

fig.savefig(f"../Images/Power-Energy Diagrams_{activity}_{date_string}.jpg")



mdf_df.insert(mdf_df.columns.size, "Uncertain value",  uncertainty_list)
mdf_df = mdf_df.reset_index()

# #Export Dataframe to Excel File
# writer = StyleFrame.ExcelWriter(f"Documents/files/Excel_files/{activity}_{date_string}.xlsx")
# sf = StyleFrame(mdf_df)

# sf.apply_column_style(cols_to_style=mdf_df.columns, styler_obj=Styler(bg_color=utils.colors.white, bold=True,font_size=8), width = 24, style_header=True)
# sf.apply_headers_style(styler_obj=Styler(bg_color=utils.colors.blue, bold=True  , font_size=8, font_color=utils.colors.white,number_format=utils.number_formats.general, protection=False))

    
# sf.to_excel(writer, sheet_name = date_string, row_to_add_filters= 0)
# writer._save()



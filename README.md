# Python_CAN_Buslogging_MDF
MDF CAN Buslogging file [filtering, merging, cutting] with asammdf

This python code uses the MDF class from asammdf to be able to use it's methods, in that way we use:

1. concatenate method: To merge several MDF Files into 1 file.
2. resample method: To resample the file into the wanted time sampling. (Uses interpolation)
3. cut method: To cut the file from start time and end time variables. (Expects that the mdf file start time is less than wanted start time and end time is greater than wanted end time)
4. to_dataframe: Used to further print a pandas dataframe that corresponds to the new file.

For more information about asammdf, visit asammdf API: https://asammdf.readthedocs.io/en/master/api.html#


To change signals according to your needs:
  Change the required_channels list:
  
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


# Python_CAN_Buslogging_MDF
MDF CAN Buslogging file [filtering, merging, cutting, dataframe generating, exporting to excel, styling] with asammdf

This python code uses the MDF class from asammdf, pandas, Styleframe, and numpy for some math operations, in that way we use:

1. concatenate method: To merge several MDF Files into 1 file.
2. resample method: To resample the file into the wanted time sampling. (Uses interpolation)
3. cut method: To cut the file from start time and end time variables. (Expects that the mdf file start time is less than wanted start time and end time is greater than wanted end time)
4. to_dataframe: Used to further print a pandas dataframe that corresponds to the new file.
5. insert: Insert list as column in dataframe.
6. ExcelWriter: For excel generation and styling.

For more information about asammdf, visit asammdf API: https://asammdf.readthedocs.io/en/master/api.html#

IMPORTANT Information:
1: This code was made for specific needs, to adjust to your needs needs to be substantially changed.
2: The excel export uses Excel map files and interpolation to generate new data and introduce it into the dataframe, you will probably don't need that so just DELETE it if you clone the repo.
3: The saving of the files is done with a writen absolute path and then saves with the filename with the activity of that day and the date extracted from the MDF File.

To change signals according to your needs:
  Change the: required_channels list:
  
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


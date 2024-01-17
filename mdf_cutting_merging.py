import numpy as np
import pandas as pd
from asammdf import MDF, Signal, blocks

path_list = [] # Here goes the path of your files

start = input("Introduce the start time in 2 digit format as the following HH:MM ")

end = input("Introduce the end time in 2 digit format as the following HH:MM ")

date = input("Introduce the date together as YYYYMMDD ")

start_minutes = (int(start[0:2]) * 60) + (int(start[3:]))
end_minutes = (int(end[0:2]) * 60) + (int(end[3:]))

required_channels = [] # Here goes the channels that map your measured variables
mdf_list = []
for path in path_list:
    mdf_list.append(MDF(path,required_channels))

mdf_merged = MDF.concatenate(mdf_list, sync = True)
mdf_merged = mdf_merged.resample(raster = 1, time_from_zero = True) #Resample to every second already adjusting the timezone to Kigali Rwanda time (+2)

mdf_hours_start = int(f"{mdf_merged.start_time:%H}") 
mdf_minutes_start = int(f"{mdf_merged.start_time:%M}")

position = int(path.find(date) + 8)
mdf_hours_end = (int(path[position:position+2]) + 2) # Add +2 to adjust time
mdf_minutes_end = (int(path[position+2:position+4]))

mdf_total_minutes_start = mdf_hours_start * 60 + mdf_minutes_start
mdf_total_minutes_end = mdf_hours_end * 60 + mdf_minutes_end


if (mdf_total_minutes_start < start_minutes) and (mdf_total_minutes_end > end_minutes):
    st = (start_minutes - mdf_total_minutes_start) * 60
    sop = (end_minutes - mdf_total_minutes_start)* 60
    mdf_merged = mdf_merged.cut(start = st, stop = sop, time_from_zero = True)

print(mdf_merged.to_dataframe(channels=required_channels))

mdf_merged.save(f"Documents/files/Merged_filtered_files/{path[path.find(date):path.find(date)+8]}_{mdf_hours_end}_{mdf_minutes_end}_{path[path.find('CAN'):]}", overwrite=True)

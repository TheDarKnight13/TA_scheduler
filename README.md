# TA_scheduler
This is Python script can automatically generate a schedule based on the availability of the TAs.

## Getting started 
The recommended setup steps are as follows:
1. Install  [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html) and create an environment.
2. Install the Google [OR-tools library](https://pypi.org/project/ortools/)
3. Ensure that the file structure is as follows: \
    ├── Folder \
  &emsp;   ├── Scheduler.py               # The python script \
  &emsp;   ├── Availability.csv           # Any TA availability csv file that you want to bulid a schedule for \

 ## Availability CSV file format
 The format of the availability csv file should strictly follow the 2 example csv files in this repo. \
 The first row should contain the name of the days followed by the slot timings for each day in the second row. The subsequent rows should contain the TA availability (1 for available and 0 for not available) with the first column containing the TA name.

 ## Generating the Schedule
 To generate the schedule, run the following command in your conda environment :\
 ```bash
python Scheduler.py -f availability.csv
```
The generated schedule will automatically be printed in a .txt file within the same folder.

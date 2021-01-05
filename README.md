# mythicwind

## Overview

This repository contains scripts, libraries and notebooks used to investigate data from an offshore measurement campaign conducted during the installation of the offshore wind [farm trianel wind farm borkum II](https://www.trianel-borkumzwei.de/). 
The wind farm consists of 32 Senvion 6XM152 turbines. The installation took place between August 2019 and May 2020. 

An offshore wind turbine undergoing installation is interesting from a research point of view for several reasons:
- Simple geometry: turbine foundation and tower are both rotationally symmetric steel tubes. Rotational symmetry also leads to (approximate) isotrope structural characteristics in the plane normal to tower and foundation.
- High Reynolds number flow: Assuming a tower diameter of 6 m, and average wind speeds ranging from 5 m/s to 12 m/s under installation conditions, Reynolds numbers range from 4.5 million to 10.5 million. 
- Wave loading und full scale conditions.
- Practical relevance to improving the competability of offshore wind.

For fluid mechanics, closely monitoring offshore wind turbines under wind and wave loading thus compares to a full scale experiment. Monitoring 32 turbines undergoing installation thus enables the measurement a broad spectrum of different states. 

## Raw data and data publication

Data is publicly available at <http://doi.org/10.5281/zenodo.4141208>

Investiagtions are ongoing, questions and contributions are welcome.

First results can be found here:

```
**OMAE 2020 :** Sander, A, Haselsteiner, AF, Barat, K, Janssen, M, Oelker, S, Ohlendorf, J, & Thoben, K. "Relative Motion During Single Blade Installation: Measurements From the North Sea." Proceedings of the ASME 2020 39th International Conference on Ocean, Offshore and Arctic Engineering. Volume 9: Ocean Renewable Energy. Virtual, Online. August 3–7, 2020. V009T09A069. ASME. https://doi.org/10.1115/OMAE2020-18935
```

```
**EURODYN 2020 :** Sander, A, Meinhardt, C & Thoben, KD. "Monitoring of Offshore Wind Turbines under Wind and Wave Loading during Installation" Proceedings of the EuroDyn 2020 XI International Conference on Structural Dynamics. Volume 1. Virtual, Online. November 23-26, 2020. https://generalconferencefiles.s3-eu-west-1.amazonaws.com/eurodyn_2020_ebook_procedings_vol1.pdf
```

### Organization of data

All data is stored in the data directory. NOTE: due to size limitations of git, the data is stored on [zenodo](http://doi.org/10.5281/zenodo.4141208)
For each turbine installation, a seperate folder can be found, e.g. turbine_01 for the first and turbine_16 for the 16th turbine. Turbine numbering follows the order of installation. 

Different data sources are organized in subfolders for each turbine dataset. Unfortunately, not every data source is available for each turbine.
Data sources are roughly sorted into categories. The following table lists these categories:

| Data type / data source | Description                                                            |
|-------------------------|------------------------------------------------------------------------|
| msr / location          | acceleration measurements, obtained by commercial accelerometer. For details, please refere to the [data description](doc/msr_data_description.md) |
| tom / location          | data from custom build sensor boxes. Data includes acceleration, angular acceleration, magnetic field, gnss recording and rough estimates of the eulerian angles. For detail refere to the [data description](doc/tom_data_description) |
| waves/wave_buoy         | Sea state statistics for the installatin period of the turbine. Details can be found in the [data description](doc/wave_buoy_data_description.md) | 
| waves/fino              | Sea state statistics from the german research platform [FINO1](htttps://) located approx. 6 km from the installation site.  Data description [here](doc/fino_wave_data_description.md) | 
| waves/wave_radar        | Sea state statstics, recorded by a wave rider wave laser. Data description is available in the [docs](doc_waverider_waves_data_description.md)
| wind/lidar              | high fidelity wind data recorded on the installation vessel during the installation of the wind farm. Details regarding data recording and data format can be found [here](doc/lida_data_description.md) | 
| wind/scada              | 10 min. mean wind statistisc recorded on wind turbines in the vicinity of the installation site. This data is used in case no LIDAR data is available. Data description can be found [here](doc/scada_data_description.md) | 
| wind/anemometer         | During some of the installations, anemometers were present on the installation vessel. These recordings are sorted into this sub-subfolder. Data description is available [here](doc/anemometer_data_description.md) | 
| wind/fino               | Additonal wind statistics recorded by the FINO research station. Least recommended for investigations, as these recordings were taken approx. 6 km from the installation site. Data description [here](doc/fino_wind_data_description.md) | 


The data directory is hence organized in the following order: 

```
data
└── turbine_12
    ├── data_type_1
    │   ├── data_source_1
    │   │   ├── clean # -> contains sanitized measurement data (e.g. time zones, resampling)
    │   │   └── raw
    │   │       └── measurement-start_measurement-end # -> raw data as recorded during the measurement campaign
```

As an example, the (incomplete) data from turbine_12 is listed below:

```

data
└── turbine_12
    ├── msr
    │   ├── sbitroot
    │   │   └── raw
    │   │       └── 2019-11-05_2019-11-08
    │   │           └── msr327234_191105_004503_sbit_root.txt
    │   ├── sbittip
    │   │   └── raw
    │   │       └── 2019-11-05_2019-11-08
    │   │           └── msr327233_191105_003530_sbit-tip.txt
    │   └── towertop
    │       └── raw
    │           └── 2019-11-05_2019-11-08
    │               └── msr327230_191104_175135_tower.txt
    ├── tom
    │   ├── helihoist
    │   │   ├── clean
    │   │   └── raw
    │   │       └── 2019-11-04_2019-11-08
    │   │           ├── log_0000.txt
    │   │           ├── log_0001.txt
    │   │           ├── log_0002.txt
    │   │           ├── ...
    │   ├── sbitroot
    │   │   └── raw
    │   │       └── 2019-11-04_2019-11-08
    │   │           ├── log_0000.txt
    │   │           ├── log_0001.txt
    │   │           ├── log_0002.txt
    │   │           ├── ...
    │   ├── sbittip
    │   │   └── raw
    │   │       └── 2019-11-04_2019-11-08
    │   │           ├── log_0000.txt
    │   │           ├── log_0001.txt
    │   │           ├── log_0002.txt
    │   │           ├── ...
    │   ├── towertop
    │   │   └── raw
    │   │       └── 2019-11-04_2019-11-08
    │   │           ├── log_0000.txt
    │   │           ├── log_0001.txt
    │   │           ├── log_0002.txt
    │   │           ├── ...
    │   ├── towertransfer
    │   │   └── raw
    │   │       └── 2019-11-04_2019-11-08
    │   │           ├── log_0000.txt
    │   │           ├── log_0001.txt
    │   │           ├── log_0002.txt
    │   │           ├── ...
    │   └── tp
    │       └── raw
    │           └── 2019-11-04_2019-11-08
    │               ├── log_0000.txt
    │               ├── log_0001.txt
    │               ├── log_0002.txt
    │               ├── ...
    ├── waves
    │   └── wave_buoy
    │       ├── clean
    │       │   └── turbine_12-waves-wave_buoy-clean-2019-11-04_2019-11-08.pickle
    │       └── raw
    │           └── 2019-11-05_2019-11-08
    │               └── wmb_sued_twb_ii_04.11.19_-_08.11.19.xls
    └── wind
        └── lidar
            ├── clean
            │   └── turbine_12-wind-lidar-clean-2019-11-04_2019-11-08.pickle
            └── raw
                └── 2019-11-05_2019-11-08
                    ├── 1708-lidar-log-190809_-_logfile_04nov19.csv
                    ├── 1708-lidar-log-190809_-_logfile_05nov19.csv
                    ├── 1708-lidar-log-190809_-_logfile_06nov19.csv
                    ├── 1708-lidar-log-190809_-_logfile_07nov19.csv
                    └── 1708-lidar-log-190809_-_logfile_08nov19.csv

```


### Physical background



- Definition, provenance, and interpretation of each variable
- Groups of variables
- Units of measurement
- Data formatting
  - Naming
  - Time
  - Epoch + Time zone
  - Periods
  - Matching
  - Imputation
  - "Encoding" (e.g. pickle, csv, json, sqlite, ...)
    - Constraints and guarantees
    - Normalization and views
    - Data types for subsequent processing (-> scikit-learn, nltk)
    - ML: Validation split

### Data loading API (-> scikit-learn, nltk)

- Download in the background
- Time conversion sugar
- Code refers to data and vice versa

## Data processing

### Cleaning

- Installation phases
- Matching (in time)
- ...

### Analysis of Orbits

- Butterworth
- Amplitude envelope

from collections import defaultdict, namedtuple

time_window = namedtuple('time_window', ("start", "stop"))



turbine_metadata = {

    "turbine_name" : str(),

    "nacelle_orientation" : 0,

    "available_positions" : {

        "helihoist-1" : {
            "fore-aft" : str(),
            "side-side" : str(),
        },
        
        "helihoist-2" :  {
            "fore-aft" : str(),
            "side-side" : str(),
        },
        
        "sbittip" : bool(),
        "sbitroot" : bool(),
        "damper" : bool(),
        "towertransfer" : bool(),
        "tp" : bool(),
    },

    "installation_turbine" : {
        "start" : 0,
        "stop" : 0,
    },
    
    "installation_tower" : {
        "start" : 0,
        "stop" : 0,
    },
    
    "installation_nacelle" : {
        "start" : 0,
        "stop" : 0,
    },
    
    "installation_blade_1" : lambda x : time_window(start=x[0], stop=x[1]),
    
    "installation_blade_2" : {
        "start" : 0,
        "stop" : 0,
    },
    
    "installation_blade_3" : {
        "start" : 0,
        "stop" : 0,
    },
    
    "failed_installation_attempts" : list(),
    
    "damper_active" : list(),
    
    "vessel" : str(),
}
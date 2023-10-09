from treemap import *

inextensive("states_hispanicpop.txt","states_population.txt",
            "Hispanic/Latino population (area) and relative fraction of population (color)",
            160,60,110);

printme(plt,filename='hispanicpop.pdf')

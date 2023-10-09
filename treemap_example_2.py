from treemap import *

redblue("states_pct_reps_2022.txt","states_pct_dems_2022.txt","states_electoralvotes.txt",
    "Electoral votes (area) and party predominance (color)")

printme(plt,filename='red_blue_electoral_votes.pdf')

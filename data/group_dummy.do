sysdir

// Put the file provided by Hiro into the PERSONAL folder

cd "C:\Users\jamel\Documents\GitHub\cab-persistency\data"

import excel ///
"C:\Users\jamel\Documents\GitHub\cab-persistency\data\reg_data.xlsx", ///
sheet("Feuil1") firstrow

destring pct_ca_reg, replace force

group_dummy

save reg_data_group_dummy.dta, replace
**# *** Current account balance data ***

*ssc install dbnomics

*ssc install libjson

*ssc install moss

cd "C:\Users\jamel\Dropbox\Latex\"

cd "PROJECTS\22-11-cur-persistence"

dbnomics data, provider(OECD) dataset(MEI) clear

dbnomics find "B6BLTT02.STSA.Q", clear // find a series

dbnomics import, provider(OECD) dataset(MEI) ///
sdmx(.B6BLTT02.STSA.Q) clear

split series_name, parse(–)

encode series_name1, generate(cn) 

rename series_name1 country_name

order cn country_name location value, first

destring value, replace force

split period_start_day, parse(-)

gen string = period_start_day3 +  "/" + period_start_day2 + ///
 "/" + period_start_day1

gen date2 = date(string, "DMY")

format date2 %td

generate qtr = quarter(date2)

generate yq = qofd(date2)

format yq %tq

xtset cn yq, quarterly

xtdescribe

tsset cn yq 

tsfill, full

order cn yq value

rename value ca

decode cn, generate(countryname)

order countryname cn yq ca, first

drop country_name location period period_start_day frequency ///
dataset_code dataset_name FREQUENCY measure subject ///
indexed_at provider_code series_code series_name ///
series_num series_name2 series_name3 series_name4 ///
series_name5 period_start_day1 period_start_day2 ///
period_start_day3 string date2 qtr

xtdescribe

xtset cn yq, quarterly

summarize ca

mdesc ca

tabstat ca, ///
statistics(count mean sd min max) by(cn) save

export delimited using "current_account", replace

export excel using "current_account", firstrow(variables) replace

save current_account, replace

use current_account, clear

by cn: gen time = _n

keep ca countryname time

reshape wide ca, i(countryname)  j(time)  

export excel using ///
"C:\Users\jamel\Dropbox\Latex\PROJECTS\22-11-cur-persistence\current_account_wide.xlsx", ///
firstrow(variables)

save current_account_wide, replace

**#********************************************************

// Descriptive statistics
// Author: Chau Nguyen


if "`c(username)'" == "WIN10" ///
	| "`c(username)'" == "MINHCHAU" ///
	| "`c(username)'" == "minhc" ///
	{
		global assignment "G:\.shortcut-targets-by-id\1bK5i-HiiYUoWJA43k2i12DogggzUsUlc\CA_2020\data"
		global assignment2 "G:\.shortcut-targets-by-id\1bK5i-HiiYUoWJA43k2i12DogggzUsUlc\CA_2020\"
}
*
global dofiles "G:\.shortcut-targets-by-id\1bK5i-HiiYUoWJA43k2i12DogggzUsUlc\CA_2020\stata-code\pre-processing"
global data_entry "$assignment\raw-data"
global data_temp "$assignment\temp-data"
global data_clean "$assignment\clean-data"
global data_regression "$assignment\regression-data"
global results "$assignment2\results"

set more off

use "$data_clean\Final entry dataset - adjusted", clear

keep cn code3 cname date2 pct_cab
sort code3 cname date2
by code3: egen count=total(pct_cab!=.)

drop if count<44

codebook code3

drop count
xtset cn date2

//tabulate code3, summarize(pct_cab)
gen pct_cab_start=.
	gen pct_cab_end=.
	bysort cname date2: replace pct_cab_start=date2 if pct_cab!=. & pct_cab[_n-1]==.
	bysort cname date2: replace pct_cab_end=date2 if (_n==_N & pct_cab!=.) | (pct_cab[_n+1]==.& pct_cab[_n]!=.)
	format pct_cab_start %tq
	format pct_cab_end %tq
	
*quietly do "$dofiles\cn_full_name_number_updated.do"
collapse (mean) mean=pct_cab (sd) sd=pct_cab (min) min=pct_cab (max) max=pct_cab (min) start =*_start (max) end=*_end (count) n=pct_cab, by(cn cname code3)

la var cname  "Country"
la var cn     "IMF code"
la var code3  "ISO code"
la var mean   "Mean"
la var sd     "SD"
la var min    "Min"
la var max    "Max"
la var start  "Start date"
la var end    "End date"
la var n	  "# observations"

export excel using "$results\summary statistics.xlsx", firstrow(varlabels) replace

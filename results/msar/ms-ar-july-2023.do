**#************ Markov Switching URT ***************************

capture log close

log using ms-ar-july-2023.log, replace

cls
clear

global Docs = "C:\Users\jamel\Dropbox\Latex\"
global Proj = "PROJECTS\22-11-cur-persistence\"
global Data = "data\seasonal_adjustment\comparison"
global Fig = "Figures\"
 
cd "${Docs}"
cd "${Proj}"
cd "${Data}"

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

label list cn_2
xtset cn_2 date3
xtdescribe

by cn_2: sum cab

// MS AR for the current account (ARG)

label list cn_2

keep if cn_2==1
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch
mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (ARM)

label list cn_2

keep if cn_2==2
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (AUS)

label list cn_2

keep if cn_2==3
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (AUT)

label list cn_2

keep if cn_2==4
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1 
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (BLR)

label list cn_2

keep if cn_2==5
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (BEL)

label list cn_2

keep if cn_2==6
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (BOL)

label list cn_2

keep if cn_2==7
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (BRA)

label list cn_2

keep if cn_2==8
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (BLG)

label list cn_2

keep if cn_2==9
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1 // State 1 Non-stationary
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (KHM)

label list cn_2

keep if cn_2==10
keep if date3<=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (CAN)

label list cn_2

keep if cn_2==11
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (CHL)

label list cn_2

keep if cn_2==12
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (CHN)

label list cn_2

keep if cn_2==13
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (COL)

label list cn_2

keep if cn_2==14
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (CRI)

label list cn_2

keep if cn_2==15
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (HRV)

label list cn_2

keep if cn_2==16
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1 // State 1 Non-stationary
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (CZE)

label list cn_2

keep if cn_2==17
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) // constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==18
*keep if date3>=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)

constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

*mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (SLV)

label list cn_2

keep if cn_2==19
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) 
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (EST)

label list cn_2

keep if cn_2==20
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (FIN)

label list cn_2

keep if cn_2==21
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account (FRA)

label list cn_2

keep if cn_2==22
*keep if date3>=tq(2019q4)

tsset date3

constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==23
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==24
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==25
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==26
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==27
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==28
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) varswitch vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==29
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==30
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==31
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==32
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==33
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

****************************************************************

use cis_quarterly_data_04_04_2023.dta, clear

// MS AR for the current account

label list cn_2

keep if cn_2==34
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==35
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==36
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch 
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==37
*keep if date3<=tq(2019q4)

tsset date3
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch 
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==38
*keep if date3<=tq(2019q4)

tsset date3
replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==39
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==40
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==41
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==42
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==43
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==44
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==45
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==46
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==47
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==48
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==49
*keep if date3<=tq(2019q4)

tsset date3
*replace cab = l.cab in 253 
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==50
*keep if date3<=tq(2019q4)

tsset date3
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==51
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==52
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==53
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==54
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==55
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==56
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==57
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==58
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==59
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==60
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==61
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==62
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

// MS AR for the current account

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==63
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - Thailand

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==64
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace

local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - Turkey

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==65
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace					
					
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - United Kingdom

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==66
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State1]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace					
					
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - United States

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==67
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace					
					
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - Uruguay

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==68
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace					
					
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - Venezuela

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==69
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust) varswitch
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1) varswitch
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')

local v = cn_2[1]					
graph export probas\ms_`v'.png, replace					
					
local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# MS AR for the current account - Vietnam

use cis_quarterly_data_04_04_2023.dta, clear
label list cn_2

keep if cn_2==70
*keep if date3<=tq(2019q4)

tsset date3
/*
replace cab = l.cab in 91
replace cab = l.cab in 93 
replace cab = l.cab in 95
replace cab = l.cab in 97
replace cab = l.cab in 99
replace cab = l.cab in 101
replace cab = l.cab in 103
*/
mswitch ar cab, arswitch ar(1) vce(robust)
constraint 1 [State2]L1.ar=1
*constraint 2 [State2]L1.ar=0.5

mswitch ar cab, arswitch ar(1) vce(robust) constraint(1)
*mswitch ar cab, arswitch ar(1) vce(robust)
*mswitch ar cab, arswitch ar(1) varswitch vce(robust) constraint(1)

*ereturn list

test (_b[State1:L.ar] -1 = 0)
local sign_ag = sign(_b[State1:L.ar] -1)
display "H_0: _b[State1:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

test (_b[State2:L.ar] -1 = 0)
local sign_ag = sign(_b[State2:L.ar] -1)
display "H_0: _b[State2:L.ar] -1  coef. p-value = "          ///
normal(`sign_ag'*sqrt(r(chi2)))

*ereturn list

estat transition
estat duration

capture drop pr
local t = ccode[1]
predict pr, pr smethod(smooth)

capture drop cap
predict cap, yhat smethod(smooth)

capture graph drop predict
capture graph drop states_`t'

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'"))                  ///
 (tsline cap if cab!=.,legend(pos(6))), name(predict)

local t = ccode[1]
twoway (tsline cab if cab!=., title("`t'") yline(0))         ///
                   (tsline pr if cab!=., yaxis(2)            ///
                    yscale(range(-5 5) axis(1))              ///
                    yscale(range(0 1) axis(2))               ///
                    yline(0.5, axis(2)) legend(off)),        ///
					name(states_`t')
					
local v = cn_2[1]					
graph export probas\ms_`v'.png, replace

local t = ccode[1]
keep date3 cn cn_2 ccode cab pr

local t = ccode[1]				
save "probas\prob_`t'.dta", replace

**# Creating Word document

putdocx clear

putdocx begin

// Create a paragraph
putdocx paragraph
putdocx text (" CAB and MS AR "), bold
*putdocx text ("can add formatted text to a paragraph.  You can ")
*putdocx text ("italicize, "), italic
*putdocx text ("strikeout, "), strikeout
*putdocx text ("underline"), underline
*putdocx text (", sub/super script")
*putdocx text ("2 "), script(sub)
*putdocx text (", and ")
*putdocx text ("shade"), shading("blue")


/*
forvalues v=1(1)70 {
	xtline pct_ca pct_ca_sa_2 if cn_2 == `v' ///
			  , ylabel(, angle(horizontal)) tlabel(, grid) ///
			  xsize(10) yline(0)
              capture graph rename ca_`v', replace
			  capture graph export figures\ca_`v'.png, replace
              *capture graph export cap_check_`cn'.pdf, replace
			  *graph close cap_check_`cn'
}
*/

/*
// Embed a graph
forvalues v=1(1)70 {
	*graph export ca_`v'.png
    putdocx paragraph, halign(center)
    putdocx image figures\ca_`v'.png
}
*/

*putdocx text (" New data and seasonally adjusted old data "), bold

/*
forvalues v=1(1)70 {
	xtline ca pct_ca_sa_2 if cn_2 == `v' ///
			  , ylabel(, angle(horizontal)) tlabel(, grid) ///
			  xsize(10) yline(0)
              graph rename cab_`v', replace
			  capture graph export figures\cab_`v'.png, replace
              *capture graph export cap_check_`cn'.pdf, replace
			  *graph close cap_check_`cn'
}
*/

// Embed a graph
forvalues v=1(1)70 {
	*graph export ca_`v'.png
    putdocx paragraph, halign(center)
    putdocx image probas\ms_`v'.png
}

/*
No seasonal adjustment
Bolivia Brazil China Iceland Indonesia Ireland 
Norway Switzerland Venezuela

encode CN, generate(CN2)

label list CN2

foreach v in 7 8 13 29 31 32 48 62 69 {
	xtline ca pct_ca if CN2 == `v' ///
			  , ylabel(, angle(horizontal)) tlabel(, grid) ///
			  xsize(10) yline(0)
              graph rename cac_`v', replace
			  capture graph export figures\cac_`v'.png, replace
              *capture graph export cap_check_`cn'.pdf, replace
			  *graph close cap_check_`cn'
}

// Embed a graph
foreach v in 7 8 13 29 31 32 48 62 69 {
	*graph export ca_`v'.png
    putdocx paragraph, halign(center)
    putdocx image figures\cac_`v'.png
}

*/

putdocx save cab-msar.docx, replace

log close
exit
## Umbrella Problem

Cost of dependency _ we have it 
cost of fix code _ we have it 
cost of escelate _ we have it 

if expected cost of fix code = expected cost of escelate that's the tipping point

#	Hidden State	Count	Prior P(S)
S1	Source Code Issues	15	0.0265
S2	Project Config Issues	33	0.0582
S3	Dependency Failures	177	0.3122
S4	Static Analysis Failures	236	0.4162
S5	Test Failures	66	0.1164
S6	Environment Setup Issues	32	0.0564
S7	Other	8	0.0141
TOTAL	567	1.0000

Cost of correct fix code : 8.33$ in spot check
Cost of wrong fix code:75.07$

P(fix_code_isse)  = P(S1) + P(S2) + P(S4) = 
P(dependency_error_issue) = P(S3) = 

EC(Fix code) = P(fix_code_issue) * 8.33 + (1- P(fix_code_issue)) * 75.07
EC(Escelate) = 50$

I'm asking at what P(fix_code_issue) does fixing code and escelating has same cost, it's 37.5%, if probability fix code is more than 37.5% we fix code.

After doing calculatins for dependency issue too, tipping turns out to be same 37.5%.

But if both of them exceeds 37.5%, let's say

P(code)=45%,P(dep)=40%

We calculate expected cost of fixing code vs dependency and choose the action,either ways it's cheaper than escelating to human.


But if let's say we make dependency fix and it breaks production, it costs of let's say $5000 then,

Row: Fix Dependency
State	Cost	Status	Reason & Calculation
S1	$75.07	ASSUMED	Wrong action. Triggers misdiagnosis chain: wrong patch review (15 min = $25.00) + CI rerun ($0.07) + manual re-diagnosis (30 min = $50.00) = $75.07.
S2	$75.07	ASSUMED	Wrong action. Same misdiagnosis chain as S1. Dependency change does not fix project config.
S3	$8.33	ASSUMED	Correct action. Agent fix is automated ($0.00) + human verification 5 min × ($100 / 60) = $8.33.
S4	$75.07	ASSUMED	Wrong action. Same misdiagnosis chain. Dependency change does not fix lint/static analysis issue.
S5	$75.07	ASSUMED	Wrong action. Same misdiagnosis chain. Dependency change does not fix test failure.
S6	$75.07	ASSUMED	Wrong action. Same misdiagnosis chain. Dependency change does not fix environment setup issue.
S7	$75.07	ASSUMED	Wrong action. Same misdiagnosis chain. Dependency change does not fix transient/external failure.


Let's say dependency fix is made, but in reality it was issue with project-config, it generated fix, code passes ci test goes to production breaks, cost of wrong dependecy fix  = $5000 assuming

then tipping point is 99.17%​ not 37.5%, the cost of wrong dependecy fix is exponentially higher.

Thresholds depends on cost and our belief of how likly a failed outcome is.



## Generalization challange
Let's say 
Dimeantions of the environment, f(company scale,geography,engineering labor,CI infrastructure,production risk,architecture,regulation,team structure,deployment process)
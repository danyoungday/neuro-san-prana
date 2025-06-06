# OxCGRT technical documentation

# Codebook and interpretation guidance
--[return to top](#)--

## C - containment and closure policies
--[return to top](#)-- <br/>
--[return to start of codebook](#codebook-and-interpretation-guidance)--

| ID | Name | Description | Measurement | Coding |
| --- | --- | --- | --- | --- |
| C1 | `C1E_School closing`<br/> `C1NV_School closing`<br/> `C1V_School closing`<br/> `C1M_School closing`| Record closings of schools and universities | Ordinal scale | 0 - no measures <br/>1 - recommend closing or all schools open with alterations resulting in significant differences compared to non-Covid-19 operations <br/>2 - require closing (only some levels or categories, eg just high school, or just public schools) <br/>3 - require closing all levels <br/>Blank - no data |

## General interpretation guidance
--[return to top](#)-- <br/>
--[return to start of codebook](#codebook-and-interpretation-guidance)--

There are a few general rules that apply to our data:

 - **We report the most stringent government policy** with the highest ordinal value. If the most stringent policy is only present in a limited geographic area or sector, we use a binary flag variable for most indicators to describe this scope and reflect whether the policy is targeted or general.
- **Implementation not announcement:** We start coding a policy from the day the policy was implemented in practice, not the day it was announced (except for `V1`, where the policy being recorded is the announced prioritisation list, not the actual availability of vaccines).
 - **If coding a country with a contested government or multiple ruling parties**, we try to code the “dominant tendency” in the jurisdiction, which generally means recording the policies of the more formalised government, or the one which governs the larger proportion of the population
 - **Where testing/vaccination exemptions are in place we still report this as a closure**. Some governments implement restrictions where citizens can gain exemption through evidence of testing or vaccination. We deal with this primarily through our differentiated coding (see more below). But the general rule is that – apart from differentiated coding – we still report the more stringent government policy that applies to people who do not obtain an exemption. The only time we would report the more open policy is if anyone can arrive and get tested onsite with a rapid test to gain entry. We would not code this as a required closure, as anyone can ‘test out’ of restrictions easily. Such at-the-door testing must apply to all sectors within the indicator, and be a government policy, not that of a private business.

## Common issues
--[return to top](#)-- <br/>
--[return to start of codebook](#codebook-and-interpretation-guidance)--

### Delineating between policy levels 0 and 1
In many of our indicators, the line between level 0 and level 1 is blurry – it is often the difference between “no policy” and a “recommendation” to avoid some activity. This can create issues when policies are reduced over time and any residual precautions could reasonably be interpreted as either a 0 or a 1. In practice, this means care should be taken in assuming a strict difference between 0 and 1 policies, as it often comes down to the judgement of our data collectors.

Our general rule is that 0 reflects a state that is comparable to pre-covid times, whereas a 1 would reflect significant differences from pre-covid operational norms. The table below provides examples of residual precautions that would indicate a 0 or a 1.

Table 5. Comparison of policies that would be rated a 0 or a 1:
| **0 – Equivalent/comparable to pre-Covid times** | **1 – Significant differences to pre-Covid times, significant behavioural and/or operational differences**|
| --- | --- |
No social distancing <br /> Full capacity <br /> Regular opening hours <br /> Any recommended change to operations (such as use of facial coverings) that is not a recommendation to close | Regular Lateral Flow Testing <br /> Social distancing <br />  Altered operating times <br /> Reduced capacity <br /> Use of close contact bubbles <br /> Significant cleaning and ventilation <br /> Requirement to check in with track and trace  |

## Detailed interpretation guidance for each indicator
--[return to top](#)-- <br/>
--[return to start of codebook](#codebook-and-interpretation-guidance)--

### C1 - School Closures
- `C1` reports closures of both schools and universities. It does not report closures of childcare, nurseries, language courses, and driving schools, which are instead recorded as workplaces under `C2`.
- If in-person teaching is suspended and all  instruction is online, this is reported as closed (physically closed). Some governments use different wording (eg. soft-closing, recommend without restricting civil liberty), but if the situation is that schools are closed, or policies make it impossible for them to open, then we report a full closure even if schools are theoretically allowed to open.
- If schools are closed, and this same closure policy then rolls into school holidays, we keep the code the same, for example ‘all levels of education remain closed’. This coding would only go down only once students actually return, when schools reopen.
- If only children of essential workers are allowed in schools, this is reported as a closure for the general public.
- Some schools only open for exams, but not for classes. In this case, if schools are open for a one-off exam, for example one that is an hour long, or on one day only, this would not change the coding. If exams are running for multiple sessions, on multiple days, or even over multiple weeks, this is a similar situation to classes being open for some groups during that time (`C1`=2).
- If teachers are back in school to prepare for the new school year, but no students are allowed back, this would not count as open.
- If individual school districts have the authority to decide closures/openings, we generally record closures conservatively with a ’targeted’ flag, as recording ‘general’ policies would require a high level of confidence that every single schools in a jurisdiction are closed.
- Summer school counts as school. If schools have been closed (`C1`=3) but then some summer school is allowed, the value would change (likely `C1`=3 and `C1_Flag`=0 if some school districts remain totally closed, or `C1`=2 and `C1_Flag`=1 if summer school has a ‘general’ country/territory wide scope). Summer school or other vacation-based programming includes substantial school-run educational programming such as entrance examination classes, remedial classes, or summer term courses, but does not include more peripheral activities such as recreational summer camps.
- If a narrowly defined list of university courses which rely on essential in-person teaching, for example medical programs, are permitted to operate as an exemption, but all other in-person university teaching is cancelled, we treat this as a closure of universities.

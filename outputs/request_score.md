# Five Safes score of our request (Week 10 rubric)

## Blood pressure control in small vs large towns of Crete (as submitted)

- **Applicant:** Public health research group, a Greek university medical school (fictional)
- **Asks for:** patients.csv without names, with full date of birth, sex, town and postcode; all hypertension diagnoses; every blood pressure reading with its date; antihypertensive prescriptions; the patient Id to join them
- **Purpose:** whether blood pressure control is worse in the smaller towns, by age band and sex
- **Setting:** the group's shared university file server
- **Outputs:** a journal article and a conference poster

| safe | criterion | met | reason |
|---|---|---|---|
| people | P1: the applicant has completed accredited researcher training | ✘ | the PhD student who will run the analysis has no accredited researcher training |
| people | P2: a named accountable organisation employs or supervises the applicant | ✔ | a named principal investigator and a university that can be held to account |
| people | P3: the organisation has signed an agreement with enforceable sanctions | ✘ | no data access agreement yet; the request arrived as a letter |
| projects | J1: the purpose has a documented lawful basis and an ethics approval | ✘ | ethics application submitted to the university committee, not yet approved |
| projects | J2: a public benefit follows that does not depend on who profits | ✔ | unequal hypertension care across Crete is a public health question with a public answer |
| projects | J3: the fields requested are the minimum the question needs | ✘ | full date of birth, postcode, prescriptions and every reading exceed the stated analysis |
| settings | S1: the analysis runs in an environment the controller operates | ✘ | the university file server is not operated by the hospital |
| settings | S2: no record-level copy leaves that environment | ✘ | the request is for a record-level copy to leave the hospital |
| settings | S3: access is logged and somebody reviews the log | ✘ | the shared drive has no access log that anybody reads |
| data | D1: direct identifiers are removed | ✔ | names, SSN, address and contact fields are not requested |
| data | D2: no linkage key usable outside the environment is supplied | ✘ | the hospital patient Id joins every table and any other release made with it |
| data | D3: dates and geography are no finer than the question needs | ✘ | full date of birth and postcode for a question asked by age band and town |
| outputs | O1: what leaves is aggregate, not record level | ✔ | an article and a poster are aggregate |
| outputs | O2: an independent checker reviews every output before release | ✘ | only the co-authors read the tables before publication |
| outputs | O3: a cumulative record of this project's past outputs is kept and consulted | ✘ | no record of what has already been published from the data |

Per safe: people 1/3 · projects 1/3 · settings 0/3 · data 1/3 · outputs 1/3

**Total 4/15 → REFUSE** (a safe scored zero: settings)

Criteria still not met, and what the rubric would ask for:
- P1: require accredited training before any access is granted
- P3: execute a data access agreement with named penalties before release
- J1: obtain ethics committee approval and record the lawful basis
- J3: cut the request to the fields the stated analysis uses
- S1: move the analysis into the trusted research environment
- S2: forbid download; the researcher works at the data, the data does not travel
- S3: name the person who reads the access log and how often
- D2: replace any national identifier with a project-specific pseudonym held by the controller
- D3: generalise birth date to year and postcode to regional unit
- O2: route every export through output checking by somebody not on the project
- O3: maintain an output register and check each new request against it

## Blood pressure control in small vs large towns of Crete (with conditions met)

- **Applicant:** Public health research group, a Greek university medical school (fictional)
- **Asks for:** one row per patient: age, sex, town and controlled yes/no, derived by the hospital and then generalised and suppressed by WP2; no identifier of any kind
- **Purpose:** whether blood pressure control is worse in the smaller towns, by age band and sex
- **Setting:** a named, access-controlled university server; the copy is destroyed at the end
- **Outputs:** aggregate tables and model summaries, checked by the hospital before publication

| safe | criterion | met | reason |
|---|---|---|---|
| people | P1: the applicant has completed accredited researcher training | ✔ | condition: the analyst completes accredited researcher training before access |
| people | P2: a named accountable organisation employs or supervises the applicant | ✔ | a named principal investigator and a university that can be held to account |
| people | P3: the organisation has signed an agreement with enforceable sanctions | ✔ | condition: a signed data access agreement with named sanctions and an audit right |
| projects | J1: the purpose has a documented lawful basis and an ethics approval | ✔ | condition: ethics approval granted; basis GDPR Art 6(1)(e) with Art 9(2)(j) and Art 89 safeguards |
| projects | J2: a public benefit follows that does not depend on who profits | ✔ | unequal hypertension care across Crete is a public health question with a public answer |
| projects | J3: the fields requested are the minimum the question needs | ✔ | minimised to the four columns the analysis uses (see request.md) |
| settings | S1: the analysis runs in an environment the controller operates | ✘ | still the university's server, not the hospital's: a safeguarded release, not a TRE |
| settings | S2: no record-level copy leaves that environment | ✘ | a record-level file still leaves the hospital; this is why the data itself must be protected |
| settings | S3: access is logged and somebody reviews the log | ✔ | condition: access to the folder is logged and the PI reviews the log monthly |
| data | D1: direct identifiers are removed | ✔ | no direct identifiers in the extract |
| data | D2: no linkage key usable outside the environment is supplied | ✔ | no patient Id and no pseudonym in the release; the hospital alone keeps the keyed pseudonym |
| data | D3: dates and geography are no finer than the question needs | ✔ | age instead of date of birth, no dates at all, no postcode; generalised further by WP2 |
| outputs | O1: what leaves is aggregate, not record level | ✔ | only aggregate tables and model summaries may be published |
| outputs | O2: an independent checker reviews every output before release | ✔ | condition: every output is checked by the hospital custodians against the output rule |
| outputs | O3: a cumulative record of this project's past outputs is kept and consulted | ✔ | condition: a cumulative release register is kept and consulted (WP3) |

Per safe: people 3/3 · projects 3/3 · settings 1/3 · data 3/3 · outputs 3/3

**Total 13/15 → APPROVE WITH CONDITIONS** (total 13 of 15, weakest safe at 1)

Criteria still not met, and what the rubric would ask for:
- S1: move the analysis into the trusted research environment
- S2: forbid download; the researcher works at the data, the data does not travel

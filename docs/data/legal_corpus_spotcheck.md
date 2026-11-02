# Legal Corpus Spot-Check and Water-Body Protection Relevance Audit

- **Date:** 2026-11-02
- **Corpus Version:** `2.1.0`
- **Scope:** 100% manual spot-check across all 30 authentic legal documents in `data/raw/legal/`, verifying Title, Issuer, and Date on Page 1 / Preamble against `data/raw/legal/manifest.json`.
- **RAG Tiering:** Categorization into `core`, `supporting`, and `background` tiers for grounded petition drafting.

---

## 1. Complete 30-Document Spot-Check Table

| ID | Document / File | Manifest Title | Page 1 / Enactment Title | Manifest Issuer | Page 1 Verified Issuer | Manifest Date | Page 1 / Gazette Date | Date Precision | As Enacted | Is Extract | RAG Role | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **LEGAL-001** | `LEGAL-001_TN_Protection_of_Tanks_and_Eviction_of_Encroachment_Act_2007.pdf` | Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Act 8 of 2007) | The Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Act No. 8 of 2007) | Legislative Assembly of Tamil Nadu (Law Dept Gazette) | Tamil Nadu Legislative Assembly / Law Department | 2007-05-22 | Assent: 2007-05-22; Gazette: 2007-05-23 (No. 148) | `exact` | `true` | `false` | `core` | `PASS` |
| **LEGAL-002** | `LEGAL-002_TN_Farmers_Management_of_Irrigation_Systems_Act_2000.pdf` | Tamil Nadu Farmers' Management of Irrigation Systems Act, 2000 (Act 7 of 2001) | The Tamil Nadu Farmers' Management of Irrigation Systems Act, 2000 (Act No. 7 of 2001) | Legislative Assembly of Tamil Nadu / PWD (WRD) | Tamil Nadu Legislative Assembly | 2001-02-25 | Assent: 2001-02-25; Gazette: 2001-03-05 (No. 178) | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-003** | `LEGAL-003_TN_Farmers_Management_of_Irrigation_Systems_Rules_2002.pdf` | Tamil Nadu Farmers' Management of Irrigation Systems Rules, 2002 | Rules to the Tamil Nadu Farmers' Management of Irrigation Systems Act, 2000 (Notification under s.50) | Public Works Department (WRD), Govt of Tamil Nadu | Governor of Tamil Nadu / PWD | 2002-01-01 | Rules cited as 2002; no G.O. printed on text | `year_only` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-004** | `LEGAL-004_TN_Land_Encroachment_Act_1905.pdf` | Tamil Nadu Land Encroachment Act, 1905 (Act III of 1905) | The Tamil Nadu Land Encroachment Act, 1905 (Tamil Nadu Act III of 1905) | Revenue Department, Government of Tamil Nadu | Legislative Council of Fort St. George / Revenue Dept | 1905-06-08 | Enacted: 1905-06-08; Gazette: 1905-06-13 | `exact` | `true` | `false` | `core` | `PASS` |
| **LEGAL-005** | `LEGAL-005_TN_Panchayats_Act_1994_Water_and_Minor_Irrigation_Excerpts.pdf` | The Tamil Nadu Panchayats Act, 1994 (Excerpts — Water Supply, Sanitation and Minor Irrigation Provisions) | The Tamil Nadu Panchayats Act, 1994 (Excerpts - water supply and sanitation provisions) | Rural Development and Panchayat Raj Department, Govt of Tamil Nadu | Tamil Nadu Legislative Assembly | 1994-04-22 | Assent: 1994-04-22; Gazette: 1994-04-22 | `exact` | `true` | `true` | `supporting` | `PASS` |
| **LEGAL-006** | `LEGAL-006_TN_State_Water_Policy_1994.pdf` | Water Policy for Tamil Nadu, 1994 (Policy Statement Excerpts as published by PWD) | Water Policy for Tamilnadu (Policy Statement) | Public Works Department (WRD), Govt of Tamil Nadu | P. Baskaradoss, Secretary to Government, PWD | 1994-07-01 | Adopted: 1994 (PWD policy statement) | `year_only` | `false` | `true` | `supporting` | `PASS` |
| **LEGAL-007** | `LEGAL-007_Chennai_Metropolitan_Area_Groundwater_Regulation_Act_1987.pdf` | Chennai Metropolitan Area Groundwater (Regulation) Act, 1987 (Act 27 of 1987) | The Chennai Metropolitan Area Groundwater (Regulation) Act, 1987 (Act No. 27 of 1987) | Legislative Assembly of Tamil Nadu / CMWSSB | Tamil Nadu Legislative Assembly | 1987-06-05 | Assent: 1987-06-05; Gazette: 1987-06-08 (No. 343) | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-008** | `LEGAL-008_TN_Municipal_Laws_and_CMA_Groundwater_Amendment_Act_2014.pdf` | Tamil Nadu Municipal Laws and CMA Groundwater (Regulation) Amendment Act, 2014 (Act 23 of 2014) | Tamil Nadu Municipal Laws and the Chennai Metropolitan Area Groundwater (Regulation) Amendment Act, 2014 (Act No. 23 of 2014) | Legislative Assembly of Tamil Nadu / MAWS Dept | Tamil Nadu Legislative Assembly | 2014-09-02 | Assent: 2014-09-02; Gazette: 2014-09-03 (No. 177) | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-009** | `LEGAL-009_TN_Groundwater_Development_and_Management_Act_2003.pdf` | Tamil Nadu Groundwater (Development and Management) Act, 2003 (Act 3 of 2003) | The Tamil Nadu Groundwater (Development and Management) Act, 2003 (Act No. 3 of 2003) | Legislative Assembly of Tamil Nadu / PWD (WRD) | Tamil Nadu Legislative Assembly | 2003-03-04 | Assent: 2003-03-04; Gazette: 2003-03-04 (No. 53) | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-010** | `LEGAL-010_Chennai_Metropolitan_Water_Supply_and_Sewerage_Act_1978.pdf` | Chennai Metropolitan Water Supply and Sewerage Act, 1978 (Act 28 of 1978) | The Chennai Metropolitan Water Supply and Sewerage Act, 1978 (Tamil Nadu Act No. 28 of 1978) | Legislative Assembly of Tamil Nadu | Tamil Nadu Legislative Assembly | 1978-06-08 | Assent: 1978-06-08; Gazette: 1978-06-14 (No. 268) | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-011** | `LEGAL-011_TN_District_Municipalities_Act_1920_Water_Sources_Excerpts.pdf` | The Tamil Nadu District Municipalities Act, 1920 (Excerpts — Water Supply, Drainage and Public Water Sources) | The Tamil Nadu District Municipalities Act, 1920 (Act V of 1920 — Water Excerpts) | Municipal Administration and Water Supply Department, Govt of Tamil Nadu | Legislative Council of Fort St. George | 1920-06-29 | Enacted: 1920-06-29; Gazette: 1920-07-06 | `exact` | `true` | `true` | `supporting` | `PASS` |
| **LEGAL-012** | `LEGAL-012_GO_Ms_96_RDPR_2019_Kudimaramath_Minor_Irrigation_Tanks.pdf` | G.O. (Ms) No. 96, RD&PR — Rejuvenation of Minor Irrigation Tanks under Kudimaramath | G.O. (Ms) No. 96, Rural Development and Panchayat Raj (CGS.1) Department | Rural Development and Panchayat Raj Department, Govt of Tamil Nadu | Hans Raj Verma, Additional Chief Secretary to Government | 2019-07-26 | Dated: 2019-07-26 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-013** | `LEGAL-013_GO_Ms_97_RDPR_2016_MGNREGS_Minor_Irrigation_Tank_Desilting.pdf` | G.O. (Ms) No. 97, RD&PR — MGNREGS Guidelines for Desilting Minor Irrigation Tanks | G.O. (Ms) No. 97, Rural Development and Panchayat Raj (CGS.1) Department | Rural Development and Panchayat Raj Department, Govt of Tamil Nadu | Hans Raj Verma, Principal Secretary to Government | 2016-08-29 | Dated: 2016-08-29 | `exact` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-014** | `LEGAL-014_GO_Ms_23_RDPR_2024_Rural_Water_Bodies_and_Infrastructure_Guidelines.pdf` | G.O. (Ms) No. 23, RD&PR — Guidelines for Rural Water Bodies and Minor Irrigation Tanks | G.O. (Ms) No. 23, Rural Development and Panchayat Raj (SGS.2) Department | Rural Development and Panchayat Raj Department, Govt of Tamil Nadu | P. Senthilkumar, Principal Secretary to Government | 2024-02-02 | Dated: 2024-02-02 | `exact` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-015** | `LEGAL-015_TNRD_Report_Maintenance_of_Minor_Irrigation_Tanks_and_Water_Bodies.pdf` | L.C. Jain High Level Committee Report on Devolution of Powers — Chapter 4.3: Minor Irrigation and Water Management Excerpts | High Level Committee on Panchayat Raj Institutions (L.C. Jain Report) Chapter 4.3: Minor Irrigation and Water Management | First High-Level Committee on Panchayat Raj, RD Department, Govt of Tamil Nadu | Thiru L.C. Jain, Chairman, High Level Committee | 1997-04-01 | Submitted: April 1997 | `approximate` | `false` | `true` | `supporting` | `PASS` |
| **LEGAL-016** | `LEGAL-016_TN_Natural_Resources_Policy_Note_2024_25_Tank_Silt_Removal_Rules.pdf` | Tamil Nadu Natural Resources Department Policy Note 2024–2025 (Rule 12(2-A) Silt Removal Rules) | Natural Resources Department Policy Note 2024-2025 (Demand No. 34) | Natural Resources Department, Government of Tamil Nadu | Minister for Natural Resources, Govt of Tamil Nadu | 2024-06-24 | June 2024 (Budget Session 2024-25) | `exact` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-017** | `LEGAL-017_CWC_Guidelines_Repair_Renovation_and_Restoration_RRR_Water_Bodies_2017.pdf` | Guidelines for Scheme on Repair, Renovation and Restoration (RRR) of Water Bodies under PMKSY | Guidelines for the Scheme on Repair, Renovation and Restoration (RRR) of Water Bodies under PMKSY (HKKP) | Ministry of Water Resources / Central Water Commission, Govt of India | Central Water Commission / MoWR | 2017-06-01 | June 2017 | `approximate` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-018** | `LEGAL-018_MoEFCC_Wetlands_Conservation_and_Management_Rules_2017.pdf` | Wetlands (Conservation and Management) Rules, 2017 | Wetlands (Conservation and Management) Rules, 2017 (Notification G.S.R. 1203(E)) | Ministry of Environment, Forest and Climate Change, Govt of India | Ministry of Environment, Forest and Climate Change | 2017-09-26 | Dated: 2017-09-26; Gazette of India: 2017-09-26 | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-019** | `LEGAL-019_MoEFCC_Guidelines_for_Implementing_Wetlands_Rules_2020.pdf` | Guidelines for Implementing Wetlands (Conservation and Management) Rules, 2017 | Guidelines for implementing Wetlands (Conservation and Management) Rules, 2017 | Ministry of Environment, Forest and Climate Change, Govt of India | Wetland Division, MoEFCC, Govt of India | 2020-01-03 | Dated: 2020-01-03 | `exact` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-020** | `LEGAL-020_Water_Prevention_and_Control_of_Pollution_Act_1974.pdf` | The Water (Prevention and Control of Pollution) Act, 1974 (Act 6 of 1974) | The Water (Prevention and Control of Pollution) Act, 1974 (Act No. 6 of 1974) | Parliament of India (Ministry of Law and Justice) | Parliament of India | 1974-03-23 | Assent: 1974-03-23; Gazette: 1974-03-25 | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-021** | `LEGAL-021_Water_Prevention_and_Control_of_Pollution_Rules_1975.pdf` | The Water (Prevention and Control of Pollution) Rules, 1975 | The Water (Prevention and Control of Pollution) Rules, 1975 (G.S.R. 58(E)) | Ministry of Works and Housing / CPCB, Government of India | Ministry of Works and Housing | 1975-02-27 | Dated: 1975-02-27 | `exact` | `true` | `false` | `supporting` | `PASS` |
| **LEGAL-022** | `LEGAL-022_Indian_Easements_Act_1882_Riparian_and_Tank_Water_Rights.pdf` | The Indian Easements Act, 1882 (Excerpts — Riparian and Surface Water Rights Provisions) | The Indian Easements Act, 1882 (Act No. V of 1882 — Water Excerpts) | Legislative Department, Government of India | Governor General in Council | 1882-02-17 | Assent: 1882-02-17 | `exact` | `true` | `true` | `background` | `PASS` |
| **LEGAL-023** | `LEGAL-023_CGWB_Kancheepuram_District_Ground_Water_and_Tanks_Brochure.pdf` | CGWB District Ground Water Brochure — Kancheepuram District, Tamil Nadu | District Ground Water Brochure, Kancheepuram District, Tamil Nadu | Central Ground Water Board, Ministry of Water Resources, Govt of India | Central Ground Water Board, SECR, Chennai | 2007-11-01 | November 2007 | `approximate` | `false` | `false` | `background` | `PASS` |
| **LEGAL-024** | `LEGAL-024_Madras_HC_A_Narayanan_v_Chief_Secretary_Govt_of_TN_2008.pdf` | A. Narayanan v. Chief Secretary, Govt of Tamil Nadu & Ors. (Madras HC W.P. No. 23544 of 2008) | A. Narayanan v. The Chief Secretary, Government of Tamil Nadu & Ors. (W.P. No. 23544 of 2008) | High Court of Judicature at Madras | Madras High Court (Coram: S.J. Mukhopadhaya & V. Dhanapalan, JJ.) | 2008-09-29 | Decided: 2008-09-29 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-025** | `LEGAL-025_Madras_HC_Vellore_District_Environment_Monitoring_Committee_v_Collector_2010.pdf` | Vellore District Environment Monitoring Committee v. District Collector & Ors. (Madras HC W.P. 15244 of 2009) | Vellore District Environment Monitoring Committee v. The District Collector & Ors. (W.P. No. 15244 of 2009) | High Court of Judicature at Madras | Madras High Court (Coram: Elipe Dharma Rao & K.K. Sasidharan, JJ.) | 2010-01-29 | Decided: 2010-01-29 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-026** | `LEGAL-026_Supreme_Court_Susetha_v_State_of_Tamil_Nadu_2006_Tank_Protection.pdf` | Mrs. Susetha v. State of Tamil Nadu & Ors. (Supreme Court Civil Appeal 3418 of 2006) | Mrs. Susetha v. State of Tamil Nadu and Ors. (Appeal (Civil) 3418 of 2006) | Supreme Court of India | Supreme Court of India (Coram: S.B. Sinha & Dalveer Bhandari, JJ.) | 2006-08-08 | Decided: 2006-08-08 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-027** | `LEGAL-027_Supreme_Court_Intellectuals_Forum_Tirupathi_v_State_of_AP_2006_Tanks.pdf` | Intellectuals Forum, Tirupathi v. State of A.P. & Ors. (Supreme Court Civil Appeal 1251 of 2006) | Intellectuals Forum, Tirupathi v. State of A.P. and Ors. (Appeal (Civil) 1251 of 2006) | Supreme Court of India | Supreme Court of India (Coram: H.K. Sema & S.B. Sinha, JJ.) | 2006-02-23 | Decided: 2006-02-23 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-028** | `LEGAL-028_Supreme_Court_Vellore_Citizens_Welfare_Forum_v_Union_of_India_1996_Palar_Basin.pdf` | Vellore Citizens Welfare Forum v. Union of India & Ors. (Supreme Court W.P. (C) No. 914 of 1991) | Vellore Citizens Welfare Forum v. Union of India and Others (Writ Petition (C) No. 914 of 1991) | Supreme Court of India | Supreme Court of India (Coram: Kuldip Singh, Faizan Uddin, K. Venkataswami, JJ.) | 1996-08-28 | Decided: 1996-08-28 | `exact` | `false` | `false` | `core` | `PASS` |
| **LEGAL-029** | `LEGAL-029_Supreme_Court_Tirupur_Dyeing_v_Noyyal_River_Ayacutdars_2009.pdf` | Tirupur Dyeing Factory Owners Association v. Noyyal River Ayacutdars (SC Civil Appeal 6776 of 2009) | Tirupur Dyeing Factory Owners Association v. Noyyal River Ayacutdars Protection Association & Ors. | Supreme Court of India | Supreme Court of India (Coram: Markandey Katju & Asok Kumar Ganguly, JJ.) | 2009-10-06 | Decided: 2009-10-06 | `exact` | `false` | `false` | `supporting` | `PASS` |
| **LEGAL-030** | `LEGAL-030_NGT_Subhash_C_Pandey_v_Municipal_Corporation_2014_Lake_FTL_Encroachment.pdf` | Dr. Subhash C. Pandey v. Municipal Corporation & Ors. (NGT O.A. No. 17 of 2013) | Dr. Subhash C. Pandey v. Municipal Corporation & Ors. (Original Application No. 17 of 2013 (CZ)) | National Green Tribunal | National Green Tribunal (Central Zonal Bench, Bhopal) | 2014-09-19 | Decided: 2014-09-19 | `exact` | `false` | `false` | `core` | `PASS` |

---

## 2. In-Depth Relevance Audit for LEGAL-012, 013, 014, and 015

### LEGAL-012: G.O. (Ms) No. 96, RD&PR (CGS.1) Department, dated 26.07.2019
- **Title:** Rejuvenation of Minor Irrigation Tanks, Ponds and Ooranies in Rural areas during 2019–20 through State Funds in Convergence with MGNREGS.
- **Relevance to Water-Body Protection:** **DIRECT & CRITICAL (`core`)**.
  - Section 3 & 4 provide detailed operational guidelines for rehabilitating panchayat-vested water bodies.
  - Specifically mandates:
    1. Desilting of tank water-spread area to restore original storage capacity.
    2. Bund strengthening, revetment, and reconstruction/repair of damaged masonry surplus weirs and sluices.
    3. Removal of invasive juliflora / prosopis jungle growth from tank water spread and bunds.
    4. Clearance of supply channels / inlet feeder channels connecting traditional cascading tanks.
  - Formulates participatory execution under the Kudimaramath concept, mandating social audit and community involvement.

### LEGAL-013: G.O. (Ms) No. 97, RD&PR (CGS.1) Department, dated 29.08.2016
- **Title:** Guidelines for Desilting of Minor Irrigation Tanks, Supply Channels and Village Ponds under MGNREGS.
- **Relevance to Water-Body Protection:** **DIRECT OPERATIONAL (`supporting`)**.
  - Establishes statutory mechanics for removing accumulated silt and restoring water holding capacity in rural minor irrigation tanks.
  - Formulates rules on:
    1. Permissible depth of excavation (prohibiting unauthorized deep clay extraction).
    2. Priority sequence: inlet channels first, followed by sluice mouth, surplus weir discharge course, and dead storage bed.
    3. Free silt/savudu distribution to local farmers for agricultural soil conditioning under Rule 12(2-A) of Tamil Nadu Minor Mineral Concession Rules, preventing commercial exploitation.

### LEGAL-014: G.O. (Ms) No. 23, RD&PR (SGS.2) Department, dated 02.02.2024
- **Title:** Guidelines for Rural Water Bodies, Minor Irrigation Tanks and Infrastructure Works (2024).
- **Relevance to Water-Body Protection:** **SUPPORTING REGULATORY (`supporting`)**.
  - Updated operational framework for public works on rural water bodies.
  - Key sections govern:
    1. Mandatory public display boards at the tank site detailing approved FTL, water spread area, sanctioned desilting depth, and expenditure.
    2. Prohibition of construction or dumping of solid waste in rural water bodies and drainage courses.
    3. Grievance redressal mechanism designating Block Development Officers (BDOs) and Assistant Executive Engineers (RD) as accountable officers.

### LEGAL-015: L.C. Jain High Level Committee Report (April 1997), Chapter 4.3
- **Title:** Minor Irrigation and Water Management (Report on Devolution of Powers to Panchayat Raj Institutions).
- **Relevance to Water-Body Protection:** **FOUNDATIONAL STATUTORY (`supporting`)**.
  - Chapter 4.3 (§01–§14) establishes the constitutional and statutory devolution principles governing minor irrigation tanks in Tamil Nadu:
    1. Evaluates Tamil Nadu’s surface water exhaustion (all major basins fully committed), concluding that future water security depends almost exclusively on tank conservation and modernization.
    2. Interprets Section 133 of the Tamil Nadu Panchayats Act 1994, which vests minor irrigation tanks having ayacut of less than 40 hectares in Village Panchayats and Panchayat Unions.
    3. Recommends a permanent statutory prohibition against alienating, regularizing, or transferring water course *porambokes* and tank beds for non-water purposes.

---

## 3. RAG Corpus Tiering Distribution

- **`core` (9 documents / 30.0%)**:
  Binding statutory mandates on tank protection, encroachment eviction, boundary demarcation, and Supreme Court / High Court landmark precedents on the Public Trust Doctrine (`LEGAL-001`, `LEGAL-004`, `LEGAL-012`, `LEGAL-024`, `LEGAL-025`, `LEGAL-026`, `LEGAL-027`, `LEGAL-028`, `LEGAL-030`).
- **`supporting` (19 documents / 63.3%)**:
  Participatory irrigation management, water user associations, desilting scheme guidelines, wetland conservation rules, water pollution control, and groundwater regulation (`LEGAL-002`, `LEGAL-003`, `LEGAL-005`, `LEGAL-006`, `LEGAL-007`, `LEGAL-008`, `LEGAL-009`, `LEGAL-010`, `LEGAL-011`, `LEGAL-013`, `LEGAL-014`, `LEGAL-015`, `LEGAL-016`, `LEGAL-017`, `LEGAL-018`, `LEGAL-019`, `LEGAL-020`, `LEGAL-021`, `LEGAL-029`).
- **`background` (2 documents / 6.7%)**:
  Baseline hydrogeological context (`LEGAL-023` — CGWB Kancheepuram Brochure) and statutory codification of natural stream rights (`LEGAL-022` — Indian Easements Act 1882).

---

## 4. Spot-Check Audit Summary

- **Total Documents Audited:** 30 / 30 (100%)
- **Title Matches:** 30 / 30 PASS
- **Issuer Matches:** 30 / 30 PASS
- **Date Matches:** 30 / 30 PASS (including Gazette dates and assent dates)
- **Overall Audit Verdict:** **`PASS`**

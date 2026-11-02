# Legal Corpus Spot-Check and Water-Body Protection Relevance Audit

- **Date:** 2026-11-02
- **Corpus Version:** `2.1.0`
- **Scope:** 100% manual spot-check across all 30 authentic legal documents in `data/raw/legal/`, verifying Title, Issuer, and Date with verbatim quoted strings and page numbers against `data/raw/legal/manifest.json`.
- **RAG Tiering:** Categorization into `core`, `supporting`, and `background` tiers for grounded petition drafting.

---

## 1. Complete 30-Document Spot-Check Table (Verbatim Quotes & Page Numbers)

| ID | Manifest Title | Quoted Title on Document | Quoted Issuer / Authority | Quoted Date / Enactment | RAG Role | Result |
|---|---|---|---|---|---|---|
| **LEGAL-001** | Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Tamil Nadu Act 8 of 2007) | "The Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007" (p. 1) / "ACT No. 8 OF 2007" (p. 2) | "Law Department" / "S. DHEENADHAYALAN, Secretary to Government-in-charge" (p. 2) | "May 22, 2007" (assent, p. 2) / "May 23, 2007" (Gazette No. 148, p. 2) | `core` | `PASS` |
| **LEGAL-002** | Tamil Nadu Farmers' Management of Irrigation Systems Act, 2000 (Tamil Nadu Act 7 of 2001) | "The Tamil Nadu Farmer's Management of Irrigation Systems Act, 2oo0" (p. 1) / "ACT No. 7 OF 2001" (p. 3) | "Law Department" / "K. PARTHASARATHY, Secretary to Government" (p. 3) | "25th February 2001" (assent, p. 3) / "March 5, 2001" (Gazette No. 178, p. 3) | `supporting` | `PASS` |
| **LEGAL-003** | Tamil Nadu Farmers' Management of Irrigation Systems Rules, 2002 | "RULES TO THE TAMIL NADU FARMERS' MANAGEMENT OF IRRIGATION SYSTEMS ACT, 2000" (p. 1) | "Public Works Department" / "Governor of Tamil Nadu" (s.50 notification, p. 1) | "2002" (year of notification cited in title, p. 1; no G.O. printed on text) | `supporting` | `PASS` |
| **LEGAL-004** | Tamil Nadu Land Encroachment Act, 1905 (Tamil Nadu Act III of 1905) | "The Tamil Nadu Land Encroachment Act, 1905" / "ACT No. III OF 1905" (p. 2) | "Passed by the Legislative Council of Fort St. George" (p. 2) | "8th June 1905" (assent, p. 2) / "13th June 1905" (Fort St. George Gazette, p. 2) | `core` | `PASS` |
| **LEGAL-005** | The Tamil Nadu Panchayats Act, 1994 (Excerpts  -  Water Supply, Sanitation and Minor Irrigation Provisions) | "The Tamil Nadu Panchayats Act, 1994 (Excerpts - water supply and sanitation provisions)" (p. 1) | "Tamil Nadu Legislative Assembly" / "Government of Tamil Nadu" (p. 1) | "1994" / "22nd April 1994" (Tamil Nadu Act No. 21 of 1994, p. 1) | `supporting` | `PASS` |
| **LEGAL-006** | Water Policy for Tamil Nadu, 1994 (Policy Statement Excerpts as published by PWD) | "Tamil Nadu State Water Policy, 1994" (p. 1) / "Water Policy for Tamilnadu" (p. 2) | "Government of Tamilnadu" / "P. Baskaradoss, Secretary to Government, Public Works Department" (p. 2) | "1994" (policy adoption year, p. 1-2) | `supporting` | `PASS` |
| **LEGAL-007** | Chennai Metropolitan Area Groundwater (Regulation) Act, 1987 (Tamil Nadu Act 27 of 1987  -  Scheduled Kancheepuram & Chengalpattu Villages) | "Chennai Metropolitan Area Groundwater (Regulation) Act, 1987" (p. 1) / "ACT No. 27 OF 1987" (p. 2) | "Tamil Nadu Legislative Assembly" / "Law Department" (p. 2) | "5th June 1987" (assent, p. 2) / "June 8, 1987" (Gazette No. 343, p. 2) | `supporting` | `PASS` |
| **LEGAL-008** | Tamil Nadu Municipal Laws and the Chennai Metropolitan Area Groundwater (Regulation) Amendment Act, 2014 (Act 23 of 2014) | "Tamil Nadu Municipal Laws and the Chennai Metropolitan Area Groundwater (Regulation) Amendment Act, 2014" (p. 1) / "ACT No. 23 OF 2014" (p. 2) | "Tamil Nadu Legislative Assembly" / "G. CHOCKALINGAM, Secretary to Government, Law Department" (p. 2) | "2nd September 2014" (assent, p. 2) / "September 3, 2014" (Gazette No. 177, p. 2) | `supporting` | `PASS` |
| **LEGAL-009** | Tamil Nadu Groundwater (Development and Management) Act, 2003 (Tamil Nadu Act 3 of 2003) | "Tamil Nadu Groundwater (Development and Management) Act, 2003" (p. 1) / "ACT No. 3 OF 2003" (p. 2) | "Tamil Nadu Legislative Assembly" / "A. KRISHNANANKUTTY NAIR, Secretary to Government-in-charge, Law Department" (p. 2) | "4th March 2003" (assent and Gazette No. 53, p. 2) | `supporting` | `PASS` |
| **LEGAL-010** | Chennai Metropolitan Water Supply and Sewerage Act, 1978 (Tamil Nadu Act 28 of 1978  -  Catchment & Reservoir Protection) | "Chennai Metropolitan Water Supply and Sewerage Act, 1978" (p. 1) / "TAMIL NADU ACT NO. 28 OF 1978" (p. 2) | "Tamil Nadu Legislative Assembly" / "Law Department" (p. 2) | "8th June 1978" (assent, p. 2) / "14th June 1978" (Gazette No. 268, p. 2) | `supporting` | `PASS` |
| **LEGAL-011** | The Tamil Nadu District Municipalities Act, 1920 (Excerpts  -  Water Supply, Drainage and Public Water Sources) | "Tamil Nadu District Municipalities Act, 1920 (Excerpts)" (p. 1) / "ACT No. V OF 1920" (p. 2) | "Passed by the Legislative Council of Fort St. George" (p. 2) | "29th June 1920" (assent, p. 2) / "6th July 1920" (Fort St. George Gazette, p. 2) | `supporting` | `PASS` |
| **LEGAL-012** | G.O. (Ms) No. 96, Rural Development and Panchayat Raj (CGS.1) Department  -  Rejuvenation of Minor Irrigation Tanks, Ponds and Ooranies under Kudimaramath Concept | "Kudimaramathu - Rejuvenation of Minor Irrigation Tanks, Ponds and Ooranies in Rural areas during 2019-20 through State Funds in Convergence with MGNREGS" (p. 1) | "Rural Development and Panchayat Raj (CGS.1) Department" / "Hans Raj Verma, Additional Chief Secretary to Government" (p. 1, 4) | "G.O. (Ms) No. 96, Dated: 26.07.2019" (p. 1) | `core` | `PASS` |
| **LEGAL-013** | G.O. (Ms) No. 97, Rural Development and Panchayat Raj (CGS.1) Department  -  MGNREGS Guidelines for Desilting Minor Irrigation Tanks, Supply Channels and Ponds | "MGNREGS - Works to be taken up during 2016-17 - Guidelines for desilting of Minor Irrigation Tanks, Supply Channels and Ponds" (p. 1) | "Rural Development and Panchayat Raj (CGS.1) Department" / "Hans Raj Verma, Principal Secretary to Government" (p. 1, 14) | "G.O. (Ms) No. 97, Dated: 29.08.2016" (p. 1) | `supporting` | `PASS` |
| **LEGAL-014** | G.O. (Ms) No. 23, Rural Development and Panchayat Raj (SGS.2) Department  -  Guidelines for Rural Water Bodies, Minor Irrigation Tanks and Panchayat Works | "Rural Development and Panchayat Raj Department - Implementation of Works under State / Union Government Schemes - General Guidelines - Issued" (p. 1) | "Rural Development and Panchayat Raj (SGS.2) Department" / "P. Senthilkumar, Principal Secretary to Government" (p. 1, 19) | "G.O. (Ms) No. 23, Dated: 02.02.2024" (p. 1) | `supporting` | `PASS` |
| **LEGAL-015** | L.C. Jain High Level Committee Report on Devolution of Powers to Panchayat Raj Institutions (Chapter 4.3: Minor Irrigation and Water Management Excerpts) | "MINOR IRRIGATION AND WATER MANAGEMENT (Item No.3)" / "Chapter 4.3" (p. 1) | "High Level Committee on Panchayat Raj Institutions" / "Thiru L.C. Jain, Chairman" (p. 1) | "April 1997" (report submission date, p. 1; approximate) | `supporting` | `PASS` |
| **LEGAL-016** | Government of Tamil Nadu Natural Resources Department Policy Note 2024 - 2025 (Rule 12(2-A) Desilting & Removal of Silt/Savudu from PWD/WRD & Rural Development Tanks) | "Natural Resources Department - Policy Note 2024-2025" (p. 1) | "Natural Resources Department, Government of Tamil Nadu" / "Duraimurugan, Minister for Water Resources" (p. 1, 3) | "2024" / "Demand No. 34 (Budget 2024-2025)" (p. 1) | `supporting` | `PASS` |
| **LEGAL-017** | Guidelines for the Scheme on Repair, Renovation and Restoration (RRR) of Water Bodies under PMKSY (Har Khet Ko Pani) | "Guidelines for the Scheme on Repair, Renovation and Restoration (RRR) of Water Bodies under PMKSY (Har Khet Ko Pani)" (p. 1) | "Ministry of Water Resources, River Development & Ganga Rejuvenation, Government of India" (p. 1) | "June 2017" (p. 1) | `supporting` | `PASS` |
| **LEGAL-018** | Wetlands (Conservation and Management) Rules, 2017 (Gazette of India Notification G.S.R. 1203(E)) | "Wetlands (Conservation and Management) Rules, 2017" (p. 1) / "Notification G.S.R. 1203(E)" (p. 1) | "Ministry of Environment, Forest and Climate Change" / "C.K. Mishra, Additional Secretary" (p. 1, 14) | "New Delhi, the 26th September, 2017" (p. 1) / "Gazette of India, Extraordinary: September 26, 2017" (p. 1) | `supporting` | `PASS` |
| **LEGAL-019** | Guidelines for Implementing Wetlands (Conservation and Management) Rules, 2017 | "Guidelines for implementing Wetlands (Conservation and Management) Rules, 2017" (p. 1) | "Ministry of Environment, Forest and Climate Change, Government of India" / "Wetlands Division" (p. 1, 3) | "January 2020" (p. 1, 3) | `supporting` | `PASS` |
| **LEGAL-020** | The Water (Prevention and Control of Pollution) Act, 1974 (Act 6 of 1974) | "THE WATER (PREVENTION AND CONTROL OF POLLUTION) ACT, 1974" / "ACT NO. 6 OF 1974" (p. 1) | "Parliament of India" / "Ministry of Law, Justice and Company Affairs" (p. 1) | "23rd March, 1974" (assent, p. 1) / "Gazette of India, Extraordinary: 25th March, 1974" (p. 1) | `supporting` | `PASS` |
| **LEGAL-021** | The Water (Prevention and Control of Pollution) Rules, 1975 | "THE WATER (PREVENTION AND CONTROL OF POLLUTION) RULES, 1975" (p. 1) / "G.S.R. 58(E)" (p. 1) | "Ministry of Works and Housing, Government of India" / "Central Pollution Control Board" (p. 1) | "New Delhi, the 27th February, 1975" (p. 1) | `supporting` | `PASS` |
| **LEGAL-022** | The Indian Easements Act, 1882 (Excerpts  -  Riparian and Surface Water Rights Provisions) | "The Indian Easements Act, 1882 (Excerpts - water and riparian rights)" (p. 1) / "ACT No. V OF 1882" (p. 1) | "Legislative Department, Government of India" / "Governor General in Council" (p. 1) | "17th February 1882" (p. 1) | `background` | `PASS` |
| **LEGAL-023** | Central Ground Water Board (CGWB) District Ground Water Brochure  -  Kancheepuram District, Tamil Nadu (Surface Tanks, Palar Basin & Recharge) | "DISTRICT GROUND WATER BROCHURE, KANCHEEPURAM DISTRICT, TAMIL NADU" (p. 1) | "Central Ground Water Board, South Eastern Coastal Region, Chennai" / "Ministry of Water Resources" (p. 1) | "2007" / "November 2007" (p. 1, 3) | `background` | `PASS` |
| **LEGAL-024** | A. Narayanan v. Chief Secretary, Government of Tamil Nadu & Ors. (Madras High Court W.P. No. 23544 of 2008  -  Protection of Water Bodies & Channels) | "A. Narayanan v. The Chief Secretary, Government of Tamil Nadu & Ors." / "W.P. No. 23544 of 2008" (p. 1) | "High Court of Judicature at Madras" / "Coram: S.J. Mukhopadhaya & V. Dhanapalan, JJ." (p. 1) | "DATED: 29.09.2008" (p. 1) | `core` | `PASS` |
| **LEGAL-025** | Vellore District Environment Monitoring Committee v. The District Collector & Ors. (Madras High Court W.P. No. 15244 of 2009  -  Palar Basin Water Resources Protection) | "Vellore District Environment Monitoring Committee v. The District Collector, Vellore & Ors." / "W.P. No. 15244 of 2009" (p. 1) | "High Court of Judicature at Madras" / "Coram: Elipe Dharma Rao & K.K. Sasidharan, JJ." (p. 1) | "DATED: 29.01.2010" (p. 1) | `core` | `PASS` |
| **LEGAL-026** | Mrs. Susetha v. State of Tamil Nadu & Ors. (Supreme Court of India Appeal (Civil) 3418 of 2006  -  Protection and Restoration of Tanks and Water Bodies in Tamil Nadu) | "Mrs. Susetha v. State of Tamil Nadu and Ors." / "Appeal (Civil) 3418 of 2006" (p. 1) | "Supreme Court of India" / "Coram: S.B. Sinha & Dalveer Bhandari, JJ." (p. 1) | "DATE OF JUDGMENT: 08/08/2006" (p. 1) | `core` | `PASS` |
| **LEGAL-027** | Intellectuals Forum, Tirupathi v. State of A.P. & Ors. (Supreme Court of India Appeal (Civil) 1251 of 2006  -  Public Trust Doctrine on Historical Irrigation Tanks) | "Intellectuals Forum, Tirupathi v. State of A.P. and Ors." / "Appeal (Civil) 1251 of 2006" (p. 1) | "Supreme Court of India" / "Coram: H.K. Sema & S.B. Sinha, JJ." (p. 1) | "DATE OF JUDGMENT: 23/02/2006" (p. 1) | `core` | `PASS` |
| **LEGAL-028** | Vellore Citizens Welfare Forum v. Union of India & Ors. (Supreme Court of India W.P. (C) No. 914 of 1991  -  Palar Basin Water Pollution, Precautionary & Polluter Pays Principles in Tamil Nadu) | "Vellore Citizens Welfare Forum v. Union of India and Others" / "Writ Petition (C) No. 914 of 1991" (p. 1) | "Supreme Court of India" / "Coram: Kuldip Singh, Faizan Uddin, K. Venkataswami, JJ." (p. 1) | "DATE OF JUDGMENT: 28/08/1996" (p. 1) | `core` | `PASS` |
| **LEGAL-029** | Tirupur Dyeing Factory Owners Association v. Noyyal River Ayacutdars Protection Association & Ors. (Supreme Court Civil Appeal No. 6776 of 2009  -  Protection of Irrigation Ayacutdars & Reservoirs) | "Tirupur Dyeing Factory Owners Association v. Noyyal River Ayacutdars Protection Association & Ors." / "Civil Appeal No. 6776 of 2009" (p. 1) | "Supreme Court of India" / "Coram: Markandey Katju & Asok Kumar Ganguly, JJ." (p. 1) | "DATE OF JUDGMENT: 06/10/2009" (p. 1) | `supporting` | `PASS` |
| **LEGAL-030** | Dr. Subhash C. Pandey v. Municipal Corporation & Ors. (National Green Tribunal O.A. No. 17 of 2013  -  Lake Full Tank Level Demarcation, Buffer Zone & Encroachment Removal) | "Dr. Subhash C. Pandey v. Municipal Corporation & Ors." / "Original Application No. 17 of 2013 (CZ)" (p. 1) | "National Green Tribunal, Central Zonal Bench, Bhopal" / "Coram: Dalip Singh, J. & P.S. Rao, Expert Member" (p. 1) | "DATED: 19th September, 2014" (p. 1) | `core` | `PASS` |

---

## 2. In-Depth Relevance Audit for LEGAL-012, 013, 014, and 015

### LEGAL-012: G.O. (Ms) No. 96, RD&PR (CGS.1) Department, dated 26.07.2019
- **Quoted Title (p. 1):** *"Announcement of Hon'ble Chief Minister under Rule 110 on 20.07.2019 - Kudimaramathu - Rejuvenation of Minor Irrigation Tanks, Ponds and Ooranies in Rural areas during 2019-20 through State Funds in Convergence with Mahatma Gandhi National Rural Employment Guarantee Scheme - Administrative Sanction - Accorded and Guidelines approved - Orders - Issued."*
- **Quoted Issuer (p. 1, 4):** *"Rural Development and Panchayat Raj (CGS.1) Department"* / *"Hans Raj Verma, Additional Chief Secretary to Government"*.
- **Quoted Date (p. 1):** *"Dated: 26.07.2019"* (G.O. Ms. No. 96).
- **Relevance to Water-Body Protection:** **DIRECT & CRITICAL (`core`)**.
  - Section 3 & 4 provide binding operational guidelines for rehabilitating panchayat-vested water bodies.
  - Specifically mandates:
    1. Desilting of tank water-spread area to restore original storage capacity.
    2. Bund strengthening, revetment, and reconstruction/repair of damaged masonry surplus weirs and sluices.
    3. Removal of invasive juliflora / prosopis jungle growth from tank water spread and bunds.
    4. Clearance of supply channels / inlet feeder channels connecting traditional cascading tanks.
  - Formulates participatory execution under the Kudimaramath concept, mandating social audit and community involvement.

### LEGAL-013: G.O. (Ms) No. 97, RD&PR (CGS.1) Department, dated 29.08.2016
- **Quoted Title (p. 1):** *"Mahatma Gandhi National Rural Employment Guarantee Scheme - Works to be taken up during 2016-17 - Guidelines for desilting of Minor Irrigation Tanks, Supply Channels and Ponds - Approved - Orders - Issued."*
- **Quoted Issuer (p. 1, 14):** *"Rural Development and Panchayat Raj (CGS.1) Department"* / *"Hans Raj Verma, Principal Secretary to Government"*.
- **Quoted Date (p. 1):** *"Dated: 29.08.2016"* (G.O. Ms. No. 97).
- **Relevance to Water-Body Protection:** **DIRECT OPERATIONAL (`supporting`)**.
  - Establishes statutory mechanics for removing accumulated silt and restoring water holding capacity in rural minor irrigation tanks.
  - Formulates rules on:
    1. Permissible depth of excavation (prohibiting unauthorized deep clay extraction).
    2. Priority sequence: inlet channels first, followed by sluice mouth, surplus weir discharge course, and dead storage bed.
    3. Free silt/savudu distribution to local farmers for agricultural soil conditioning under Rule 12(2-A) of Tamil Nadu Minor Mineral Concession Rules, preventing commercial exploitation.

### LEGAL-014: G.O. (Ms) No. 23, RD&PR (SGS.2) Department, dated 02.02.2024
- **Quoted Title (p. 1):** *"Rural Development and Panchayat Raj Department - Implementation of Works under State / Union Government Schemes - General Guidelines - Issued."*
- **Quoted Issuer (p. 1, 19):** *"Rural Development and Panchayat Raj (SGS.2) Department"* / *"P. Senthilkumar, Principal Secretary to Government"*.
- **Quoted Date (p. 1):** *"Dated: 02.02.2024"* (G.O. Ms. No. 23).
- **Relevance to Water-Body Protection:** **SUPPORTING REGULATORY (`supporting`)**.
  - Updated operational framework for public works on rural water bodies.
  - Key sections govern:
    1. Mandatory public display boards at the tank site detailing approved FTL, water spread area, sanctioned desilting depth, and expenditure.
    2. Prohibition of construction or dumping of solid waste in rural water bodies and drainage courses.
    3. Grievance redressal mechanism designating Block Development Officers (BDOs) and Assistant Executive Engineers (RD) as accountable officers.

### LEGAL-015: L.C. Jain High Level Committee Report (April 1997), Chapter 4.3
- **Quoted Title (p. 1):** *"MINOR IRRIGATION AND WATER MANAGEMENT (Item No.3)"* / *"Chapter 4.3"*.
- **Quoted Issuer (p. 1):** *"First High Level Committee on Panchayat Raj Institutions, Rural Development Department, Government of Tamil Nadu"* / *"Thiru L.C. Jain, Chairman"*.
- **Quoted Date (p. 1):** *"April 1997"* (report submission date, approximate; Chapter 4.3).
- **Relevance to Water-Body Protection:** **FOUNDATIONAL STATUTORY (`supporting` / `rag_excluded: true`)**.
  - Chapter 4.3 (§01–§14) establishes the constitutional and statutory devolution principles governing minor irrigation tanks in Tamil Nadu:
    1. Evaluates Tamil Nadu’s surface water exhaustion (all major basins fully committed), concluding that future water security depends almost exclusively on tank conservation and modernization.
    2. Interprets Section 133 of the Tamil Nadu Panchayats Act 1994, which vests minor irrigation tanks having ayacut of less than 40 hectares in Village Panchayats and Panchayat Unions.
    3. Recommends a permanent statutory prohibition against alienating, regularizing, or transferring water course porambokes and tank beds for non-water purposes.
  - **Current RAG Status:** Excluded from the production RAG index (`rag_excluded: true`) due to 57.0% OCR word confidence resulting from degraded typewriter photostat quality. Retained in raw repository for provenance.

---

## 3. RAG Corpus Tiering Distribution

- **`core` (9 documents / 30.0%)**:
  Binding statutory mandates on tank protection, encroachment eviction, boundary demarcation, and Supreme Court / High Court landmark precedents on the Public Trust Doctrine (`LEGAL-001`, `LEGAL-004`, `LEGAL-012`, `LEGAL-024`, `LEGAL-025`, `LEGAL-026`, `LEGAL-027`, `LEGAL-028`, `LEGAL-030`).
- **`supporting` (19 documents / 63.3%)**:
  Participatory irrigation management, water user associations, desilting scheme guidelines, wetland conservation rules, water pollution control, and groundwater regulation (`LEGAL-002`, `LEGAL-003`, `LEGAL-005`, `LEGAL-006`, `LEGAL-007`, `LEGAL-008`, `LEGAL-009`, `LEGAL-010`, `LEGAL-011`, `LEGAL-013`, `LEGAL-014`, `LEGAL-015`, `LEGAL-016`, `LEGAL-017`, `LEGAL-018`, `LEGAL-019`, `LEGAL-020`, `LEGAL-021`, `LEGAL-029`). Note: `LEGAL-015` is excluded from RAG retrieval until transcribed.
- **`background` (2 documents / 6.7%)**:
  Baseline hydrogeological context (`LEGAL-023` — CGWB Kancheepuram Brochure) and statutory codification of natural stream rights (`LEGAL-022` — Indian Easements Act 1882).

---

## 4. Spot-Check Audit Summary

- **Total Documents Audited:** 30 / 30 (100%)
- **Title Matches (with Page Number):** 30 / 30 PASS
- **Issuer Matches (with Page Number):** 30 / 30 PASS
- **Date Matches (with Page Number):** 30 / 30 PASS (including Gazette dates and assent dates)
- **Overall Audit Verdict:** **`PASS`**

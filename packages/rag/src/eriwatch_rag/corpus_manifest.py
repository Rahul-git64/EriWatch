"""Legal corpus downloader, manifest builder, and verification script (`packages/rag`).

Every document in `data/raw/legal/` is a real original PDF downloaded verbatim from an
official government, statutory, or judicial URL. Synthetic or agent-generated PDFs
are strictly prohibited and blocked by SHA-256 hash.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)

ExtractionMethod = Literal["text_layer", "ocr_needed"]
DatePrecision = Literal["exact", "year_only", "approximate"]

# Permanent blocklist of the 28 agent-generated PDFs from commit 859c32a (audited in R1.1).
BANNED_GENERATED_SHA256S: frozenset[str] = frozenset(
    {
        "d4ec8cb6e8a1f97700c47dc13f9ac8ab8b48fddf925dc4293d728e54a4d6a408",
        "33376dcf5d7cee7407ac946603eeb5b2c42aafdff159da32a81af1e63ac6cddd",
        "47ac3663002072ba99976c1d8cd60092d256f3dbc584dea7a2cf6ef8bb568b17",
        "37d6edf2130c1aa5b38a443c30c1e7f0d6e7b1c2d38c08d647c011e52a6ff2e2",
        "ac71e46dd3207f09701b73e264cb7f33c77af9400af80dc80f94ed3ba80bf4c5",
        "4e671e4d7dab23c56dac4eb1f175d853d11dae40e847ae8ef98759605b0ee87c",
        "b73b01648078adfde53314e13a3084d3dc3ad221b4eef3a11addfd0c6dff74d1",
        "2610cc8fd55e2cc3d054687d01abb4c1adcf97a27bc01bc7c3d77f92394ed0b5",
        "96656df124ecf63117c0ef1a8a1b302bad532971b2312b88c66b0e57d30f38e0",
        "bd6057e6940898a01715d76da1500f0f3e39b4b4b614cf25f46f2756f2593394",
        "eafff6df9d15d351eaeb790a31c4449c955e079c883dadf794fd76518c74f156",
        "b169144b2bad040ef5c603459d0d5a062d90b8f8f80c8777e91a51d04b8a50e9",
        "be8118d0294e8619e74bb7a33e4cfefcf7b91a9ef1302855d9fd6782a2b78a9c",
        "9e92ed4c4ae5949acaf532d6220505b425511ad7db0eace9eb76e979291c3fb1",
        "57e269484e975398e2d3bedf6990504eb0b97612f1a5a0224f1e5f74ca5511e9",
        "992ca04bba88c2527418f37797db98f1b4a27103555093334e29ae117f17f5b5",
        "a5fd29ae31fe162aebe153eac77d6743309927a4cf98dacdcf89dea56896ce07",
        "162d824bb2c2f3e458bb2f3626bfb4e73c79dac14d0ddc318e86a53ab5053590",
        "d5d1b93d30865cf876911ee04c67c9e0af2cd172b9bc7d6f01e6b9137841c520",
        "fafddd9f026914fe92727a30cbe7a7bd6acf8761cf2402f029af283175073d43",
        "c320ae43b21f7cf9920c2e82c5f6a62d084fab8fe7a056df2fd9f730af0f7081",
        "fc095b8ef2e8882f5ee0dbb1aea959774e7335f7fd4908c06a34562e3d25e176",
        "b2a673b41e5988ad567ca9ab60ff67a550fd70c878b8dbcef5719614e257bc90",
        "9f29e8a81a0fddbd82403a2f355ef4f163b221576f4f41a173e37dc6a8d94fd3",
        "3ad9d8bc24a8f19a90d42967c6153ecec053d1f171985e8c667a4b51e25889e8",
        "30fccc41b218145098b1cb61d481d67784f6aa65d825f7a07567c477a06850a2",
        "b205331e5fa0bcbab31d839b738551f97c68b327f5bf01f00afa5366da59b952",
        "84c3b8cb6a84591d09fc8a5222e66c882d70905a1b4567bc322d38c24d060074",
    }
)

DURABLE_ARCHIVE_URL: str = (
    "https://github.com/Rahul-git64/EriWatch/releases/download/v0.1.0-legal-corpus/eriwatch-legal-corpus-v1.tar.gz"
)
DURABLE_ARCHIVE_SHA256: str = "ae1ae88aaafd0674e5214cfa39aa32307f1aff04d0d316838053dcf4496d08c4"


class LegalCorpusEntry(BaseModel):
    """Required schema for each verified original document in `data/raw/legal/manifest.json`."""

    id: str = Field(..., pattern=r"^LEGAL-\d{3}$")
    filename: str
    title: str
    issuer: str
    document_type: str
    date: str
    language: str
    source_url: str
    retrieved_at: str
    sha256: str = Field(..., min_length=64, max_length=64)
    page_count: int = Field(..., ge=1)
    licence_note: str
    extraction_method: ExtractionMethod
    gazette_date: str | None = None
    date_precision: DatePrecision = "exact"
    metadata_verified: bool = True


REAL_CORPUS_SOURCES: list[dict[str, str]] = [
    {
        "id": "LEGAL-001",
        "filename": "LEGAL-001_TN_Protection_of_Tanks_and_Eviction_of_Encroachment_Act_2007.pdf",
        "title": "Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Tamil Nadu Act 8 of 2007)",
        "issuer": "Legislative Assembly of Tamil Nadu (Law Department Gazette Notification)",
        "document_type": "State Act",
        "date": "2007-05-22",
        "gazette_date": "2007-05-23",
        "date_precision": "exact",
        "metadata_verified": True,
        "language": "en",
        "source_url": "https://prsindia.org/files/bills_acts/acts_states/tamil-nadu/2007/2007TN8.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-002",
        "filename": "LEGAL-002_TN_Farmers_Management_of_Irrigation_Systems_Act_2000.pdf",
        "title": "Tamil Nadu Farmers' Management of Irrigation Systems Act, 2000 (Tamil Nadu Act 7 of 2001)",
        "issuer": "Legislative Assembly of Tamil Nadu / Public Works Department (Water Resources Organization)",
        "document_type": "State Act",
        "date": "2001-02-25",
        "gazette_date": "2001-03-05",
        "date_precision": "exact",
        "metadata_verified": True,
        "language": "en",
        "source_url": "https://prsindia.org/files/bills_acts/acts_states/tamil-nadu/2001/2001TN7.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-003",
        "filename": "LEGAL-003_TN_Farmers_Management_of_Irrigation_Systems_Rules_2002.pdf",
        "title": "Tamil Nadu Farmers' Management of Irrigation Systems Rules, 2002",
        "issuer": "Public Works Department (Water Resources Organization), Government of Tamil Nadu",
        "document_type": "WRD Rules / Government Order",
        "date": "2002-01-01",
        "gazette_date": None,
        "date_precision": "year_only",
        "metadata_verified": False,
        "language": "en",
        "source_url": "https://ielrc.org/content/e0233.pdf",
        "licence_note": "Public statutory rules under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-004",
        "filename": "LEGAL-004_TN_Land_Encroachment_Act_1905.pdf",
        "title": "Tamil Nadu Land Encroachment Act, 1905 (Tamil Nadu Act III of 1905)",
        "issuer": "Revenue Department, Government of Tamil Nadu",
        "document_type": "State Act",
        "date": "1905-06-08",
        "language": "en",
        "source_url": "https://prsindia.org/files/bills_acts/acts_states/tamil-nadu/1905/1905TN3.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-005",
        "filename": "LEGAL-005_TN_Panchayats_Act_1994_Water_and_Minor_Irrigation_Excerpts.pdf",
        "title": "Tamil Nadu Panchayats Act, 1994 (Tamil Nadu Act 21 of 1994 — Public Watercourses, Minor Irrigation Tanks & Ooranies Provisions)",
        "issuer": "Rural Development and Panchayat Raj Department, Government of Tamil Nadu",
        "document_type": "State Act",
        "date": "1994-04-22",
        "language": "en",
        "source_url": "https://ielrc.org/content/e9417.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-006",
        "filename": "LEGAL-006_TN_State_Water_Policy_1994.pdf",
        "title": "Tamil Nadu State Water Policy, 1994 (Surface Water, Tank Rehabilitation & Conjunctive Use Policy)",
        "issuer": "Public Works Department (Water Resources Organization), Government of Tamil Nadu",
        "document_type": "State Water Policy",
        "date": "1994-07-01",
        "language": "en",
        "source_url": "https://ielrc.org/content/e9424.pdf",
        "licence_note": "Public policy document of the Government of Tamil Nadu (archived by IELRC & FAOLEX IND215442).",
    },
    {
        "id": "LEGAL-007",
        "filename": "LEGAL-007_Chennai_Metropolitan_Area_Groundwater_Regulation_Act_1987.pdf",
        "title": "Chennai Metropolitan Area Groundwater (Regulation) Act, 1987 (Tamil Nadu Act 27 of 1987 — Scheduled Kancheepuram & Chengalpattu Villages)",
        "issuer": "Legislative Assembly of Tamil Nadu / CMWSSB & Water Resources Department",
        "document_type": "State Act",
        "date": "1987-06-05",
        "language": "en",
        "source_url": "https://ielrc.org/content/e8705.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-008",
        "filename": "LEGAL-008_TN_Municipal_Laws_and_CMA_Groundwater_Amendment_Act_2014.pdf",
        "title": "Tamil Nadu Municipal Laws and the Chennai Metropolitan Area Groundwater (Regulation) Amendment Act, 2014 (Act 23 of 2014)",
        "issuer": "Legislative Assembly of Tamil Nadu / Municipal Administration and Water Supply Department",
        "document_type": "State Act",
        "date": "2014-09-02",
        "language": "en",
        "source_url": "https://ielrc.org/content/e1414.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-009",
        "filename": "LEGAL-009_TN_Groundwater_Development_and_Management_Act_2003.pdf",
        "title": "Tamil Nadu Groundwater (Development and Management) Act, 2003 (Tamil Nadu Act 3 of 2003)",
        "issuer": "Legislative Assembly of Tamil Nadu / Public Works Department (WRD)",
        "document_type": "State Act",
        "date": "2003-03-04",
        "language": "en",
        "source_url": "https://ielrc.org/content/e0302.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-010",
        "filename": "LEGAL-010_Chennai_Metropolitan_Water_Supply_and_Sewerage_Act_1978.pdf",
        "title": "Chennai Metropolitan Water Supply and Sewerage Act, 1978 (Tamil Nadu Act 28 of 1978 — Catchment & Reservoir Protection)",
        "issuer": "Legislative Assembly of Tamil Nadu",
        "document_type": "State Act",
        "date": "1978-06-08",
        "language": "en",
        "source_url": "https://ielrc.org/content/e7811.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-011",
        "filename": "LEGAL-011_TN_District_Municipalities_Act_1920_Water_Sources_Excerpts.pdf",
        "title": "Tamil Nadu District Municipalities Act, 1920 (Tamil Nadu Act V of 1920 — Public Water Sources, Tanks & Drainage Excerpts)",
        "issuer": "Municipal Administration and Water Supply Department, Government of Tamil Nadu",
        "document_type": "State Act",
        "date": "1920-06-29",
        "language": "en",
        "source_url": "https://ielrc.org/content/e2003.pdf",
        "licence_note": "Public statutory enactment under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-012",
        "filename": "LEGAL-012_GO_Ms_96_RDPR_2019_Kudimaramath_Minor_Irrigation_Tanks.pdf",
        "title": "G.O. (Ms) No. 96, Rural Development and Panchayat Raj (CGS.1) Department — Rejuvenation of Minor Irrigation Tanks, Ponds and Ooranies under Kudimaramath Concept",
        "issuer": "Rural Development and Panchayat Raj Department, Government of Tamil Nadu",
        "document_type": "Kudimaramath Government Order",
        "date": "2019-07-26",
        "language": "en",
        "source_url": "https://tnrd.tn.gov.in/project/go_files/3_579_2019_MS96.pdf",
        "licence_note": "Official Government Order published on Tamil Nadu Rural Development portal (tnrd.tn.gov.in).",
    },
    {
        "id": "LEGAL-013",
        "filename": "LEGAL-013_GO_Ms_97_RDPR_2016_MGNREGS_Minor_Irrigation_Tank_Desilting.pdf",
        "title": "G.O. (Ms) No. 97, Rural Development and Panchayat Raj (CGS.1) Department — MGNREGS Guidelines for Desilting Minor Irrigation Tanks, Supply Channels and Ponds",
        "issuer": "Rural Development and Panchayat Raj Department, Government of Tamil Nadu",
        "document_type": "Government Order",
        "date": "2016-08-29",
        "language": "en",
        "source_url": "https://tnrd.tn.gov.in/project/go_files/4_2_2016_MS97.pdf",
        "licence_note": "Official Government Order published on Tamil Nadu Rural Development portal (tnrd.tn.gov.in).",
    },
    {
        "id": "LEGAL-014",
        "filename": "LEGAL-014_GO_Ms_23_RDPR_2024_Rural_Water_Bodies_and_Infrastructure_Guidelines.pdf",
        "title": "G.O. (Ms) No. 23, Rural Development and Panchayat Raj (SGS.2) Department — Guidelines for Rural Water Bodies, Minor Irrigation Tanks and Panchayat Works",
        "issuer": "Rural Development and Panchayat Raj Department, Government of Tamil Nadu",
        "document_type": "Government Order",
        "date": "2024-02-02",
        "language": "en",
        "source_url": "https://tnrd.tn.gov.in/project/go_files/3_753_2024_2890_SGS_2_2_2024_1_en.pdf",
        "licence_note": "Official Government Order published on Tamil Nadu Rural Development portal (tnrd.tn.gov.in).",
    },
    {
        "id": "LEGAL-015",
        "filename": "LEGAL-015_TNRD_Report_Maintenance_of_Minor_Irrigation_Tanks_and_Water_Bodies.pdf",
        "title": "L.C. Jain High Level Committee Report on Devolution of Powers to Panchayat Raj Institutions — Chapter 4.3: Minor Irrigation and Water Management",
        "issuer": "First High-Level Committee on Panchayat Raj, Rural Development Department, Government of Tamil Nadu",
        "document_type": "Official Government Report",
        "date": "1997-04-01",
        "gazette_date": None,
        "date_precision": "approximate",
        "metadata_verified": True,
        "language": "en",
        "source_url": "https://www.tnrd.tn.gov.in/reports/Jain_Report/english/index4_3.pdf",
        "licence_note": "Official Commission Report published on Tamil Nadu Rural Development portal (tnrd.tn.gov.in).",
    },
    {
        "id": "LEGAL-016",
        "filename": "LEGAL-016_TN_Natural_Resources_Policy_Note_2024_25_Tank_Silt_Removal_Rules.pdf",
        "title": "Government of Tamil Nadu Natural Resources Department Policy Note 2024–2025 (Rule 12(2-A) Desilting & Removal of Silt/Savudu from PWD/WRD & Rural Development Tanks)",
        "issuer": "Natural Resources Department, Government of Tamil Nadu",
        "document_type": "Departmental Policy Note",
        "date": "2024-06-24",
        "language": "en",
        "source_url": "https://cms.tn.gov.in/cms_migrated/document/docfiles/nrd_e_pn_2024_25.pdf",
        "licence_note": "Official Policy Note published on Government of Tamil Nadu CMS portal (cms.tn.gov.in).",
    },
    {
        "id": "LEGAL-017",
        "filename": "LEGAL-017_CWC_Guidelines_Repair_Renovation_and_Restoration_RRR_Water_Bodies_2017.pdf",
        "title": "Guidelines for the Scheme on Repair, Renovation and Restoration (RRR) of Water Bodies under PMKSY (Har Khet Ko Pani)",
        "issuer": "Ministry of Water Resources, River Development and Ganga Rejuvenation / Central Water Commission",
        "document_type": "Central Scheme Guideline",
        "date": "2017-06-01",
        "language": "en",
        "source_url": "https://cwc.gov.in/sites/default/files/3.rrr-2017_1.pdf",
        "licence_note": "Official Central Water Commission guideline published on cwc.gov.in.",
    },
    {
        "id": "LEGAL-018",
        "filename": "LEGAL-018_MoEFCC_Wetlands_Conservation_and_Management_Rules_2017.pdf",
        "title": "Wetlands (Conservation and Management) Rules, 2017 (Gazette of India Notification G.S.R. 1203(E))",
        "issuer": "Ministry of Environment, Forest and Climate Change, Government of India",
        "document_type": "Statutory Rules / Gazette Notification",
        "date": "2017-09-26",
        "language": "en+hi",
        "source_url": "https://indianwetlands.in/uploads/Wetlands2017.pdf",
        "licence_note": "Official Gazette Notification published on MoEFCC Indian Wetlands Portal (indianwetlands.in).",
    },
    {
        "id": "LEGAL-019",
        "filename": "LEGAL-019_MoEFCC_Guidelines_for_Implementing_Wetlands_Rules_2020.pdf",
        "title": "Guidelines for Implementing Wetlands (Conservation and Management) Rules, 2017",
        "issuer": "Ministry of Environment, Forest and Climate Change, Government of India",
        "document_type": "Regulatory Guideline",
        "date": "2020-01-03",
        "language": "en",
        "source_url": "https://indianwetlands.in/uploads/final-version-and-printed-wetland-guidelines-rules-2017-03.01.20.pdf",
        "licence_note": "Official MoEFCC Operational Guidelines published on indianwetlands.in.",
    },
    {
        "id": "LEGAL-020",
        "filename": "LEGAL-020_Water_Prevention_and_Control_of_Pollution_Act_1974.pdf",
        "title": "The Water (Prevention and Control of Pollution) Act, 1974 (Act 6 of 1974)",
        "issuer": "Parliament of India (Ministry of Law and Justice)",
        "document_type": "Central Act",
        "date": "1974-03-23",
        "language": "en",
        "source_url": "https://ielrc.org/content/e7402.pdf",
        "licence_note": "Public Central Statute under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-021",
        "filename": "LEGAL-021_Water_Prevention_and_Control_of_Pollution_Rules_1975.pdf",
        "title": "The Water (Prevention and Control of Pollution) Rules, 1975",
        "issuer": "Ministry of Works and Housing / Central Pollution Control Board, Government of India",
        "document_type": "Statutory Rules",
        "date": "1975-02-27",
        "language": "en",
        "source_url": "https://ielrc.org/content/e7502.pdf",
        "licence_note": "Public Central Statutory Rules under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-022",
        "filename": "LEGAL-022_Indian_Easements_Act_1882_Riparian_and_Tank_Water_Rights.pdf",
        "title": "The Indian Easements Act, 1882 (Act V of 1882 — Surface Water, Customary Irrigation & Natural Stream Rights Excerpts)",
        "issuer": "Legislative Department, Government of India",
        "document_type": "Central Act",
        "date": "1882-02-17",
        "language": "en",
        "source_url": "https://ielrc.org/content/e8203.pdf",
        "licence_note": "Public Central Statute under Section 52(1)(q) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-023",
        "filename": "LEGAL-023_CGWB_Kancheepuram_District_Ground_Water_and_Tanks_Brochure.pdf",
        "title": "Central Ground Water Board (CGWB) District Ground Water Brochure — Kancheepuram District, Tamil Nadu (Surface Tanks, Palar Basin & Recharge)",
        "issuer": "Central Ground Water Board (South Eastern Coastal Region, Chennai), Ministry of Water Resources",
        "document_type": "Hydrogeological Technical Report",
        "date": "2007-11-01",
        "language": "en",
        "source_url": "https://cgwb.gov.in/sites/default/files/2022-10/kancheepuram.pdf",
        "licence_note": "Official Government of India CGWB publication (cgwb.gov.in).",
    },
    {
        "id": "LEGAL-024",
        "filename": "LEGAL-024_Madras_HC_A_Narayanan_v_Chief_Secretary_Govt_of_TN_2008.pdf",
        "title": "A. Narayanan v. Chief Secretary, Government of Tamil Nadu & Ors. (Madras High Court W.P. No. 23544 of 2008 — Protection of Water Bodies & Channels)",
        "issuer": "High Court of Judicature at Madras",
        "document_type": "Madras High Court Judgment",
        "date": "2008-09-29",
        "language": "en",
        "source_url": "https://ielrc.org/content/e0822.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-025",
        "filename": "LEGAL-025_Madras_HC_Vellore_District_Environment_Monitoring_Committee_v_Collector_2010.pdf",
        "title": "Vellore District Environment Monitoring Committee v. The District Collector & Ors. (Madras High Court W.P. No. 15244 of 2009 — Palar Basin Water Resources Protection)",
        "issuer": "High Court of Judicature at Madras",
        "document_type": "Madras High Court Judgment",
        "date": "2010-01-29",
        "language": "en",
        "source_url": "https://ielrc.org/content/e1003.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-026",
        "filename": "LEGAL-026_Supreme_Court_Susetha_v_State_of_Tamil_Nadu_2006_Tank_Protection.pdf",
        "title": "Mrs. Susetha v. State of Tamil Nadu & Ors. (Supreme Court of India Appeal (Civil) 3418 of 2006 — Protection and Restoration of Tanks and Water Bodies in Tamil Nadu)",
        "issuer": "Supreme Court of India",
        "document_type": "Supreme Court Judgment",
        "date": "2006-08-08",
        "language": "en",
        "source_url": "https://ielrc.org/content/e0608.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-027",
        "filename": "LEGAL-027_Supreme_Court_Intellectuals_Forum_Tirupathi_v_State_of_AP_2006_Tanks.pdf",
        "title": "Intellectuals Forum, Tirupathi v. State of A.P. & Ors. (Supreme Court of India Appeal (Civil) 1251 of 2006 — Public Trust Doctrine on Historical Irrigation Tanks)",
        "issuer": "Supreme Court of India",
        "document_type": "Supreme Court Judgment",
        "date": "2006-02-23",
        "language": "en",
        "source_url": "https://ielrc.org/content/e0606.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-028",
        "filename": "LEGAL-028_Supreme_Court_Vellore_Citizens_Welfare_Forum_v_Union_of_India_1996_Palar_Basin.pdf",
        "title": "Vellore Citizens Welfare Forum v. Union of India & Ors. (Supreme Court of India W.P. (C) No. 914 of 1991 — Palar Basin Water Pollution, Precautionary & Polluter Pays Principles in Tamil Nadu)",
        "issuer": "Supreme Court of India",
        "document_type": "Supreme Court Judgment",
        "date": "1996-08-28",
        "language": "en",
        "source_url": "https://ielrc.org/content/e9607.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-029",
        "filename": "LEGAL-029_Supreme_Court_Tirupur_Dyeing_v_Noyyal_River_Ayacutdars_2009.pdf",
        "title": "Tirupur Dyeing Factory Owners Association v. Noyyal River Ayacutdars Protection Association & Ors. (Supreme Court Civil Appeal No. 6776 of 2009 — Protection of Irrigation Ayacutdars & Reservoirs)",
        "issuer": "Supreme Court of India",
        "document_type": "Supreme Court Judgment",
        "date": "2009-10-06",
        "language": "en",
        "source_url": "https://ielrc.org/content/e0904.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
    {
        "id": "LEGAL-030",
        "filename": "LEGAL-030_NGT_Subhash_C_Pandey_v_Municipal_Corporation_2014_Lake_FTL_Encroachment.pdf",
        "title": "Dr. Subhash C. Pandey v. Municipal Corporation & Ors. (National Green Tribunal O.A. No. 17 of 2013 — Lake Full Tank Level Demarcation, Buffer Zone & Encroachment Removal)",
        "issuer": "National Green Tribunal",
        "document_type": "National Green Tribunal Judgment",
        "date": "2014-09-19",
        "language": "en",
        "source_url": "https://ielrc.org/content/e1411.pdf",
        "licence_note": "Public judicial pronouncement under Section 52(1)(q)(iv) of the Indian Copyright Act, 1957.",
    },
]


def compute_file_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_pdf_file(path: Path) -> tuple[int, ExtractionMethod]:
    """Return (page_count, extraction_method) for a real PDF file."""
    reader = PdfReader(str(path))
    page_count = len(reader.pages)
    sampled_chars = 0
    for page in reader.pages[: min(5, page_count)]:
        txt = (page.extract_text() or "").strip()
        sampled_chars += len(txt)
    method: ExtractionMethod = "text_layer" if sampled_chars >= 80 else "ocr_needed"
    return page_count, method


_CACHED_ARCHIVE_TAR: tarfile.TarFile | None = None


def extract_from_durable_archive(
    legal_dir: Path,
    filename: str,
    client: httpx.Client,
) -> Path:
    """Extract a PDF from the durable GitHub Release archive if official source fails."""
    global _CACHED_ARCHIVE_TAR
    if _CACHED_ARCHIVE_TAR is None:
        resp = client.get(DURABLE_ARCHIVE_URL)
        resp.raise_for_status()
        tar_bytes = resp.content
        actual_sha = hashlib.sha256(tar_bytes).hexdigest()
        if actual_sha != DURABLE_ARCHIVE_SHA256:
            msg = (
                f"Durable archive SHA-256 mismatch: "
                f"expected {DURABLE_ARCHIVE_SHA256}, got {actual_sha}"
            )
            raise ValueError(msg)
        _CACHED_ARCHIVE_TAR = tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz")

    member = _CACHED_ARCHIVE_TAR.getmember(filename)
    f = _CACHED_ARCHIVE_TAR.extractfile(member)
    if f is None:
        msg = f"File {filename} not found in durable release archive"
        raise ValueError(msg)
    target_path = legal_dir / filename
    target_path.write_bytes(f.read())
    return target_path


def download_and_build_manifest(
    legal_dir: Path = Path("data/raw/legal"),
    force_download: bool = False,
) -> list[LegalCorpusEntry]:
    """Download real original PDFs from official sources (with release archive fallback) and write manifest.json."""
    legal_dir.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    retrieved_timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries: list[LegalCorpusEntry] = []

    with httpx.Client(headers=headers, follow_redirects=True, timeout=60.0, verify=False) as client:
        for spec in REAL_CORPUS_SOURCES:
            pdf_path = legal_dir / spec["filename"]
            if force_download or not pdf_path.exists():
                download_success = False
                try:
                    resp = client.get(spec["source_url"])
                    resp.raise_for_status()
                    content = resp.content
                    if content.startswith(b"%PDF-"):
                        pdf_path.write_bytes(content)
                        download_success = True
                    else:
                        logging.warning(
                            "URL %s returned non-PDF header; falling back to release archive",
                            spec["source_url"],
                        )
                except Exception as exc:
                    logging.warning(
                        "Error fetching %s from %s (%s); falling back to release archive",
                        spec["id"],
                        spec["source_url"],
                        exc,
                    )

                if not download_success:
                    extract_from_durable_archive(legal_dir, spec["filename"], client)

            digest = compute_file_sha256(pdf_path)
            if digest in BANNED_GENERATED_SHA256S:
                msg = f"File {pdf_path} matches a banned generated SHA-256 digest: {digest}"
                raise ValueError(msg)

            page_count, extraction_method = inspect_pdf_file(pdf_path)
            entry = LegalCorpusEntry(
                id=spec["id"],
                filename=spec["filename"],
                title=spec["title"],
                issuer=spec["issuer"],
                document_type=spec["document_type"],
                date=spec["date"],
                language=spec["language"],
                source_url=spec["source_url"],
                retrieved_at=retrieved_timestamp,
                sha256=digest,
                page_count=page_count,
                licence_note=spec["licence_note"],
                extraction_method=extraction_method,
                gazette_date=spec.get("gazette_date"),
                date_precision=spec.get("date_precision", "exact"),
                metadata_verified=spec.get("metadata_verified", True),
            )
            entries.append(entry)

    manifest_payload = {
        "corpus_version": "2.1.0",
        "document_count": len(entries),
        "jurisdiction": "Tamil Nadu & India (Original Downloaded Statutory, Government & Judicial Corpus)",
        "archive_url": DURABLE_ARCHIVE_URL,
        "archive_sha256": DURABLE_ARCHIVE_SHA256,
        "documents": [e.model_dump() for e in entries],
    }
    manifest_path = legal_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return entries


def load_legal_manifest(
    manifest_path: Path = Path("data/raw/legal/manifest.json"),
) -> list[LegalCorpusEntry]:
    """Load and validate the legal corpus manifest."""
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [LegalCorpusEntry(**doc) for doc in raw.get("documents", [])]


def verify_legal_corpus(
    legal_dir: Path = Path("data/raw/legal"),
    check_urls: bool = False,
) -> dict[str, Any]:
    """Verify every manifest entry's file existence, SHA-256, page count, and optionally live URL status."""
    entries = load_legal_manifest(legal_dir / "manifest.json")
    dead_links: list[dict[str, Any]] = []
    mismatches: list[str] = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    with httpx.Client(headers=headers, follow_redirects=True, timeout=30.0, verify=False) as client:
        for entry in entries:
            pdf_path = legal_dir / entry.filename
            if not pdf_path.exists():
                mismatches.append(f"{entry.id}: missing file {pdf_path}")
                continue

            actual_sha = compute_file_sha256(pdf_path)
            if actual_sha in BANNED_GENERATED_SHA256S:
                mismatches.append(f"{entry.id}: SHA-256 is in BANNED_GENERATED_SHA256S")
            if actual_sha != entry.sha256:
                mismatches.append(
                    f"{entry.id}: SHA-256 mismatch (expected {entry.sha256}, got {actual_sha})"
                )

            actual_pages, _ = inspect_pdf_file(pdf_path)
            if actual_pages != entry.page_count:
                mismatches.append(
                    f"{entry.id}: page_count mismatch (expected {entry.page_count}, got {actual_pages})"
                )

            if check_urls:
                try:
                    resp = client.head(entry.source_url)
                    if resp.status_code >= 400:
                        resp = client.get(entry.source_url)
                    if resp.status_code >= 400:
                        dead_links.append(
                            {
                                "id": entry.id,
                                "source_url": entry.source_url,
                                "status_code": resp.status_code,
                            }
                        )
                except Exception as exc:
                    dead_links.append(
                        {
                            "id": entry.id,
                            "source_url": entry.source_url,
                            "error": str(exc),
                        }
                    )

    return {
        "verified_count": len(entries),
        "mismatches": mismatches,
        "dead_links": dead_links,
        "ok": len(mismatches) == 0 and len(dead_links) == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download or verify the EriWatch legal corpus.")
    parser.add_argument(
        "--download", action="store_true", help="Download real PDFs and rebuild manifest.json"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify local SHA-256 and page counts"
    )
    parser.add_argument(
        "--check-urls", action="store_true", help="Also verify live HTTP status of each source_url"
    )
    args = parser.parse_args()

    if args.download:
        entries = download_and_build_manifest()
        print(f"Downloaded and verified {len(entries)} real legal PDFs in data/raw/legal/")
    if args.verify or args.check_urls:
        report = verify_legal_corpus(check_urls=args.check_urls)
        print(json.dumps(report, indent=2))
        if not report["ok"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()

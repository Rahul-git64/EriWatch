# Data Licensing, Attribution, and Ethics Governance (`docs/data/licensing_and_ethics.md`)

## 1. Public Data Provenance & Attribution Table

EriWatch relies exclusively on open-access satellite missions, public meteorological/hydrological portals, open geospatial registries, and published statutory/judicial documents. No proprietary, scraped personal, or closed-commercial datasets are used.

| Dataset | Provider / Custodial Agency | Licence | Mandatory Attribution String |
|---|---|---|---|
| **Sentinel-2 L2A Optical Imagery** | European Space Agency (ESA) / Copernicus Programme (hosted via Microsoft Planetary Computer & Element84 Earth Search) | Copernicus Open Access License (Free, Full & Open) | *"Contains modified Copernicus Sentinel data [2019–2026], processed by EriWatch."* |
| **JRC Global Surface Water (`jrc-gsw`)** | European Commission Joint Research Centre (Pekel et al., *Nature*, 2016) | European Union Reuse Notice (`CC-BY-4.0` equivalent) | *"Source: EC Joint Research Centre Global Surface Water (Pekel et al., 2016)."* |
| **Daily Rainfall & Subsurface Wetness (`PRECTOTCORR`, `T2M`, `GWETROOT`, `GWETPROF`)** | NASA Langley Research Center (LaRC) POWER Project | NASA Open Data Policy (Public Domain / `CC0`) | *"Data obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program."* |
| **Groundwater Station Telemetry** | Central Ground Water Board (CGWB) & India-WRIS (Ministry of Jal Shakti, Govt. of India) | Government Open Data License – India (`GODL-India`) | *"Groundwater station data courtesy of India-WRIS and Central Ground Water Board (CGWB), Government of India."* |
| **Water-Body Boundaries (`osm`)** | OpenStreetMap Contributors | Open Database License (`ODbL 1.0`) | *"© OpenStreetMap contributors, licensed under ODbL 1.0."* |
| **Statutory Acts, WRD Government Orders, and Court Judgments** | Tamil Nadu Water Resources Department (WRD / PWD), Madras High Court, and National Green Tribunal (Southern Zone) | Section 52(1)(q) of the Indian Copyright Act, 1957 (Public legislative enactments, government orders, and judicial pronouncements) | *"Cited from public orders of the Tamil Nadu Water Resources Department, Madras High Court, and National Green Tribunal."* |

---

## 2. Privacy & Personal Data Minimisation

1. **Zero Unnecessary Personal Data:**
   - Exploring tank maps, water-spread histories, 30-day forecasts, and shrinkage analytics requires **no login and zero personal data**.
2. **Protection of Complainant Identity & PII Masking:**
   - When a citizen or panchayat representative files a grievance, contact details are encrypted or hashed at rest (`PII_ENCRYPTION_KEY`) and are never exposed on public endpoints.
   - Before any complaint text is sent to an external LLM API (`Gemini Flash` or `Groq`), `packages/rag` automatically masks phone numbers, Aadhaar/ID patterns, email addresses, and personal names (`[REDACTED_PHONE]`, `[REDACTED_NAME]`) so no personally identifiable information leaves the platform.
3. **Photo Upload Safety:**
   - Uploaded complaint photos are validated for MIME type (`image/jpeg`, `image/png`, `image/webp`), capped at 5 MB, and stripped of GPS/device EXIF metadata if requested by the complainant.

---

## 3. Algorithmic & Legal Safeguards

1. **Mandatory Human-in-the-Loop (HITL) Petition Review:**
   - EriWatch **never** auto-dispatches a legal petition to government authorities without explicit human review and approval (`status: "approved"` logged in `audit_log` with reviewer ID and timestamp).
2. **Strict Grounding & Refusal Policy:**
   - Every legal claim in a generated petition draft must carry an inline citation (`doc_id`, `page`, `clause`) resolving to a passage in the verified WRD / High Court / NGT corpus.
   - If retrieval similarity falls below the calibrated threshold or no statutory clause supports the user's request, the system **refuses to fabricate a legal citation** and clearly states that no supporting government order was found in the corpus.
3. **Uncertainty Transparency on Satellite & ML Outputs:**
   - Satellite observations during monsoon cloud cover are explicitly flagged (`cloudy`, `partial`, `low_confidence`) rather than interpolated silently.
   - Encroachment and shrinkage findings are presented as *preliminary remote-sensing indicators* (`confidence: "high" | "medium"`) requiring field verification by Revenue / WRD survey officials, preventing false accusation harm.

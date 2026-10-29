# Pilot Tank Selection Criteria & Cohort (Chengalpattu & Kancheepuram Districts)

## 1. Regional Rationale

EriWatch focuses its pilot cohort on **36 irrigation tanks (*eris*)** across **Kancheepuram** (18 tanks) and **Chengalpattu** (18 tanks) districts in northern Tamil Nadu (`12.35°N – 13.06°N, 79.60°E – 80.23°E`). This region was selected for four reasons:

1. **Hydrological & Flood Criticality:** The Adyar, Palar, and Ongur river sub-basins contain dense cascading tank chains (*system* and *non-system* tanks) that directly buffer Northeast Monsoon floodwaters entering the southern Chennai Metropolitan Area while irrigating *Samba* and *Navarai* paddy crops.
2. **Ground-Truth Accessibility:** Located within 15–75 km of SAI University (Paiyanur / OMR, Chengalpattu District), allowing direct physical verification of tank bunds, sluices, and encroachment patterns.
3. **Sentinel-2 Tile Efficiency:** All 36 tanks fall within just two adjacent Sentinel-2 MGRS tiles (`44PLV` and `44PLU`, plus the southern edge of `44PMV`), minimizing STAC metadata queries while maximizing temporal revisit consistency (5-day revisit with Sentinel-2A/2B/2C).
4. **Diversity of Urbanisation & Hydrological Stress:** Spans peri-urban IT-corridor tanks facing severe real-estate encroachment (e.g., *Pallikaranai*, *Perumbakkam*, *Medavakkam*, *Chitlapakkam*, *Sembakkam*, *Thaiyur*) alongside large rural agricultural system tanks facing siltation and canal-inflow volatility (e.g., *Madurantakam*, *Thenneri*, *Uthiramerur*, *Parandur*, *Sriperumbudur*).

## 2. Quantitative Selection Criteria

Every tank in the 36-tank pilot cohort satisfies all four engineering criteria:

1. **Minimum Spatial Resolution Threshold ($\ge 12\text{ ha}$ historical maximum area):**
   - At Sentinel-2's 10 m native resolution (`B03` Green, `B08` NIR), 1 pixel equals $100\text{ m}^2 = 0.01\text{ ha}$, and at 20 m (`B11` SWIR1, `SCL`), 1 pixel equals $400\text{ m}^2 = 0.04\text{ ha}$.
   - Requiring a historical maximum extent of $\ge 12\text{ ha}$ ensures at least **1,200 pixels at 10 m** (300 pixels at 20 m) per tank, preventing mixed-pixel boundary noise from dominating the water-spread time series.
2. **Stratified Hydrological State Distribution:**
   - **`healthy` (12 tanks):** Perennial or well-maintained major system tanks with stable monsoon fill and $\le 10\%$ long-term footprint loss.
   - **`seasonal` (13 tanks):** Rainfed (*non-system*) agricultural tanks that fill sharply during the October–December Northeast Monsoon and draw down below 15% capacity by May–July.
   - **`shrinking` (11 tanks):** Peri-urban or silted tanks exhibiting documented boundary loss, weed infestation (*Eichhornia crassipes* / *Prosopis juliflora*), or residential encroachment against their historical maximum footprint.
3. **Administrative Coverage:**
   - **Kancheepuram District (18 tanks across 5 blocks):** Kundrathur, Sriperumbudur, Walajabad, Kancheepuram, and Uthiramerur.
   - **Chengalpattu District (18 tanks across 6 blocks):** St. Thomas Mount, Thiruporur, Kattankolathur, Chengalpattu, Tirukalukundram, and Madurantakam.
4. **Boundary Provenance Transparency:**
   - Polygons sourced from OpenStreetMap (`osm`) carry `confidence = "high"` when verified against JRC Global Surface Water extent.
   - Where OSM ways are incomplete or unclosed for rural tanks, boundaries are digitised/derived from historical maximum water extent (`derived`) and explicitly flagged so downstream analytics and users know the provenance.

---

## 3. Pilot Cohort Table (36 Tanks)

| ID | Tank Name | District | Block | Centroid (`lat, lon`) | Nominal Max Area (ha) | State Archetype | Boundary Source |
|---|---|---|---|---|---|---|---|
| `TN-KPM-001` | Chembarambakkam Periya Eri | Kancheepuram | Kundrathur | `13.0116, 80.0592` | 1520.0 | `healthy` | `osm` |
| `TN-KPM-002` | Thenneri Hissa Eri | Kancheepuram | Walajabad | `12.8586, 79.8825` | 385.0 | `healthy` | `osm` |
| `TN-KPM-003` | Sriperumbudur Periya Eri | Kancheepuram | Sriperumbudur | `12.9675, 79.9418` | 290.0 | `healthy` | `osm` |
| `TN-KPM-004` | Uthiramerur Vaikunda Perumal Eri | Kancheepuram | Uthiramerur | `12.6165, 79.7558` | 480.0 | `seasonal` | `osm` |
| `TN-KPM-005` | Parandur Periya Eri | Kancheepuram | Kancheepuram | `12.9312, 79.7544` | 215.0 | `shrinking` | `derived` |
| `TN-KPM-006` | Kundrathur Periya Eri | Kancheepuram | Kundrathur | `12.9974, 80.0972` | 145.0 | `shrinking` | `osm` |
| `TN-KPM-007` | Manimangalam Eri | Kancheepuram | Kundrathur | `12.9182, 80.0419` | 175.0 | `healthy` | `osm` |
| `TN-KPM-008` | Somangalam Eri | Kancheepuram | Kundrathur | `12.9488, 80.0365` | 118.0 | `seasonal` | `osm` |
| `TN-KPM-009` | Pillaipakkam Eri | Kancheepuram | Sriperumbudur | `12.9905, 79.9852` | 132.0 | `shrinking` | `osm` |
| `TN-KPM-010` | Nemili Eri (Sriperumbudur) | Kancheepuram | Sriperumbudur | `12.9415, 79.9912` | 94.0 | `seasonal` | `derived` |
| `TN-KPM-011` | Sunguvarchatram Eri | Kancheepuram | Sriperumbudur | `12.9278, 79.8695` | 88.0 | `shrinking` | `derived` |
| `TN-KPM-012` | Walajabad Chitheri | Kancheepuram | Walajabad | `12.7932, 79.8214` | 76.0 | `seasonal` | `derived` |
| `TN-KPM-013` | Nathapettai Eri | Kancheepuram | Kancheepuram | `12.8218, 79.7345` | 162.0 | `healthy` | `osm` |
| `TN-KPM-014` | Mamandur Vadakku Eri | Kancheepuram | Kancheepuram | `12.7458, 79.6621` | 310.0 | `healthy` | `osm` |
| `TN-KPM-015` | Dusi Mamandur Big Tank | Kancheepuram | Kancheepuram | `12.7685, 79.6712` | 410.0 | `seasonal` | `osm` |
| `TN-KPM-016` | Oragadam Vaipoor Eri | Kancheepuram | Walajabad | `12.8384, 79.9410` | 68.0 | `shrinking` | `derived` |
| `TN-KPM-017` |Padappai Karasangal Eri | Kancheepuram | Kundrathur | `12.8855, 80.0258` | 64.0 | `shrinking` | `derived` |
| `TN-KPM-018` |Edamichi Periya Eri | Kancheepuram | Uthiramerur | `12.5642, 79.7890` | 140.0 | `seasonal` | `derived` |
| `TN-CGL-001` | Madurantakam Periya Eri | Chengalpattu | Madurantakam | `12.5133, 79.8736` | 970.0 | `healthy` | `osm` |
| `TN-CGL-002` | Kolavai Lake (Chengalpattu) | Chengalpattu | Kattankolathur | `12.7072, 79.9856` | 720.0 | `healthy` | `osm` |
| `TN-CGL-003` | Ponneri /Maraimalai Nagar Eri | Chengalpattu | Kattankolathur | `12.7945, 80.0265` | 92.0 | `shrinking` | `osm` |
| `TN-CGL-004` | Guduvancheri Nandhivaram Eri | Chengalpattu | Kattankolathur | `12.8432, 80.0598` | 85.0 | `shrinking` | `osm` |
| `TN-CGL-005` | Urapakkam Kilambakkam Eri | Chengalpattu | Kattankolathur | `12.8648, 80.0685` | 54.0 | `shrinking` | `derived` |
| `TN-CGL-006` | Sembakkam Periya Eri | Chengalpattu | St. Thomas Mount | `12.9242, 80.1585` | 78.0 | `shrinking` | `osm` |
| `TN-CGL-007` | Chitlapakkam Eri | Chengalpattu | St. Thomas Mount | `12.9336, 80.1412` | 36.0 | `shrinking` | `osm` |
| `TN-CGL-008` | Medavakkam Periya Eri | Chengalpattu | St. Thomas Mount | `12.9125, 80.1842` | 62.0 | `shrinking` | `osm` |
| `TN-CGL-009` | Perumbakkam Eri | Chengalpattu | St. Thomas Mount | `12.8995, 80.1985` | 96.0 | `healthy` | `osm` |
| `TN-CGL-010` | Siruseri Navalur Eri | Chengalpattu | Thiruporur | `12.8352, 80.2145` | 58.0 | `seasonal` | `derived` |
| `TN-CGL-011` | Kelambakkam Pudupakkam Eri | Chengalpattu | Thiruporur | `12.7965, 80.2054` | 72.0 | `seasonal` | `derived` |
| `TN-CGL-012` | Thaiyur Periya Eri | Chengalpattu | Thiruporur | `12.7625, 80.1892` | 185.0 | `healthy` | `osm` |
| `TN-CGL-013` | Thiruporur Periya Eri | Chengalpattu | Thiruporur | `12.7245, 80.1845` | 130.0 | `seasonal` | `osm` |
| `TN-CGL-014` | Paiyanur Eri (Near SAI Univ) | Chengalpattu | Thiruporur | `12.6685, 80.1582` | 66.0 | `seasonal` | `derived` |
| `TN-CGL-015` | Manamai / Kunnathur Eri | Chengalpattu | Tirukalukundram | `12.6012, 80.1485` | 74.0 | `seasonal` | `derived` |
| `TN-CGL-016` | Tirukalukundram Kondangi Eri | Chengalpattu | Tirukalukundram | `12.6185, 80.0542` | 195.0 | `healthy` | `osm` |
| `TN-CGL-017` | Nenmeli Eri (Chengalpattu) | Chengalpattu | Chengalpattu | `12.6642, 79.9985` | 112.0 | `seasonal` | `derived` |
| `TN-CGL-018` | Karunguzhi Eri | Chengalpattu | Madurantakam | `12.5415, 79.8942` | 148.0 | `healthy` | `osm` |

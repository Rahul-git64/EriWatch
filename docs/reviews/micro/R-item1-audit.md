# Micro-Review: Item 1 — TN-CGL-010 Verification Audit and Notes

## Scope of Work
Addressed User Requirement 1:
1. **Audited TN-CGL-010 Identity & Sources**:
   - Location: Navalur Periya Eri / Navalur Lake (nominal 24.99 ha in registry, 33.43 acres total site), Thiruporur taluk, Chengalpattu district, situated within the SIPCOT IT Park in Siruseri.
   - Project: Rejuvenated by the State Industries Promotion Corporation of Tamil Nadu (SIPCOT) at ₹30 crore as the "Navalur Lake Eco Park" (*Namma Navalur*, [nammanavalur.com](https://nammanavalur.com)). Reported in regional press (e.g., Times of India) regarding urban green infrastructure and local resident concerns over peripheral earth-filling and embankment narrowing.
2. **Explicit `unverified` Status**:
   - Formally designated claims of "circular aeration islands" and "seasonal algal blooms" as **`unverified`** in both `data/processed/tank_registry.geojson` (`notes` property) and `docs/adr/0005-water-spread-measurement-and-quality-flags.md` Section 4, acknowledging that no in-situ sensor telemetry or water quality measurements have been logged.
3. **Geometry Unaltered**:
   - The polygon geometry in `data/processed/tank_registry.geojson` was strictly retained without any modification.

## Verification
- `uv run pytest packages/geo/tests/test_registry.py -v` -> 3 passed in 2.47s.
- `uv run ruff check .` -> All checks passed.

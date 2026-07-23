#!/usr/bin/env python3
"""One-off generator for the DIAG-MACROBETA-0001 a-priori sign map.

Run ONCE, before outcome contact. Output is hash-pinned in the register row.
"""
import csv
import hashlib
from pathlib import Path

OUT = Path.home() / "alpha-research" / "governance" / "prereg" / "DIAG-MACROBETA-0001_sign_map.csv"

# (symbols, sector, crude_sign, fx_sign, channel)
# crude_sign / fx_sign in {POS, NEG, AMB, NA}
#   POS = stock return loads POSITIVELY on the factor's log return
#   fx factor = USDINR: POS means the stock RISES when the rupee DEPRECIATES
#   AMB = economically ambiguous by construction -> EXCLUDED from hit-rate scoring
#         but reported (its own prediction is "no reliable sign")
#   NA  = no prediction offered on that factor -> excluded from scoring
BUCKETS = [
    # ---------------- CRUDE-POSITIVE ----------------
    (["ONGC", "OIL"], "Upstream E&P", "POS", "POS",
     "Realisation is the crude price itself; sold in USD. CAVEAT: subsidy-sharing "
     "(pre-2015) and the 2022 windfall levy cap the upside, so this is partly a policy beta."),
    (["CHENNPETRO", "MRPL"], "Standalone refining", "POS", "AMB",
     "GRM + crude-inventory gains rise with crude; USD crude purchase vs USD-linked "
     "product realisation roughly offsets on FX."),
    (["COALINDIA"], "Thermal coal", "POS", "AMB",
     "Energy substitution: seaborne thermal coal co-moves with crude; domestic "
     "notified pricing damps it. Weak prediction."),

    # ---------------- CRUDE-NEGATIVE ----------------
    (["INDIGO", "JETAIRWAYS"], "Aviation", "NEG", "NEG",
     "ATF is 30-40% of opex and is priced off crude in USD; USD operating-lease and "
     "maintenance liabilities. Expected negative on BOTH factors - the sharpest joint call in the map."),
    (["ASIANPAINT", "BERGEPAINT", "KANSAINER", "AKZOINDIA"], "Paints", "NEG", "NEG",
     "~50%+ of the RM basket is crude-derived (monomers, solvents, resins) plus imported "
     "TiO2 priced in USD; domestic pricing with lagged pass-through."),
    (["MRF", "APOLLOTYRE", "CEATLTD", "JKTYRE"], "Tyres (domestic-skewed)", "NEG", "NEG",
     "Carbon black and synthetic rubber are crude derivatives; natural rubber and CB "
     "feedstock are imported in USD. Domestic replacement/OEM pricing."),
    (["BALKRISIND"], "Tyres (export-skewed)", "NEG", "POS",
     "Same crude-derived input cost, but ~70%+ of revenue is off-highway export in EUR/USD, "
     "so the FX sign FLIPS versus the domestic tyre makers. Deliberate discriminating test."),
    (["PIDILITIND"], "Adhesives", "NEG", "NEG",
     "VAM (vinyl acetate monomer) is crude/gas-linked and imported."),
    (["SUPREMEIND", "ASTRAL", "UFLEX", "COSMOFIRST", "JINDALPOLY",
      "TIMETECHNO", "NILKAMAL", "VIPIND"], "Plastics / packaging / pipes", "NEG", "NA",
     "PVC, PP, PE, BOPET/BOPP resin are direct crude/naphtha derivatives - the highest "
     "input-cost share in the map. FX left NA except POLYPLEX (below)."),
    (["CASTROLIND", "GULFOILLUB"], "Lubricants", "NEG", "NEG",
     "Base oil is a refinery cut (crude derivative) and largely imported in USD."),
    (["IOC", "BPCL", "HINDPETRO"], "Oil marketing companies", "NEG", "NEG",
     "POLICY BETA, NOT A PURE INPUT-COST BETA. Crude bought in USD; retail pricing was "
     "administered/politically frozen for material parts of the window (2017-18, 2021-22), "
     "so marketing margin compresses when crude rises. Under true daily pricing the sign "
     "would be neutral-to-positive (inventory gains). PRE-STATED RISK: expect sub-period sign instability."),
    (["IGL", "MGL", "GUJGASLTD", "PETRONET"], "City gas / LNG", "NEG", "NEG",
     "Gas sourced on crude-linked LNG contracts and APM formula, priced in USD; "
     "regulated/competitive retail pricing with lagged pass-through."),
    (["ULTRACEMCO", "SHREECEM", "ACC", "AMBUJACEM", "DALBHARAT", "JKCEMENT",
      "RAMCOCEM"], "Cement", "NEG", "NA",
     "Pet coke is a refinery product and diesel freight is a large cost line; "
     "power+fuel+freight is ~50% of cost. Moderate."),
    (["MARUTI", "HEROMOTOCO", "TVSMOTOR", "EICHERMOT"], "Autos (domestic demand)", "NEG", "NA",
     "Retail fuel cost is a direct running-cost drag on 2W and entry-car demand. Weak."),
    (["BAJAJ-AUTO"], "Autos (export-skewed)", "NEG", "POS",
     "Same domestic running-cost drag, but ~40% of volume is exported (Africa/LatAm) "
     "in USD, so FX sign is positive. Discriminating test versus HEROMOTOCO."),
    (["HINDUNILVR", "MARICO", "GODREJCP", "DABUR", "COLPAL"], "FMCG", "NEG", "NA",
     "LAB (linear alkyl benzene), HDPE/PET packaging and some palm-substitute inputs are "
     "crude-linked. Weak."),

    # ---------------- USDINR-POSITIVE ----------------
    (["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS",
      "PERSISTENT", "COFORGE"], "IT services", "NA", "POS",
     "70-90% USD/EUR/GBP revenue against an almost entirely INR cost base - the single "
     "strongest a-priori claim in this study. If IT does not load positively on USDINR, "
     "the METHOD is suspect, not the economics."),
    (["SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "AUROPHARMA", "DIVISLAB", "TORNTPHARM",
      "GLENMARK", "ALKEM", "ZYDUSLIFE", "NATCOPHARM", "GRANULES", "LAURUSLABS",
      "BIOCON", "SYNGENE", "IPCALAB", "JUBLPHARMA"], "Pharma exporters", "NA", "POS",
     "Large US/EU generic and CRAMS revenue in USD. WEAKER than IT: KSM/API inputs are "
     "imported from China in USD and several carry USD acquisition debt, both offsetting."),
    (["WELSPUNIND", "TRIDENT", "KPRMILL", "VTL", "ARVIND"], "Textile exporters", "NA", "POS",
     "Home-textile and yarn/garment export revenue in USD against INR cotton and INR labour."),
    (["NATIONALUM", "HINDZINC", "NMDC"], "Metals - net exporters, low USD debt", "NA", "POS",
     "LME/global reference prices are set in USD, so INR realisation rises mechanically "
     "with depreciation, and these three carry little USD debt to offset it."),
    (["POLYPLEX"], "Packaging films - overseas ops", "NEG", "POS",
     "Crude-derived PET chip input (NEG on crude) but a majority of capacity and revenue "
     "sits in overseas subsidiaries, so translated earnings rise with depreciation."),
    (["MUTHOOTFIN", "MANAPPURAM"], "Gold-loan NBFC", "NA", "POS",
     "Collateral is gold, priced in USD internationally; INR gold rises with depreciation, "
     "improving LTV headroom and disbursement value. Weak."),

    # ---------------- USDINR-NEGATIVE ----------------
    (["DIXON", "AMBER", "HAVELLS", "VOLTAS", "BLUESTARCO", "CROMPTON", "WHIRLPOOL",
      "ORIENTELEC", "BAJAJELEC", "SYMPHONY"], "Consumer durables / EMS", "NA", "NEG",
     "Components, compressors and finished-goods sourcing from China/ASEAN invoiced in USD; "
     "sales entirely domestic in INR."),
    (["POLYCAB", "KEI"], "Wires & cables", "NA", "NEG",
     "Copper and aluminium are LME-priced in USD; domestic INR sales with lagged pass-through."),
    (["BHARTIARTL", "IDEA"], "Telecom", "NA", "NEG",
     "Large USD-denominated debt and USD-priced network equipment against INR revenue; "
     "MTM on the debt hits reported earnings directly."),
    (["TATAPOWER"], "Power - imported coal", "AMB", "NEG",
     "Mundra runs on imported coal invoiced in USD plus USD debt (FX NEG). Crude sign is "
     "AMB because the Indonesian coal-mine stake is a natural hedge on the commodity leg."),

    # ---------------- EXPLICITLY AMBIGUOUS (reported, NOT scored) ----------------
    (["RELIANCE"], "Conglomerate - refining+petchem+retail+telecom", "AMB", "AMB",
     "PRE-STATED SIGN-CHANGER. Refining/petchem argues crude-positive; the Jio (2016+) and "
     "Retail build-out progressively dilutes energy in the mix, and O2C is a crude BUYER. "
     "Net exposure plausibly changes sign within the window, so no directional prediction is offered."),
    (["HINDALCO", "TATASTEEL", "JSWSTEEL", "VEDL"], "Metals - large USD debt", "AMB", "AMB",
     "USD-linked realisation argues FX-positive; large USD debt stacks (Novelis, Corus/TSE) "
     "argue FX-negative. Net sign is not determinable a priori."),
    (["SRF", "AARTIIND", "ATUL", "DEEPAKNTR", "NOCIL", "VINATIORGA", "FLUOROCHEM",
      "NAVINFLUOR", "PIIND", "TATACHEM"], "Specialty chemicals", "AMB", "AMB",
     "Benzene/toluene/naphtha derivatives are the feedstock (crude-negative) but most "
     "contracts are cost-plus with fast pass-through and a large export book (FX-positive), "
     "so neither sign is defensible ex ante. DELIBERATELY UNSCORED - the alternative is an "
     "unfalsifiable map in which every chemical name confirms the theory."),
    (["TITAN", "KALYANKJIL", "RAJESHEXPO"], "Jewellery", "NA", "AMB",
     "Higher INR gold lifts inventory value and ticket size but suppresses volume; the two "
     "effects have opposite signs and different lags."),
    (["ADANIPORTS", "ADANIGREEN", "ADANITRANS"], "Adani group", "AMB", "AMB",
     "USD debt argues FX-negative, but the Jan-2023 Hindenburg episode dominates this "
     "group's return variance in the window and is unrelated to macro betas. Reported, not scored."),
    (["GESHIP", "SCI"], "Shipping", "AMB", "AMB",
     "Bunker fuel is a crude-derived cost, but tanker charter rates often RISE with oil "
     "dislocation; freight is USD-earned against USD debt."),
    (["GRASIM"], "VSF / diversified", "AMB", "NA",
     "Energy and caustic costs argue crude-negative; VSF competes with crude-derived "
     "polyester, so higher crude can help pricing."),
]

HEADER = ["symbol", "sector", "crude_sign", "fx_sign", "channel"]

rows = []
seen = {}
for symbols, sector, cs, fs, channel in BUCKETS:
    for s in symbols:
        if s in seen:
            raise SystemExit(f"duplicate symbol in map: {s} ({seen[s]} vs {sector})")
        seen[s] = sector
        rows.append([s, sector, cs, fs, channel])

rows.sort(key=lambda r: r[0])

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(HEADER)
    w.writerows(rows)

h = hashlib.sha256(OUT.read_bytes()).hexdigest()
n_crude = sum(1 for r in rows if r[2] in ("POS", "NEG"))
n_fx = sum(1 for r in rows if r[3] in ("POS", "NEG"))
print(f"wrote {len(rows)} symbols -> {OUT}")
print(f"directional crude predictions: {n_crude}")
print(f"directional fx    predictions: {n_fx}")
print(f"sha256 {h}")

# Data Model — PSC Consumer Record Search Tool

**Feature:** 1-psc-consumer-search
**Date:** 2026-04-05

---

## Source: PSCData - PSCData.csv

All entities are derived from a single flat CSV file. No relational joins occur at runtime;
the model below documents the logical relationships embedded in the data.

---

## Entity: ConsumerRecord (primary)

Represents a single electricity consumer registered with PSC.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| Cons_No | string | No | Unique consumer number (e.g., `BL001271`) |
| Contract_Ac | string | No | Contract account number (12+ digits) |
| Contract | string | Yes | Internal contract reference |
| Install_No | string | Yes | Installation number (starts with 7) |
| GIC_Code | string | Yes | Geographic identification code |
| Sch_No. | string | Yes | Schedule number |
| Leg_Ac_No | string | Yes | Legacy account number |
| Meter_No | string | Yes | Physical meter serial number |
| Meter_Typ | string | Yes | Meter type (CTO, Hook, Inactive, …) |
| Tariff | string | Yes | Tariff code (A3-G, E-1_I, …) |
| PSC_Cons_IBC | string | Yes | IBC numeric ID |
| IBC_Name | string | Yes | IBC name (e.g., JOHAR, GADAP) |
| AMR_STATUS | string | Yes | AMR status: AMR, NON AMR, Inactive, Active |
| Actual_Latitude | float | Yes | GPS latitude (0 if unknown) |
| Actual_Longitude | float | Yes | GPS longitude (0 if unknown) |
| DTS_ID | string | Yes | Distribution Transformer Station ID |
| PMT_Name | string | Yes | Primary Metering Terminal name |
| FeederID_(BH) | string | Yes | BH feeder ID |
| Feeder_Name_(BH) | string | Yes | BH feeder name |
| FeederID | string | Yes | Active feeder ID |
| Feeder_Name | string | Yes | Active feeder name |
| CM_No | string | Yes | Commercial Manager number |

**Primary key:** `Cons_No`

---

## Logical Relationships (inferred, not enforced)

```
Feeder (FeederID)
  └── DTS (DTS_ID)      [one feeder → many DTS]
        └── Consumer (Cons_No)  [one DTS → many consumers]
              ├── Meter (Meter_No, Meter_Typ)
              ├── IBC (IBC_Name)
              └── PMT (PMT_Name)
```

---

## Searchable Field Index

| Logical Name | CSV Column | Auto-Detect Pattern | Aliases |
|---|---|---|---|
| Consumer No | Cons_No | `^[A-Z]{2}\d+$` | cons, consumer, consno, cons_no |
| Contract Account | Contract_Ac | `^4\d{11,}$` | contract, contract_ac, account |
| Install No | Install_No | `^7\d{9,}$` | install, install_no |
| GIC Code | GIC_Code | `^[A-Z]\d{4}$` | gic, gic_code |
| Meter No | Meter_No | `^(CTO-\|TY\|TJ\|TL)\w+` | meter, meter_no |
| Meter Type | Meter_Typ | keyword: CTO,THREE,HOOK,INACTIVE | meter_type, meter_typ, type, cto |
| Tariff | Tariff | `^[A-Z]\d[-_][A-Z]` | tariff |
| IBC Name | IBC_Name | none (partial text) | ibc, ibc_name |
| AMR Status | AMR_STATUS | keyword: AMR,NON AMR,INACTIVE,ACTIVE | amr, amr_status, status |
| DTS ID | DTS_ID | `^\d{4,7}$` | dts, dts_id |
| PMT Name | PMT_Name | none (partial text) | pmt, pmt_name |
| Feeder Name | Feeder_Name | none (partial text) | feeder, feeder_name |
| Feeder ID | FeederID | none (numeric) | feeder_id, feederid |

---

## Validation Rules

| Rule | Field | Constraint |
|------|-------|------------|
| V-01 | Cons_No | 2 uppercase letters + digits |
| V-02 | AMR_STATUS | One of: AMR, NON AMR, Inactive, Active (case-insensitive) |
| V-03 | Meter_Typ | One of: CTO, Three, Hook, Inactive (case-insensitive) |
| V-04 | DTS_ID | 4–7 digit numeric string |
| V-05 | Tariff | Letter + digit + hyphen/underscore + letter (e.g., A3-G) |

*Validation is used for auto-detection only; the tool does not reject records failing validation.*

---

## State Transitions

| Field | Possible Values | Notes |
|-------|----------------|-------|
| AMR_STATUS | AMR → NON AMR → Inactive | Reflects metering upgrade lifecycle |
| Meter_Typ | CTO / Hook / Three / Inactive | Meter hardware type; Inactive = decommissioned |

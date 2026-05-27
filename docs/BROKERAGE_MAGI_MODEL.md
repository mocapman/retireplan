# Simple Brokerage MAGI Model

## Purpose

This document defines the simplest useful brokerage/MAGI model for RetirePlan.

The goal is not tax-lot precision.

The goal is to give the retirement planner enough information to estimate the tax and MAGI impact of using taxable brokerage money for spending.

The detailed MAGI Tracker remains separate.

RetirePlan should answer the annual planning question:

```text
If I need to use brokerage money this year, how much of that creates taxable capital gain and MAGI?
```

---

## Design Decision

RetirePlan will not track individual brokerage tax lots.

RetirePlan will model taxable brokerage as three simple buckets:

```text
brokerage_cash
brokerage_cost_basis
brokerage_unrealized_gain
```

From those values, the planner can estimate the taxable gain created when holdings are sold.

This is enough for rough annual planning.

The MAGI Tracker can handle current-year details such as loss harvesting, lot selection, and sale timing.

---

## Core Brokerage Buckets

## 1. Brokerage Cash

Brokerage cash is already cash.

Using brokerage cash for spending does not create taxable capital gain.

```text
Brokerage cash used → $0 new capital gain
```

## 2. Brokerage Cost Basis

Cost basis is the already-taxed principal inside taxable holdings.

When holdings are sold, this portion is not taxable again.

```text
Cost basis recovered → not new MAGI
```

## 3. Brokerage Unrealized Gain

Unrealized gain is the taxable growth inside taxable holdings.

When holdings are sold, part of the sale is assumed to be taxable gain.

```text
Gain portion sold → capital gain → MAGI
```

---

## Starting Example

Current rough brokerage picture:

```text
Total taxable brokerage/cash:   $540,000
Brokerage cash:                 $250,000
Taxable holdings cost basis:    $230,000
Taxable holdings gains:          $63,000
Taxable holdings value:         $293,000
```

The taxable holdings gain ratio is:

```text
gain_ratio = unrealized_gain / holdings_value
```

Using the example:

```text
gain_ratio = $63,000 / $293,000
           ≈ 21.5%
```

That means each dollar of taxable holdings sold is roughly:

```text
78.5% return of basis
21.5% taxable capital gain
```

---

## Simple Sale Rule

When brokerage funds are needed:

```text
1. Use brokerage cash first.
2. If brokerage cash is exhausted, sell taxable holdings.
3. Estimate capital gain from the sale using the current gain ratio.
```

Formula:

```text
holdings_value = brokerage_cost_basis + brokerage_unrealized_gain
brokerage_gain_ratio = brokerage_unrealized_gain / holdings_value
capital_gain_realized = holdings_sold * brokerage_gain_ratio
basis_used = holdings_sold - capital_gain_realized
```

If holdings value is zero, gain ratio is zero.

---

## MAGI Impact

Brokerage cash does not increase MAGI.

Brokerage holdings sales increase MAGI only by the estimated realized gain.

```text
Brokerage_MAGI_Income = capital_gain_realized
```

This brokerage MAGI income is then added to the other MAGI components:

```text
IRA draws
+ RMDs
+ Roth conversions
+ taxable Social Security
+ brokerage capital gains
+ other MAGI income, if modeled
- MAGI offsets, if modeled
= projected MAGI
```

---

## Roth Conversion Room

The planner should estimate MAGI before Roth conversion first.

```text
MAGI_Before_Conversion
= IRA draws
+ RMDs
+ taxable Social Security
+ brokerage capital gains
+ other MAGI income
- MAGI offsets
```

Then:

```text
Conversion_Room = Target_MAGI - MAGI_Before_Conversion
```

Then:

```text
Recommended_Roth_Conversion
= min(Conversion_Room, available IRA balance)
```

If conversion room is negative, recommended conversion is zero.

---

## What RetirePlan Does Not Do

RetirePlan does not need to model:

- individual lots
- exact sale dates
- specific securities sold
- wash sale rules
- tax-loss harvesting strategy
- dividend schedules
- current-year ACA reconciliation precision
- detailed qualified versus ordinary dividend handling

Those belong in the separate MAGI Tracker if needed.

---

## MAGI Tracker Boundary

The MAGI Tracker is the current-year detail tool.

It may help decide:

- which lots to sell
- when to sell
- whether to harvest losses
- how much gain has already been realized
- how much MAGI room remains this year

RetirePlan is the annual projection tool.

It should use simple brokerage buckets to estimate long-term consequences.

The tools may share summary numbers, but RetirePlan should not become the MAGI Tracker.

---

## Required Inputs

Minimum inputs for this model:

```text
brokerage_cash
brokerage_cost_basis
brokerage_unrealized_gain
```

Optional later inputs:

```text
other_magi_income
magi_offsets
```

Do not add optional inputs until they are needed.

---

## Required Outputs

Useful output fields:

```text
Brokerage_Cash
Brokerage_Cost_Basis
Brokerage_Unrealized_Gain
Brokerage_Gain_Ratio
Brokerage_Draw
Brokerage_Holdings_Sold
Brokerage_Basis_Used
Brokerage_Capital_Gains
Brokerage_MAGI_Income
```

These do not all need to be visible in the GUI.

They should be available for audit/export when implemented.

---

## Core Rule

The planner should remain simple enough to explain brokerage MAGI in one sentence:

```text
Brokerage cash creates no MAGI; selling taxable holdings creates gain based on the current gain ratio.
```

That is the model.


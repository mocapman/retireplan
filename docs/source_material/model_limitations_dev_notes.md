# Model Limitations Dev Notes

This is a development note, not an active project requirement.

## Purpose

RetirePlan is becoming useful for scenario comparison and tax-aware retirement planning, but it is not yet complete enough to trust blindly for final tax-sensitive decisions.

The tool should remain a liquid-money retirement planner, not a full net-worth planner.

## Scope Boundary

RetirePlan models liquid retirement money:

- taxable brokerage / cash
- Traditional IRA
- Roth IRA
- Social Security
- taxes
- MAGI
- ACA planning, once implemented
- RMDs
- drawdown timing
- survivor spending

RetirePlan does not currently include non-liquid assets in the core projection:

- primary residence
- collectibles
- personal property
- vehicles
- other saleable assets

The primary residence may be considered a long-term-care, emergency, or late-life reserve, but it should not be mixed into the normal annual drawdown engine.

Collectibles may eventually be modeled as optional cash events or external future liquidity, but they are not part of the recurring retirement engine.

## Current Known Gaps

### ACA Subsidy Modeling

ACA subsidy calculation is not complete.

MAGI can be tracked and projected, but the planner does not yet fully calculate annual ACA subsidy, repayment, or premium tax credit effects.

This is a major remaining gap because MAGI management is one of the core reasons for the planner.

### Capital Gains and Qualified Dividends

Federal tax treatment is simplified.

Brokerage capital gains are now included in MAGI/taxable income, but the model does not yet fully separate:

- long-term capital gains
- qualified dividends
- ordinary dividends
- interest
- ordinary income

This may overstate or distort federal tax in some scenarios.

### State Tax

State tax is currently intended as a simplified estimate:

```text
Estimated State Tax =
max(0, taxable income - estimated state deduction)
× estimated state tax rate



Use this as:

```text
docs/source_material/model_limitations_dev_notes.md
```

````markdown
# Model Limitations Dev Notes

This is a development note, not an active project requirement.

## Purpose

RetirePlan is becoming useful for scenario comparison and tax-aware retirement planning, but it is not yet complete enough to trust blindly for final tax-sensitive decisions.

The tool should remain a liquid-money retirement planner, not a full net-worth planner.

## Scope Boundary

RetirePlan models liquid retirement money:

- taxable brokerage / cash
- Traditional IRA
- Roth IRA
- Social Security
- taxes
- MAGI
- ACA planning, once implemented
- RMDs
- drawdown timing
- survivor spending

RetirePlan does not currently include non-liquid assets in the core projection:

- primary residence
- collectibles
- personal property
- vehicles
- other saleable assets

The primary residence may be considered a long-term-care, emergency, or late-life reserve, but it should not be mixed into the normal annual drawdown engine.

Collectibles may eventually be modeled as optional cash events or external future liquidity, but they are not part of the recurring retirement engine.

## Current Known Gaps

### ACA Subsidy Modeling

ACA subsidy calculation is not complete.

MAGI can be tracked and projected, but the planner does not yet fully calculate annual ACA subsidy, repayment, or premium tax credit effects.

This is a major remaining gap because MAGI management is one of the core reasons for the planner.

### Capital Gains and Qualified Dividends

Federal tax treatment is simplified.

Brokerage capital gains are now included in MAGI/taxable income, but the model does not yet fully separate:

- long-term capital gains
- qualified dividends
- ordinary dividends
- interest
- ordinary income

This may overstate or distort federal tax in some scenarios.

### State Tax

State tax is currently intended as a simplified estimate:

```text
Estimated State Tax =
max(0, taxable income - estimated state deduction)
× estimated state tax rate
````

This is good enough for planning, but it is not an Oregon tax return calculation.

It does not model:

* Oregon brackets
* Oregon credits
* exact Oregon deduction rules
* special Oregon adjustments

### Survivor Tax Assumptions

Survivor logic has improved, especially RMD continuation, but survivor-year tax behavior still needs review.

Important survivor questions:

* single filing tax brackets
* single standard deduction
* state deduction treatment
* survivor Social Security
* survivor spending percentage
* inherited/continued IRA treatment
* Roth preservation versus spending

### Roth Conversion Strategy

Roth conversions are modeled, but the strategy is still simplified.

The planner does not yet fully optimize:

* conversion amount by tax bracket
* ACA subsidy effect
* survivor tax risk
* RMD reduction
* Roth preservation
* current versus future tax tradeoffs

### Sequence of Returns

The planner uses assumed annual growth rates.

It does not yet model market volatility or bad timing, such as:

* early retirement market crash
* flat returns for several years
* large drawdowns during market weakness
* sequence-of-return risk

This is acceptable for scenario comparison, but not a full risk model.

## Proper Use

The current planner is useful for:

* comparing spending scenarios
* testing GoGo / SlowGo / NoGo assumptions
* seeing account depletion timing
* estimating tax direction
* comparing total taxes under different spend levels
* seeing Roth / IRA / brokerage interaction
* identifying years that need adjustment

The current planner should not be treated as:

* a tax return calculator
* a complete CFP-grade retirement plan
* a final Roth conversion calculator
* a precise ACA subsidy calculator
* a replacement for advisor/CPA review

## Red-Team Summary

The tool is no longer a toy. It is becoming a useful decision-support engine.

But before relying on it for real execution, the most important things to challenge are:

1. ACA subsidy calculation
2. capital gains / qualified dividend tax treatment
3. survivor-year tax assumptions
4. Roth conversion strategy
5. sequence-of-return risk
6. whether non-liquid reserves should remain outside the core model

The planner is good enough to guide discussion and expose tradeoffs.

It is not yet good enough to trust blindly for final tax-sensitive decisions.

# RetirePlan Project Contract

## Core Purpose

RetirePlan is a tax-management and retirement scenario tool.

Its primary purpose is to help answer two questions:

1. **How should money move through accounts over time to reduce unnecessary taxes?**
2. **Can the plan still fund the desired lifestyle under different spending, growth, tax, and survivor assumptions?**

The tool is not trying to perfectly predict the future. It is trying to make the major tax, spending, MAGI, ACA, account-balance, and survivor consequences visible enough to support real decisions.

The goal is not perfect precision.

The goal is a clear, auditable, manually verifiable decision-support engine.

---

## Primary Need 1: Tax-Managed Money Movement

The core of the planner is tax management.

The central question is:

> How do I move money through Cash, Brokerage, Roth IRA, Traditional IRA, Social Security, and RMDs at the right time so I minimize what I give to the IRS and Oregon?

The planner must clearly distinguish money by tax character:

| Money Source | Tax Role |
|---|---|
| Cash | Already taxed; generally does not create MAGI when spent |
| Brokerage principal | Usually already taxed; may create taxable gains when sold |
| Brokerage dividends | Taxable; may affect MAGI |
| Brokerage interest | Taxable; may affect MAGI |
| Brokerage capital gains | Taxable; may affect MAGI |
| Roth IRA | Generally tax-free if qualified; useful for low-tax spending support |
| Traditional IRA withdrawals | Taxable; affect MAGI and taxable income |
| Roth conversions | Taxable now; reduce future Traditional IRA/RMD exposure |
| Social Security | Cash inflow; may be partly taxable depending on other income |
| RMDs | Forced taxable Traditional IRA distributions later |

The projection exists because timing changes the tax result.

---

## Primary Need 2: Scenario Testing

The second core purpose is scenario evaluation.

The user must be able to change major assumptions and see whether the plan still works.

Examples:

| Change | Question Answered |
|---|---|
| GoGo years from 10 to 8 | Does reducing early high spending extend plan life? |
| Roth growth rate from 6% to 8% | Does better tax-free growth materially improve longevity? |
| Spending target | How much lifestyle can be supported? |
| MAGI target | What ACA/tax tradeoff is being chosen? |
| Roth conversion amount | How much tax should be paid now to reduce later risk? |
| Social Security start age | Does claiming earlier or later improve the plan? |
| Survivor spending | Does the surviving spouse remain secure? |

The tool should expose consequences, not pretend to know the future.

---

## Required Model Chain

The planner should be built from basic truths in a clear dependency chain:

```text
Seed Inputs
→ Known Law / Policy Values
→ Derived Annual Values
→ Taxable Income / MAGI
→ Taxes / ACA / RMD Effects
→ Required Draws
→ Account Balances
→ Final Viability
```

Every important number must be traceable.

No mystery math.

No hidden totals.

No calculation should exist only because the code says so.

---

## Major Outputs Must Be Auditable

Every major displayed result must have supporting values available for review, especially in CSV/export or diagnostic output.

Examples:

| Displayed Result | Supporting Diagnostic Values |
|---|---|
| Taxes Due | Federal tax, Oregon tax, taxable IRA income, taxable Social Security, taxable Roth conversion, taxable capital gains, taxable dividends, taxable interest |
| MAGI | IRA withdrawals, Roth conversions, taxable Social Security, capital gains, dividends, interest, deductions or adjustments if modeled |
| MAGI Guardrails | MAGI floor, target, ceiling, remaining room, status |
| Total Spend | Base spend, taxes, healthcare premiums if included, other modeled additions |
| Account Balances | Starting balance, draws, conversions, growth, RMDs, ending balance |
| Roth Conversion | MAGI room, tax impact, ACA impact, Traditional IRA balance effect, Roth balance effect |

The GUI may stay clean.

Diagnostic detail may be hidden by default, but it must be retrievable and exportable.

---

## Variable Discipline

Variables must be managed with strict discipline.

A new variable should not be created unless it is required.

A variable should not be renamed or reused until its actual meaning has been confirmed by usage.

Before changing or adding a variable, confirm:

| Requirement | Question |
|---|---|
| Source | Where does the value originate? |
| Unit | Dollars, percent, year, age, boolean, status, or other? |
| Timing | Monthly, annual, starting-year, current-year, projected-year, or lifetime? |
| Tax role | Taxable, non-taxable, MAGI-affecting, balance-only, or diagnostic? |
| Layer | Input, internal calculation, schema/output, GUI display, export field, or test fixture? |
| Dependencies | What values create it? |
| Consumers | What later calculations use it? |
| Necessity | Is this actually needed, or is it duplicating an existing concept? |

Variable meaning is determined by usage, not by name alone.

---

## Dependency Map Requirement

The project needs a variable and calculation dependency map.

The purpose is to prevent sidequests, circular logic, hidden coupling, and duplicate concepts.

The map should show how each major value is created and why it exists.

Starting dependency outline:

```text
target_spend_base
+ inflation_rate
+ spending phase rules
→ projected_base_spend

projected_base_spend
+ taxes_due
→ total_spend_needed

total_spend_needed
- social_security_cash_received
- available cash or account draws
→ amount_needed_from_accounts

amount_needed_from_accounts
+ draw strategy
+ MAGI room
+ taxable rules
→ brokerage_draw / roth_draw / ira_draw / roth_conversion

ira_draw
+ roth_conversion
+ taxable brokerage income
+ taxable social_security
→ MAGI / taxable_income

MAGI
+ MAGI guardrail values
→ MAGI remaining / MAGI status

taxable_income
+ federal brackets
+ Oregon brackets
→ taxes_due

draws
+ conversions
+ growth
+ RMDs
→ ending account balances

ending account balances
→ next year starting balances
```

This dependency map is a design tool, not decoration.

It should control development decisions.

---

## Known Values Versus Predictions

The planner will use both known values and unknowable assumptions.

Known or externally defined values may include:

- federal tax brackets
- Oregon tax brackets
- standard deduction
- ACA rules or subsidy tables/formulas
- RMD divisors
- Social Security claiming assumptions
- current account balances
- current tax law assumptions

Unknowable assumptions may include:

- future market returns
- future inflation
- future healthcare costs
- future tax-law changes
- future ACA policy changes
- actual lifespan
- survivor needs
- timing of major spending events

The tool must not pretend these assumptions are facts.

It should make assumptions visible and easy to change.

---

## Feature Admission Rule

Every feature must justify its complexity.

A feature belongs in the core planner only if it materially improves one of the two primary needs:

1. tax-managed money movement
2. scenario testing for spending and plan viability

Before adding a feature, answer:

| Test | Question |
|---|---|
| Decision Test | What real decision does this improve? |
| Tax Test | Does this affect IRS/Oregon taxes, MAGI, ACA, RMDs, or account draw timing? |
| Scenario Test | Does this improve meaningful spending or longevity analysis? |
| Audit Test | Can the result be traced and recalculated? |
| Complexity Test | Is the financial value greater than the added complexity and uncertainty? |

If the answer is weak, the feature should be rejected or moved to a side calculator.

---

## Core Engine Versus Side Calculators

The core engine should include recurring annual projection logic that affects the main plan.

Likely core engine concepts:

- annual spending phases
- account balances
- draw sequencing
- taxable income
- MAGI
- ACA subsidy impact
- Roth conversions
- Traditional IRA withdrawals
- RMDs
- Social Security
- federal and Oregon taxes
- survivor scenario handling

Likely side calculator concepts:

- one-off capital gain experiments
- ACA repayment estimates
- Roth conversion what-if comparisons
- tax-loss harvesting experiments
- brokerage tax-lot detail
- highly specific intrayear timing questions

Side calculators may be useful, but they should not destabilize the annual projection engine.

---

## Development Workflow

Development should proceed in stable plateaus.

Each change should follow this order:

1. Define the requirement.
2. Identify the decision the change supports.
3. Inspect the actual source files before editing.
4. Confirm variable meaning by usage, not name.
5. Make the smallest useful change.
6. Avoid unrelated cleanup.
7. Preserve existing behavior unless intentionally changing it.
8. Expose diagnostic values when adding or changing major outputs.
9. Run the full test suite.
10. Summarize files changed, purpose, test command, test result, warnings, and suggested commit message.

Default test command:

```powershell
python -m pytest
```

Do not commit until the plateau is stable and understood.

---

## Final Truth Being Cornered

The planner is trying to corner this final answer:

> Given taxable money, tax-free money, tax-deferred money, spending needs, health-insurance constraints, tax law, and best-guess future assumptions, what is the least-wasteful way to fund life?

The practical output should help decide:

```text
Spend this much.
Pull this much from here.
Convert this much.
Avoid crossing this MAGI/tax line.
Expect this tax cost.
Preserve this much future flexibility.
Here is how long the plan survives.
Here is what breaks the plan.
```

That is the project.

Not generic retirement advice.

Not perfect forecasting.

Not tax trivia.

Not a sidequest.

A clear, testable, tax-aware planning engine.


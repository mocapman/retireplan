from __future__ import annotations

from typing import Dict, Any


class ConfigManager:
    """Handles configuration conversion between GUI and engine formats"""

    @staticmethod
    def config_to_dict(cfg) -> Dict[str, Any]:
        """Convert configuration object to dictionary for the input panel"""
        return {
            "birth_year_person1": cfg.birth_year_person1,
            "birth_year_person2": cfg.birth_year_person2,
            "final_age_person1": cfg.final_age_person1,
            "final_age_person2": cfg.final_age_person2,
            "filing_status": cfg.filing_status,
            "balances": {
                "brokerage_cash": cfg.brokerage_cash,
                "brokerage_cost_basis": cfg.brokerage_cost_basis,
                "brokerage_unrealized_gain": cfg.brokerage_unrealized_gain,
                "roth": cfg.balances_roth,
                "ira": cfg.balances_ira,
            },
            "spending": {
                "start_year": cfg.start_year,
                "year1_spend": cfg.year1_spend,
                "year1_brokerage_draw": cfg.year1_brokerage_draw,
                "year1_ira_draw": cfg.year1_ira_draw,
                "year1_roth_draw": cfg.year1_roth_draw,
                "year1_magi_floor": cfg.year1_magi_floor,
                "year1_magi_target": cfg.year1_magi_target,
                "year1_magi_ceiling": cfg.year1_magi_ceiling,
                "year1_extra_magi_income": cfg.year1_extra_magi_income,
                "year1_magi_loss_offset": cfg.year1_magi_loss_offset,
                "year1_planned_roth_conversion": cfg.year1_planned_roth_conversion,
                "year1_magi_income": cfg.year1_magi_income,
                "year1_magi_losses": cfg.year1_magi_losses,
                "year1_roth_conversion": cfg.year1_roth_conversion,
                "year1_income_to_date": cfg.year1_income_to_date,
                "year1_projected_income": cfg.year1_projected_income,
                "year1_capital_gains_to_date": cfg.year1_capital_gains_to_date,
                "year1_projected_capital_gains": (
                    cfg.year1_projected_capital_gains
                ),
                "year1_capital_losses_to_date": cfg.year1_capital_losses_to_date,
                "year1_projected_capital_losses": (
                    cfg.year1_projected_capital_losses
                ),
                "aca_magi_floor": cfg.aca_magi_floor,
                "aca_magi_target": cfg.aca_magi_target,
                "aca_magi_ceiling": cfg.aca_magi_ceiling,
                "aca_extra_magi_income": cfg.aca_extra_magi_income,
                "aca_magi_loss_offset": cfg.aca_magi_loss_offset,
                "aca_planned_roth_conversion": cfg.aca_planned_roth_conversion,
                "aca_annual_magi_income": cfg.aca_annual_magi_income,
                "aca_annual_magi_loss": cfg.aca_annual_magi_loss,
                "aca_annual_roth_conversion": cfg.aca_annual_roth_conversion,
                "medicare_magi_floor": cfg.medicare_magi_floor,
                "medicare_magi_target": cfg.medicare_magi_target,
                "medicare_magi_ceiling": cfg.medicare_magi_ceiling,
                "medicare_extra_magi_income": cfg.medicare_extra_magi_income,
                "medicare_magi_loss_offset": cfg.medicare_magi_loss_offset,
                "medicare_planned_roth_conversion": (
                    cfg.medicare_planned_roth_conversion
                ),
                "medicare_annual_magi_income": cfg.medicare_annual_magi_income,
                "medicare_annual_magi_loss": cfg.medicare_annual_magi_loss,
                "medicare_annual_roth_conversion": (
                    cfg.medicare_annual_roth_conversion
                ),
                "magi_income_ytd": cfg.magi_income_ytd,
                "magi_income_projected": cfg.magi_income_projected,
                "magi_income_years": cfg.magi_income_years,
                "magi_gains_ytd": cfg.magi_gains_ytd,
                "magi_gains_projected": cfg.magi_gains_projected,
                "magi_gains_years": cfg.magi_gains_years,
                "magi_losses_ytd": cfg.magi_losses_ytd,
                "magi_losses_projected": cfg.magi_losses_projected,
                "magi_losses_years": cfg.magi_losses_years,
                "magi_conversions_ytd": cfg.magi_conversions_ytd,
                "magi_conversions_projected": cfg.magi_conversions_projected,
                "magi_conversions_years": cfg.magi_conversions_years,
                "target_spend": cfg.target_spend,
                "gogo_percent": cfg.gogo_percent,
                "slow_percent": cfg.slow_percent,
                "nogo_percent": cfg.nogo_percent,
                "gogo_years": cfg.gogo_years,
                "slow_years": cfg.slow_years,
                "survivor_percent": cfg.survivor_percent,
            },
            "social_security": {
                "person1_start_age": cfg.ss_person1_start_age,
                "person1_annual_at_start": cfg.ss_person1_annual_at_start,
                "ss_person1_monthly_by_start_age": (
                    cfg.ss_person1_monthly_by_start_age
                ),
                "person2_start_age": cfg.ss_person2_start_age,
                "person2_annual_at_start": cfg.ss_person2_annual_at_start,
                "ss_person2_monthly_by_start_age": (
                    cfg.ss_person2_monthly_by_start_age
                ),
            },
            "rates": {
                "inflation": cfg.inflation,
                "brokerage_growth": cfg.brokerage_growth,
                "roth_growth": cfg.roth_growth,
                "ira_growth": cfg.ira_growth,
            },
            "tax_health": {
                "magi_target_base": cfg.magi_target_base,
                "standard_deduction_base": cfg.standard_deduction_base,
                "estimated_state_deduction": cfg.estimated_state_deduction,
                "estimated_state_tax_rate": cfg.estimated_state_tax_rate,
                "rmd_start_age": cfg.rmd_start_age,
                "aca_end_age": cfg.aca_end_age,
                "aca_full_premium_monthly": cfg.aca_full_premium_monthly,
                "aca_premium_by_magi": cfg.aca_premium_by_magi,
                "magi_floor_base": cfg.magi_floor_base,
                "magi_ceiling_base": cfg.magi_ceiling_base,
                "medicare_magi_ceiling_base": cfg.medicare_magi_ceiling_base,
            },
            "draw_order": cfg.draw_order,
        }

    @staticmethod
    def update_config_from_dict(cfg, config_dict: Dict[str, Any]):
        """Update the configuration object from a dictionary"""
        for key, value in config_dict.items():
            if key == "balances":
                if (
                    "brokerage_cash" not in value
                    and "brokerage_cost_basis" not in value
                    and "brokerage_unrealized_gain" not in value
                ):
                    cfg.brokerage_cash = value.get("brokerage", 0)
                    cfg.brokerage_cost_basis = 0
                    cfg.brokerage_unrealized_gain = 0
                else:
                    cfg.brokerage_cash = value.get("brokerage_cash", 0)
                    cfg.brokerage_cost_basis = value.get("brokerage_cost_basis", 0)
                    cfg.brokerage_unrealized_gain = value.get(
                        "brokerage_unrealized_gain", 0
                    )
                cfg.balances_brokerage = (
                    cfg.brokerage_cash
                    + cfg.brokerage_cost_basis
                    + cfg.brokerage_unrealized_gain
                )
                cfg.balances_roth = value["roth"]
                cfg.balances_ira = value["ira"]
            elif key == "spending":
                for k, v in value.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
            elif key == "social_security":
                for k, v in value.items():
                    if k == "person1_start_age":
                        cfg.ss_person1_start_age = v
                    elif k == "person1_annual_at_start":
                        cfg.ss_person1_annual_at_start = v
                    elif k == "ss_person1_monthly_by_start_age":
                        cfg.ss_person1_monthly_by_start_age = v
                    elif k == "person2_start_age":
                        cfg.ss_person2_start_age = v
                    elif k == "person2_annual_at_start":
                        cfg.ss_person2_annual_at_start = v
                    elif k == "ss_person2_monthly_by_start_age":
                        cfg.ss_person2_monthly_by_start_age = v
            elif key == "rates":
                for k, v in value.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
            elif key == "tax_health":
                for k, v in value.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
            elif hasattr(cfg, key):
                setattr(cfg, key, value)

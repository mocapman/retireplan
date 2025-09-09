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
                "brokerage": cfg.balances_brokerage,
                "roth": cfg.balances_roth,
                "ira": cfg.balances_ira,
            },
            "spending": {
                "start_year": cfg.start_year,
                "year1_spend": cfg.year1_spend,
                "year1_cash_events": cfg.year1_cash_events,
                "year1_brokerage_draw": cfg.year1_brokerage_draw,
                "year1_ira_draw": cfg.year1_ira_draw,
                "year1_roth_draw": cfg.year1_roth_draw,
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
                "person2_start_age": cfg.ss_person2_start_age,
                "person2_annual_at_start": cfg.ss_person2_annual_at_start,
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
                "rmd_start_age": cfg.rmd_start_age,
                "aca_end_age": cfg.aca_end_age,
                "aca_subsidy_annual": getattr(cfg, "aca_subsidy_annual", None),
            },
            "draw_order": cfg.draw_order,
        }

    @staticmethod
    def update_config_from_dict(cfg, config_dict: Dict[str, Any]):
        """Update the configuration object from a dictionary"""
        for key, value in config_dict.items():
            if key == "balances":
                cfg.balances_brokerage = value["brokerage"]
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
                    elif k == "person2_start_age":
                        cfg.ss_person2_start_age = v
                    elif k == "person2_annual_at_start":
                        cfg.ss_person2_annual_at_start = v
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

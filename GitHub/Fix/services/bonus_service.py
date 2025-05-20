import json
from datetime import datetime
from typing import Callable, Dict, List, Any
from fastapi import HTTPException, status
from config import RULES_FILE
from http_service.schemas import bonus_schemas  # Import your Pydantic schema


def load_rules() -> Dict[str, Any]:
    """
    Загружает правила начисления бонусов из JSON-файла.
    """
    try:
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        default_rules = {
            "base_rate": {"rate": 1, "per_amount": 10, "order": 1},
            "holiday_bonus": {"multiplier": 2, "applies_on": ["Sat", "Sun"], "order": 2},
            "vip_boost": {"multiplier": 1.4, "order": 3},
        }
        save_rules(default_rules)
        return default_rules


def save_rules(rules: Dict[str, Any]) -> None:
    """
    Сохраняет правила начисления бонусов в JSON-файл.
    """
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)


def apply_base_rate(amount: float, rule_config: Dict[str, Any]) -> float:
    """
    Применяет базовое правило начисления бонусов.
    """
    return (amount // rule_config["per_amount"]) * rule_config["rate"]


def apply_holiday_bonus(base_bonus: float, timestamp_str: str, rule_config: Dict[str, Any]) -> float:
    """
    Применяет бонус за выходные/праздничные дни.
    """
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    if timestamp.strftime("%a") in rule_config["applies_on"]:
        return base_bonus * rule_config["multiplier"]
    return base_bonus


def apply_vip_boost(bonus: float, customer_status: str, rule_config: Dict[str, Any]) -> float:
    """
    Применяет бонус для VIP-клиентов.
    """
    if customer_status.lower() == "vip":
        return bonus * rule_config["multiplier"]
    return bonus


RuleApplier = Callable[[float, Any, Dict[str, Any]], float]

rule_appliers: Dict[str, RuleApplier] = {
    "base_rate": apply_base_rate,
    "holiday_bonus": apply_holiday_bonus,
    "vip_boost": apply_vip_boost,
}


def calculate_bonus(request: bonus_schemas.BonusRequest) -> dict:  # Use the Pydantic model
    """
    Вычисляет бонусы на основе заданных правил.
    """
    try:
        rules = load_rules()
        amount = request.transaction_amount  # Access attributes from the Pydantic model
        print(f"Type of amount: {type(amount)}, value: {amount}")
        timestamp_str = request.timestamp.isoformat() # Convert datetime to string
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        customer_status = request.customer_status
        applied_rules: List[Dict[str, Any]] = []
        total_bonus = 0.0

        sorted_rules = sorted(rules.items(), key=lambda item: item[1]["order"])

        for rule_name, rule_config in sorted_rules:
            if rule_name in rule_appliers:
                if rule_name == "base_rate":
                    total_bonus = rule_appliers[rule_name](float(amount), rule_config)
                    applied_rules.append({"rule": rule_name, "bonus": int(total_bonus)})
                elif rule_name == "holiday_bonus":
                    new_bonus = rule_appliers[rule_name](total_bonus, timestamp_str, rule_config)
                    if new_bonus > total_bonus:
                        applied_rules.append({"rule": rule_name, "bonus": int(new_bonus - total_bonus)})
                        total_bonus = new_bonus
                elif rule_name == "vip_boost":
                    new_bonus = rule_appliers[rule_name](total_bonus, customer_status, rule_config)
                    applied_rules.append({"rule": rule_name, "bonus": int(new_bonus - total_bonus)})
                    total_bonus = new_bonus
            else:
                print(f"Warning: Rule '{rule_name}' has no defined applier function.")

        return {"total_bonus": int(total_bonus), "applied_rules": applied_rules}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
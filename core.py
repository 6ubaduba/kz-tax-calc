from typing import Dict, Any

def calculate_deal(
    revenue_gross: float,
    expense_gross: float,
    expense_type: str = "with_vat",  # "with_vat", "no_vat", "no_docs"
    vat_rate: float = 0.12           # 0.12 (12%) или 0.16 (16%)
) -> Dict[str, Any]:
    # 1. Извлечение НДС из выручки (считаем, что сумма от клиента включает НДС)
    # Формула извлечения: Gross * Rate / (1 + Rate)
    vat_factor = vat_rate / (1.0 + vat_rate)
    vat_output = revenue_gross * vat_factor
    revenue_net = revenue_gross - vat_output

    # 2. Обработка расхода в зависимости от сценария
    if expense_type == "with_vat":
        # С НДС: есть зачет по НДС и есть вычет по ИПН (на сумму без НДС)
        vat_input = expense_gross * vat_factor
        expense_net = expense_gross - vat_input
        deductible_expense = expense_net
        expense_desc = f"С документами и НДС ({int(vat_rate * 100)}%)"
    elif expense_type == "no_vat":
        # Без НДС: зачета по НДС нет (0), но вся сумма идет на вычет по ИПН
        vat_input = 0.0
        expense_net = expense_gross
        deductible_expense = expense_gross
        expense_desc = "Официально, но без НДС (только вычет по ИПН)"
    else:
        # Без документов: ни зачета по НДС, ни вычета по ИПН
        vat_input = 0.0
        expense_net = expense_gross
        deductible_expense = 0.0
        expense_desc = "Без закрывающих документов (расход не подтвержден)"

    # 3. Расчет НДС к уплате
    vat_payable = max(0.0, vat_output - vat_input)

    # 4. Расчет ИПН (10% от налогооблагаемой прибыли: Доход без НДС - Подтвержденный расход)
    taxable_profit = max(0.0, revenue_net - deductible_expense)
    ipn_payable = taxable_profit * 0.10

    # 5. Итоги по налогам и чистая прибыль
    total_tax = vat_payable + ipn_payable
    net_profit = revenue_gross - expense_gross - total_tax
    margin_percent = (net_profit / revenue_gross * 100) if revenue_gross > 0 else 0.0

    return {
        "Сценарий расхода": expense_desc,
        "Ставка НДС": f"{int(vat_rate * 100)}%",
        "НДС": {
            "НДС с реализации": round(vat_output, 2),
            "НДС в зачет": round(vat_input, 2),
            "НДС к уплате": round(vat_payable, 2)
        },
        "ИПН": {
            "Доход без НДС": round(revenue_net, 2),
            "Расход, принятый на вычет": round(deductible_expense, 2),
            "Налогооблагаемая прибыль": round(taxable_profit, 2),
            "ИПН (10%) к уплате": round(ipn_payable, 2)
        },
        "Итого налогов (НДС + ИПН)": round(total_tax, 2),
        "Чистая прибыль (на руки)": round(net_profit, 2),
        "Маржинальность от оборота": f"{round(margin_percent, 1)}%",
        "Сверка по кэшу": f"{round(revenue_gross, 2)} - {round(expense_gross, 2)} - {round(total_tax, 2)} = {round(net_profit, 2)} ₸"
    }

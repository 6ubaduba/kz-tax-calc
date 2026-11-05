import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()

class DealRequest(BaseModel):
    revenue: float
    expense: float = 0.0
    expense_category: str = "with_vat"  # with_vat, without_vat, no_docs
    vat_rate: float = 12.0

@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse(status_code=404)

@app.get("/", response_class=HTMLResponse)
def get_index():
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Расчет сделки (ИП на ОУР с НДС)</title>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Налоги РК">
    <link rel="apple-touch-icon" href="/logo.png">
    <link rel="icon" type="image/png" href="/logo.png">

    <style>
        :root {
            --bg: #0b132b;
            --card-bg: #ffffff;
            --accent: #2563eb;
            --text: #1c1c1e;
            --subtext: #8e8e93;
            --border: #e5e5ea;
            --red: #dc2626;
            --green: #16a34a;
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: var(--bg);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: var(--text);
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }

        .card {
            width: 100%;
            max-width: 420px;
            background: var(--card-bg);
            border-radius: 20px;
            padding: 18px 20px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            transition: all 0.25s ease;
        }

        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
            transition: all 0.2s ease;
        }

        .logo {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            object-fit: cover;
            transition: all 0.2s ease;
        }

        .header h1 {
            font-size: 17px;
            font-weight: 700;
            margin: 0;
            color: var(--text);
        }

        .inputs-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: all 0.2s ease;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .label-row {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        label {
            font-size: 12px;
            font-weight: 600;
            color: #3a3a3c;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .tooltip-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: #e5e5ea;
            color: #636366;
            font-size: 11px;
            font-weight: bold;
            cursor: pointer;
            position: relative;
            user-select: none;
        }

        .tooltip-icon:hover {
            background-color: var(--accent);
            color: #ffffff;
        }

        .tooltip-text {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            width: 220px;
            background-color: #1f2937;
            color: #ffffff;
            font-size: 11px;
            line-height: 1.35;
            font-weight: 400;
            padding: 8px 10px;
            border-radius: 8px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            z-index: 100;
            pointer-events: none;
            transition: opacity 0.2s ease, visibility 0.2s ease;
        }

        .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #1f2937 transparent transparent transparent;
        }

        .tooltip-icon:hover .tooltip-text,
        .tooltip-icon.active .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

        input, select {
            width: 100%;
            height: 42px;
            padding: 0 12px;
            font-size: 15px;
            border: 1.5px solid #d1d1d6;
            border-radius: 10px;
            background-color: #f9f9fb;
            outline: none;
            transition: all 0.2s ease;
        }

        input:focus, select:focus {
            border-color: var(--accent);
            background-color: #ffffff;
        }

        .row-group {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 10px;
        }

        .btn {
            width: 100%;
            height: 44px;
            background-color: var(--accent);
            color: white;
            border: none;
            font-size: 15px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            margin-top: 12px;
            transition: all 0.2s ease;
        }

        .btn:active {
            opacity: 0.85;
        }

        .results {
            margin-top: 10px;
            border-top: 1px solid var(--border);
            padding-top: 10px;
            display: none;
            animation: fadeIn 0.25s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .res-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 13px;
            color: #3a3a3c;
        }

        .res-row.total {
            font-size: 15px;
            font-weight: 700;
            border-top: 1px dashed var(--border);
            margin-top: 4px;
            padding-top: 6px;
            color: var(--text);
        }

        .val-tax { color: var(--red); font-weight: 600; }
        .val-clean { color: var(--green); font-weight: 700; }

        .compact-mode .header {
            margin-bottom: 6px;
            padding-bottom: 6px;
        }
        .compact-mode .logo {
            width: 30px;
            height: 30px;
            border-radius: 8px;
        }
        .compact-mode .header h1 {
            font-size: 14px;
        }
        .compact-mode .inputs-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }
        .compact-mode .row-group {
            grid-column: span 2;
            gap: 6px;
        }
        .compact-mode label {
            font-size: 10px;
        }
        .compact-mode input, .compact-mode select {
            height: 32px;
            font-size: 12px;
            padding: 0 8px;
            border-radius: 8px;
        }
        .compact-mode .btn {
            height: 36px;
            font-size: 13px;
            margin-top: 8px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="card" id="mainCard">
        <div class="header">
            <img src="/logo.png" alt="Лого" class="logo">
            <h1>Расчет сделки (ИП на ОУР с НДС)</h1>
        </div>

        <div class="inputs-container">
            <div class="input-group">
                <div class="label-row">
                    <label>Сумма от клиента:</label>
                    <span class="tooltip-icon" onclick="toggleTooltip(event, this)">ⓘ
                        <span class="tooltip-text">Полная сумма выставленного счета или полученной оплаты от заказчика с учетом НДС.</span>
                    </span>
                </div>
                <input type="number" id="revenue" placeholder="500000" inputmode="numeric">
            </div>

            <div class="input-group">
                <div class="label-row">
                    <label>Расход по сделке:</label>
                    <span class="tooltip-icon" onclick="toggleTooltip(event, this)">ⓘ
                        <span class="tooltip-text">Фактическая сумма оплаты поставщику, субподрядчику или затраты на товар/услугу.</span>
                    </span>
                </div>
                <input type="number" id="expense" placeholder="300000" inputmode="numeric">
            </div>

            <div class="row-group">
                <div class="input-group">
                    <div class="label-row">
                        <label>Категория расхода:</label>
                        <span class="tooltip-icon" onclick="toggleTooltip(event, this)">ⓘ
                            <span class="tooltip-text"><b>В орган / с НДС:</b> дает зачет по НДС и вычет по ИПН.<br><b>Без НДС:</b> только вычет по ИПН.<br><b>Без документов:</b> не уменьшает налоги.</span>
                        </span>
                    </div>
                    <select id="expense_cat">
                        <option value="with_vat">В орган / с НДС</option>
                        <option value="without_vat">Без НДС (с актами)</option>
                        <option value="no_docs">Без документов</option>
                    </select>
                </div>

                <div class="input

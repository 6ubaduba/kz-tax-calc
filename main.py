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
            font-

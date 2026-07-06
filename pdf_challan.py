import os
from datetime import datetime
from xhtml2pdf import pisa

CHALLAN_FOLDER = "challans"


def safe_folder_name(name):
    cleaned = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))
    return cleaned.strip().replace(" ", "_")


def build_challan_html(company_name, challan_number, date_str, po_no, items):
    total_takkas = sum(item.get('takka_count', 0) or 0 for item in items)
    total_qty = sum(item.get('quantity', 0) or 0 for item in items)

    rows_html = ""
    for i, item in enumerate(items, start=1):
        raw_list = str(item.get('takka_list', '') or '')
        takka_values = [v.strip() for v in raw_list.split(',') if v.strip() and v.strip() != '-']

        takka_rows = ""
        for j in range(0, len(takka_values), 4):
            chunk = takka_values[j:j + 4]
            cells = "".join(f'<td class="takka-box">{v}</td>' for v in chunk)
            takka_rows += f"<tr>{cells}</tr>"
        if not takka_rows:
            takka_rows = '<tr><td class="takka-box">-</td></tr>'

        rows_html += f"""
        <tr>
            <td class="sr">{i}</td>
            <td class="fabric-name">{item['fabric_name']}</td>
            <td class="size">{item['size']}</td>
            <td class="takka-cell">
                <div class="takka-label">TOTAL TAKKAS: {item.get('takka_count', 0)}</div>
                <table class="takka-grid">{takka_rows}</table>
            </td>
            <td class="qty">{item['quantity']}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica; font-size: 11px; color: #1E2A44; }}
        .header-table {{ width: 100%; margin-bottom: 8px; }}
        .header-table td {{ vertical-align: top; }}
        .company-name {{ font-size: 22px; font-weight: bold; color: #1E2A44; }}
        .tagline {{ font-size: 11px; color: #C08A1E; font-weight: bold; letter-spacing: 1px; }}
        .owner-info {{ text-align: right; font-size: 10px; color: #5B6B7F; }}
        .owner-info b {{ color: #1E2A44; font-size: 11px; }}
        .title-bar {{ background-color: #1E2A44; color: #FFFFFF; text-align: center; font-size: 14px; font-weight: bold; letter-spacing: 2px; padding: 7px; margin-bottom: 10px; border-bottom: 3px solid #D9A521; }}
        .meta-table {{ width: 100%; margin-bottom: 8px; }}
        .meta-table td {{ vertical-align: top; width: 50%; padding: 6px 8px; font-size: 10px; }}
        .box-label {{ font-size: 9.5px; color: #C08A1E; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 5px; }}
        .party-box {{ background-color: #EAF1F8; padding: 7px 8px; border-radius: 4px; border-left: 3px solid #1E2A44; }}
        .party-name {{ font-size: 12px; font-weight: bold; color: #1E2A44; }}
        table.items {{ width: 100%; border-collapse: collapse; }}
        table.items th {{ background-color: #1E2A44; color: #FFFFFF; padding: 7px 6px; font-size: 9.5px; border: 1px solid #1E2A44; text-align: left; }}
        table.items td {{ padding: 8px 6px; font-size: 10px; border: 1px solid #D7DEE8; vertical-align: top; }}
        td.sr {{ text-align: center; color: #5B6B7F; }}
        td.fabric-name {{ font-weight: bold; color: #1E2A44; }}
        td.qty {{ text-align: right; font-weight: bold; white-space: nowrap; color: #1E2A44; }}
        .takka-label {{ font-size: 9px; color: #1E2A44; font-weight: bold; margin-bottom: 4px; }}
        table.takka-grid {{ border-collapse: collapse; }}
        table.takka-grid td.takka-box {{ border: 1px solid #D7DEE8; background-color: #F5F8FB; padding: 4px 8px; font-size: 9.5px; text-align: center; color: #3B6EA5; }}
        .summary-row td {{ background-color: #FBF3E0; font-weight: bold; border: 1px solid #E8D6A0; padding: 9px 6px; font-size: 10.5px; white-space: nowrap; }}
        .summary-label {{ color: #5B6B7F; }}
        .takka-total-summary {{ color: #C08A1E; }}
        .signature-label {{ font-size: 10px; color: #5B6B7F; }}
        .for-company {{ color: #1E2A44; }}
        .page-frame {{ border: 1px solid #D7DEE8; border-radius: 6px; padding: 14px 16px; }}
        .logo-img {{ border-radius: 50%; }}
    </style>
    </head>
    <body>
    <div class="page-frame">
        <div class="title-bar">DELIVERY CHALLAN</div>

        <table class="header-table">
            <tr>
                <td style="width:15%;">
                    <img class="logo-img" src="static/logo.png" width="60" height="60"/>
                </td>
                <td style="width:55%;">
                    <span class="company-name">KRUPALU CREATION</span><br/>
                    <span class="tagline">DIGITAL PRINTING</span>
                </td>
                <td class="owner-info">
                    <b>Sunny Patel</b><br/>
                    +91 74055 97333<br/>
                    info@krupalucreation.com
                </td>
            </tr>
        </table>

        <table class="meta-table">
            <tr>
                <td>
                    <div class="box-label">DELIVER TO / PARTY DETAILS</div>
                    <div class="party-box">
                        <div class="party-name">{company_name}</div>
                    </div>
                </td>
                <td>
                    <div class="box-label">CHALLAN DETAILS</div>
                    Challan No: <b>{challan_number}</b><br/>
                    Date: <b>{date_str}</b><br/>
                    PO No: <b>{po_no}</b>
                </td>
            </tr>
        </table>

        <table class="items">
            <tr>
                <th style="width:6%;">SR.<br/>NO.</th>
                <th style="width:20%;">FABRIC NAME</th>
                <th style="width:10%;">SIZE</th>
                <th style="width:50%;">TAKKA DETAILS (METERS BREAKDOWN)</th>
                <th style="width:14%; text-align:right;">TOTAL<br/>QTY (M)</th>
            </tr>
            {rows_html}
            <tr class="summary-row">
                <td colspan="3"></td>
                <td colspan="2"><span class="summary-label">TOTAL SUMMARY:</span> <span class="takka-total-summary">Total Takkas: {total_takkas}</span></td>
            </tr>
        </table>

        <table style="width:100%; margin-top:16px;">
            <tr>
                <td style="width:50%;">Received in good condition, By ______________</td>
                <td style="width:50%; text-align:right;">
                    <b class="for-company">For, Krupalu Creation</b><br/><br/>
                    <img src="static/signature.png" width="110"/><br/>
                    <span class="signature-label">Authorized Signature</span>
                </td>
            </tr>
        </table>

        <div style="margin-top:20px; padding-top:8px; border-top:1px dashed #D7DEE8; font-size:9px; color:#5B6B7F;">
            <b>Terms &amp; Conditions:</b><br/>
            1. Goods once delivered will not be taken back.<br/>
            2. Check delivery immediately. Any discrepancy should be reported within 24 hours.
        </div>
    </div>
    </body>
    </html>
    """
    return html


def generate_challan_pdf(company_name, challan_number, date_str, po_no, items):
    month_folder = datetime.now().strftime("%Y-%m")
    folder_path = os.path.join(CHALLAN_FOLDER, safe_folder_name(company_name), month_folder)
    os.makedirs(folder_path, exist_ok=True)

    filename = safe_folder_name(challan_number) + ".pdf"
    filepath = os.path.join(folder_path, filename)

    html = build_challan_html(company_name, challan_number, date_str, po_no, items)

    with open(filepath, "wb") as f:
        pisa.CreatePDF(html, dest=f)

    return filepath

def generate_statement_pdf(company_name, period_label, orders, total_given, total_delivered):
    rows_html = ""
    for i, o in enumerate(orders, start=1):
        rows_html += f"""
        <tr>
            <td>{i}</td>
            <td>{o['fabric_name']}</td>
            <td>{o['date_received']}</td>
            <td>{o['inward_challan_number']}</td>
            <td align="right">{o['meters_given']}</td>
            <td align="right">{o['delivered']}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica; font-size: 11px; color: #1E2A44; }}
        h2 {{ text-align: center; letter-spacing: 2px; font-size: 13px; color: #5B6B7F; }}
        .company {{ text-align: center; font-size: 22px; font-weight: bold; margin: 0; }}
        .tagline {{ text-align: center; font-size: 11px; color: #5B6B7F; margin: 2px 0 10px; }}
        table.summary {{ width: 100%; margin-bottom: 10px; }}
        table.summary td {{ font-size: 11px; padding: 4px 0; }}
        table.items {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        table.items th {{ background-color: #1E2A44; color: white; padding: 6px; font-size: 10px; border: 1px solid #1E2A44; }}
        table.items td {{ padding: 6px; font-size: 10px; border: 1px solid #D3DBE5; }}
    </style>
    </head>
    <body>
        <h2>PARTY STATEMENT</h2>
        <p class="company">Krupalu Creation</p>
        <p class="tagline">Digital Printing</p>
        <hr>
        <table class="summary">
            <tr>
                <td>Party: <b>{company_name}</b></td>
                <td>Period: <b>{period_label}</b></td>
            </tr>
            <tr>
                <td>Total given: <b>{total_given} m</b></td>
                <td>Total delivered: <b>{total_delivered} m</b></td>
            </tr>
        </table>
        <table class="items">
            <tr>
                <th>Sr</th>
                <th>Fabric</th>
                <th>Date</th>
                <th>Challan</th>
                <th>Given</th>
                <th>Delivered</th>
            </tr>
            {rows_html}
        </table>
        <br/>
        <table style="width:100%; margin-top:20px;">
            <tr>
                <td></td>
                <td align="right">
                    <img src="static/signature.png" width="110"/><br/>
                    <span style="font-size:10px; color:#5B6B7F;">Authorized Signature</span>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    folder_path = os.path.join("statements", safe_folder_name(company_name))
    os.makedirs(folder_path, exist_ok=True)
    filename = f"statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(folder_path, filename)

    with open(filepath, "wb") as f:
        pisa.CreatePDF(html, dest=f)

    return filepath, filename
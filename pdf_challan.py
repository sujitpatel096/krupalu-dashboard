import os
from datetime import datetime
from xhtml2pdf import pisa

CHALLAN_FOLDER = "challans"


def safe_folder_name(name):
    cleaned = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))
    return cleaned.strip().replace(" ", "_")


def build_challan_html(company_name, challan_number, date_str, po_no, items):
    rows_html = ""
    for i, item in enumerate(items, start=1):
        rows_html += f"""
        <tr>
            <td>{i}</td>
            <td>{item['fabric_name']}</td>
            <td align="center">{item['size']}</td>
            <td>{item['takka_list']}</td>
            <td align="center">{item.get('takka_count', '-')}</td>
            <td align="right"><b>{item['quantity']}</b></td>
        </tr>
        """

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica; font-size: 11px; color: #1E2A44; }}
        h2 {{ text-align: center; letter-spacing: 2px; font-size: 13px; color: #5B6B7F; }}
        .company {{ text-align: center; font-size: 22px; font-weight: bold; margin: 0; }}
        .tagline {{ text-align: center; font-size: 11px; color: #5B6B7F; margin: 2px 0; }}
        .owner {{ text-align: center; font-size: 10px; color: #5B6B7F; margin-bottom: 10px; }}
        .meta {{ width: 100%; margin-bottom: 10px; }}
        .meta td {{ font-size: 10px; }}
        table.items {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        table.items th {{ background-color: #1E2A44; color: white; padding: 6px; font-size: 10px; border: 1px solid #1E2A44; }}
        table.items td {{ padding: 6px; font-size: 10px; border: 1px solid #D3DBE5; }}
    </style>
    </head>
    <body>
        <h2>DELIVERY CHALLAN</h2>
        <p class="company">Krupalu Creation</p>
        <p class="tagline">Digital Printing</p>
        <p class="owner">Sunny Patel | 7405597333</p>
        <hr>
        <table class="meta">
            <tr>
                <td>PO No: <b>{po_no}</b></td>
                <td>Challan No: <b>{challan_number}</b></td>
                <td>Date: <b>{date_str}</b></td>
            </tr>
        </table>
        <p>To: <b>{company_name}</b></p>
        <table class="items">
            <tr>
                <th>Sr. No.</th>
                <th>Fabric Name</th>
                <th>Size</th>
                <th>Takka (m)</th>
                <th>Total Takka</th>
                <th>Quantity (m)</th>
            </tr>
            {rows_html}
        </table>
        <br/>
        <table style="width:100%; margin-top:30px;">
            <tr>
                <td>Received in good condition, By ______________</td>
                <td align="right">
                    <img src="static/signature.png" width="110"/><br/>
                    <span style="font-size:10px; color:#5B6B7F;">Authorized Signature</span>
                </td>
            </tr>
        </table>
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
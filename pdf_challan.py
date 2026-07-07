import os
from datetime import datetime
from xhtml2pdf import pisa

CHALLAN_FOLDER = "challans"

COMPANY_ADDRESS = "Plot No 30, 1st Floor, Sai Ashish Industries, Rayka Circle, Udhna, Surat."
COMPANY_GST_NUMBER = ""  # Add your GST number here once available


def safe_folder_name(name):
    cleaned = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))
    return cleaned.strip().replace(" ", "_")


def build_challan_html(company_name, challan_number, date_str, po_no, items):
    total_takkas = sum(item.get('takka_count', 0) or 0 for item in items)
    total_quantity = sum(float(item.get('quantity', 0) or 0) for item in items)

    rows_html = ""
    for i, item in enumerate(items, start=1):
        raw_list = str(item.get('takka_list', '') or '')
        takka_values = [v.strip() for v in raw_list.split(',') if v.strip() and v.strip() != '-']

        def build_row(chunk):
            # 6 boxes with a real spacer <td> between each, so boxes always
            # stay visually separate (xhtml2pdf does not honor border-spacing).
            cells = ""
            for idx in range(6):
                if idx > 0:
                    cells += '<td class="takka-spacer"></td>'
                if idx < len(chunk):
                    cells += f'<td class="takka-box" valign="middle">{chunk[idx]}</td>'
                else:
                    cells += '<td class="takka-box-empty">&nbsp;</td>'
            return f"<tr>{cells}</tr>"

        takka_rows = ""
        for j in range(0, len(takka_values), 6):
            takka_rows += build_row(takka_values[j:j + 6])

        if not takka_rows:
            takka_rows = build_row(['-'])

        # The last item row's own bottom border is removed, and a small
        # extra bottom padding is added so there's a bit of breathing room
        # before the summary row's border line (without drawing a second line).
        is_last_row = (i == len(items))
        no_border = ' style="border-bottom:none;"' if is_last_row else ''

        rows_html += (
            f'<tr><td class="sr"{no_border}>{i}</td>'
            f'<td class="fabric-name"{no_border}>{item["fabric_name"]}</td>'
            f'<td class="size"{no_border}>{item.get("size", "") or ""}</td>'
            f'<td class="takka-cell"{no_border}><div class="takka-label-bar">TOTAL TAKKAS: {item.get("takka_count", 0)}</div>'
            f'<table class="takka-grid">{takka_rows}</table></td>'
            f'<td class="qty"{no_border}>{float(item["quantity"]):,}</td></tr>'
        )


    html = f"""
    <html>
    <head>
    <style>
        @page {{
            margin: 0.4in 0.3in 0.4in 0.3in;
        }}
        body {{ font-family: Helvetica; font-size: 10px; color: #1E2A44; }}
        
        .outer-frame {{ width: 100%; border-collapse: collapse; }}
        .outer-frame > tr > td {{ border: 1px solid #D6DEE6; padding: 10px 12px; }}

        .header-table {{ width: 100%; margin-bottom: 8px; }}
        .header-table td {{ vertical-align: middle; }}
        .logo-img {{ border-radius: 50%; }}
        .company-name {{ font-size: 18px; font-weight: bold; color: #1E2A44; }}
        .tagline {{ font-size: 10px; color: #5B6B7F; }}
        .address-line {{ font-size: 8.5px; color: #5B6B7F; margin-top: 1px; }}
        .gst-line {{ font-size: 8.5px; color: #5B6B7F; }}
        .owner-info {{ text-align: right; font-size: 9.5px; color: #5B6B7F; line-height: 1.2; }}
        .owner-info b {{ color: #1E2A44; font-size: 10px; }}

        .title-bar {{ background-color: #1E2A44; color: #FFFFFF; text-align: center; font-size: 13px; font-weight: bold; letter-spacing: 2px; padding: 5px; margin-bottom: 8px; }}

        .meta-table {{ width: 100%; margin-bottom: 8px; border-collapse: collapse; border: none; }}
        .meta-table td {{ vertical-align: top; width: 50%; padding: 2px 4px; font-size: 10px; border: none; }}
        .box-label {{ font-size: 9px; color: #5B6B7F; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 2px; }}
        .party-box {{ background-color: #F2F5F9; padding: 4px 6px; border-radius: 4px; }}
        .party-name {{ font-size: 11px; font-weight: bold; color: #1E2A44; }}
        .challan-no-value {{ color: #1E2A44; }}

        table.items {{ width: 100%; border-collapse: collapse; }}
        table.items th {{ background-color: #F2F5F9; color: #1E2A44; padding: 5px 4px; font-size: 9.5px; font-weight: bold; text-align: left; border-top: 1.5px solid #1E2A44; border-bottom: 1.5px solid #1E2A44; }}
        table.items td {{ padding: 10px 4px; font-size: 9.5px; border-bottom: 1px solid #D3DBE5; vertical-align: middle; }}
        td.sr {{ text-align: center; color: #5B6B7F; width: 5%; }}
        td.fabric-name {{ font-weight: bold; color: #1E2A44; width: 22%; }}
        td.size {{ white-space: nowrap; width: 8%; }}
        td.takka-cell {{ padding: 10px 4px; width: 52%; }}
        td.qty {{ text-align: right; font-weight: bold; white-space: nowrap; color: #1E2A44; width: 13%; }}

        .takka-label-bar {{ 
            color: #1a56db; 
            font-size: 9px; 
            font-weight: bold;
            padding: 0px 0px 4px 0px; 
        }}
        
        table.takka-grid {{ 
            border-collapse: collapse; 
            width: auto;
            margin: 0;
            padding: 0;
        }}
        
        table.takka-grid td.takka-box {{ 
            width: 45px; 
            height: 18px;
            border: 1px solid #D3DBE5; 
            border-radius: 4px; 
            background-color: #F2F5F9; 
            padding: 3px 4px 2px 4px; 
            font-size: 9px; 
            line-height: 9px;
            text-align: center; 
            vertical-align: middle;
            color: #1E2A44; 
        }}
        table.takka-grid td.takka-box-empty {{
            width: 45px;
            border: none;
            background: transparent;
            padding: 2px 4px;
        }}
        table.takka-grid td.takka-spacer {{
            width: 5px;
            border: none;
            background: transparent;
            padding: 0;
        }}

        table.items tr.summary-row td {{ background-color: #F2F5F9; font-weight: bold; padding: 8px 4px; font-size: 10px; white-space: nowrap; border-top: 1.5px solid #9AAEC4; border-bottom: 1.5px solid #9AAEC4; }}
        .takka-total-summary {{ color: #1E2A44; font-weight: bold; }}

        .summary-separator {{
            border-bottom: 1.5px solid #000000;
            margin-bottom: 15px;
        }}

        .signature-label {{ font-size: 9px; color: #5B6B7F; }}
        .signature-table {{ width: 100%; margin-top: 8px; border-collapse: collapse; border: none; }}
        .signature-table td {{ padding: 2px 4px; border: none; vertical-align: bottom; font-size: 10px; }}
    </style>
    </head>
    <body>
    <table class="outer-frame"><tr><td>
        <table class="header-table">
            <tr>
                <td style="width:12%;">
                    <img class="logo-img" src="static/logo.png" width="45" height="45"/>
                </td>
                <td style="width:58%;">
                    <span class="company-name">KRUPALU CREATION</span><br/>
                    <span class="tagline">DIGITAL PRINTING</span><br/>
                    <span class="address-line">{COMPANY_ADDRESS}</span><br/>
                    <span class="gst-line">GST No: {COMPANY_GST_NUMBER or '-'}</span>
                </td>
                <td class="owner-info">
                    <b>Sunny Patel</b><br/>
                    +91 74055 97333<br/>
                    info@krupalucreation.com
                </td>
            </tr>
        </table>

        <div class="title-bar">DELIVERY CHALLAN</div>

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
                    Challan No: <b class="challan-no-value">{challan_number}</b><br/>
                    Date: <b>{date_str}</b><br/>
                    PO No: <b>{po_no or ''}</b>
                </td>
            </tr>
        </table>

        <table class="items">
            <tr>
                <th style="width:5%;">SR.<br/>NO.</th>
                <th style="width:22%;">FABRIC NAME</th>
                <th style="width:8%;">SIZE</th>
                <th style="width:52%;">TAKKA DETAILS (METERS BREAKDOWN)</th>
                <th style="width:13%; text-align:right;">TOTAL<br/>QTY (M)</th>
            </tr>
            {rows_html}
            <tr class="summary-row">
                <td colspan="3"></td>
                <td style="text-align: left;">
                    <span class="takka-total-summary">Total Takkas: {total_takkas}</span>
                </td>
                <td style="text-align: right; color: #1E2A44; font-weight: bold;">
                    {total_quantity:,} m
                </td>
            </tr>
        </table>

        <div class="summary-separator"></div>

        <table class="signature-table">
            <tr>
                <td style="width:50%;">Received in good condition By ______________</td>
                <td style="width:50%; text-align:right;">
                    <b>For, Krupalu Creation</b><br/>
                    <img src="static/signature.png" width="75"/><br/>
                    <span class="signature-label">Authorized Signature</span>
                </td>
            </tr>
        </table>

        <div style="margin-top:12px; padding-top:6px; border-top:1px dashed #D3DBE5; font-size:8.5px; color:#5B6B7F;">
            <b>Terms &amp; Conditions:</b><br/>
            1. Goods once delivered will not be taken back. 2. Check delivery immediately. Any discrepancy should be reported within 24 hours.
        </div>
    </td></tr></table>
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

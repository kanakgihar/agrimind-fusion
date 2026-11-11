"""PDF report generation with ReportLab. Takes plain dicts/paths so it can be tested without the web stack."""
import io
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.disease_knowledge import DISCLAIMER

GREEN = colors.HexColor("#1E4D3B")


def _img(path, max_w=80 * mm, max_h=70 * mm):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    s = min(max_w / w, max_h / h)
    return Image(str(path), width=w * s, height=h * s)


def build_pdf(scan: dict, recommendation: dict, upload_path=None, overlay_path=None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title=f"AgriMind Fusion scan {scan['scan_id']}")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=GREEN, fontSize=20, alignment=0)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=GREEN, fontSize=13, spaceBefore=10)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.HexColor("#555555"), leading=11)
    P = lambda t, st=body: Paragraph(escape(str(t)), st)  # noqa: E731

    s = []
    s.append(Paragraph("AgriMind Fusion - Scan report", h1))
    s.append(P(f"Scan #{scan['scan_id']}  |  Created: {scan.get('created_at', '')}  |  Report generated: {datetime.now():%Y-%m-%d %H:%M}", small))

    s.append(Paragraph("1. Image-based prediction (model output)", h2))
    imgs = []
    if upload_path and Path(upload_path).exists():
        imgs.append([_img(upload_path), P("Uploaded image", small)])
    if overlay_path and Path(overlay_path).exists():
        imgs.append([_img(overlay_path), P("Grad-CAM overlay (where the model looked)", small)])
    if imgs:
        t = Table([[c[0] for c in imgs], [c[1] for c in imgs]])
        t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        s.append(t)
    s.append(Spacer(1, 4))
    rows = [["Predicted class", scan["display_name"]], ["Crop", scan["crop"]],
            ["Status", "Healthy (per model)" if scan["is_healthy"] else "Disease / pest class predicted"],
            ["Confidence (softmax score)", f"{scan['confidence']:.1%}"], ["Model", scan["model_version"]]]
    t = Table([[P(a), P(b)] for a, b in rows], colWidths=[55 * mm, 110 * mm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3EC"))]))
    s.append(t)
    s.append(Spacer(1, 4))
    s.append(P("Top-3 predictions: " + "; ".join(f"{x['display_name']} ({x['confidence']:.1%})" for x in scan["top3"])))
    for w in scan.get("warnings", []):
        s.append(P("Warning: " + w, small))
    gi = scan.get("gradcam_info")
    if gi:
        s.append(P(f"Grad-CAM: strongest model attention in the {gi.get('main_region')} area (about {gi.get('coverage_pct')}% of the image). "
                   "Grad-CAM shows where the model looked; it does not prove the biological cause.", small))

    s.append(Paragraph("2. Environmental context (user-entered or fetched; NOT used by the image model)", h2))
    env, risk = scan.get("environment"), scan.get("risk")
    if env and risk:
        s.append(P(f"Rule-based risk: {risk['category']} (score {risk['score']}/{risk['max_score']}, {risk['rule_version']})"))
        for f in risk["factors"]:
            s.append(P(f"- {f['factor']}: {f['explanation']}", small))
        for f in risk.get("stress_flags", []):
            s.append(P(f"- {f}", small))
    else:
        s.append(P("No environmental data was provided for this scan."))
    s.append(P("Satellite indices: not included in this report.", small))

    s.append(Paragraph("3. Recommendations (general guidance, traceable to inputs)", h2))
    s.append(P(f"Urgency: {recommendation.get('urgency', 'n/a')}.  {recommendation.get('summary', '')}"))
    for sec in ("Next step", "Management", "Prevention", "Monitoring", "Irrigation", "Environmental precaution"):
        its = [i for i in recommendation.get("items", []) if i["section"] == sec]
        if its:
            s.append(P(sec, ParagraphStyle("sec", parent=body, fontName="Helvetica-Bold", spaceBefore=4)))
            for i in its:
                s.append(P(f"- {i['text']}  [source: {i['source']}]", body))
    s.append(Paragraph("4. Limitations and disclaimer", h2))
    s.append(P(DISCLAIMER, small))
    s.append(P(recommendation.get("knowledge_source", ""), small))
    doc.build(s)
    return buf.getvalue()

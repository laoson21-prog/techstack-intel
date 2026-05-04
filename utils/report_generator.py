# utils/report_generator.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from utils.database import get_all_companies, get_company_stack
from utils.affiliate_links import get_affiliate

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

# ─────────────────────────────────────────
# PALETTE SILICON VALLEY
# ─────────────────────────────────────────
C_BG_DARK      = colors.HexColor("#0a0e1a")
C_BG_CARD      = colors.HexColor("#111827")
C_BG_ROW_ALT   = colors.HexColor("#f8faff")
C_BG_ROW_NORM  = colors.white

C_BLUE_PRIMARY = colors.HexColor("#3b82f6")
C_BLUE_LIGHT   = colors.HexColor("#93c5fd")
C_BLUE_DARK    = colors.HexColor("#1e3a5f")

C_GREEN        = colors.HexColor("#10b981")
C_GREEN_LIGHT  = colors.HexColor("#d1fae5")
C_GREEN_DARK   = colors.HexColor("#065f46")

C_PURPLE       = colors.HexColor("#8b5cf6")

C_ORANGE       = colors.HexColor("#f59e0b")

C_TEXT_PRIMARY = colors.HexColor("#111827")
C_TEXT_SECOND  = colors.HexColor("#6b7280")
C_TEXT_LIGHT   = colors.HexColor("#9ca3af")
C_BORDER       = colors.HexColor("#e5e7eb")
C_BORDER_DARK  = colors.HexColor("#374151")

PAGE_W, PAGE_H = A4


# ─────────────────────────────────────────
# CANVAS PERSONNALISE (header / footer)
# ─────────────────────────────────────────
class PremiumCanvas(canvas.Canvas):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self.draw_page_decorations(page_num=i + 1)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_num):
        # Barre superieure bleue
        self.setFillColor(C_BLUE_PRIMARY)
        self.rect(0, PAGE_H - 8*mm, PAGE_W, 8*mm, fill=1, stroke=0)

        # Accent violet droite
        self.setFillColor(C_PURPLE)
        self.rect(PAGE_W - 4*cm, PAGE_H - 8*mm, 4*cm, 8*mm, fill=1, stroke=0)

        # Logo texte
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 9)
        self.drawString(1.5*cm, PAGE_H - 5.5*mm, "TECHSTACK INTEL")

        # Date
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#bfdbfe"))
        self.drawRightString(PAGE_W - 4.5*cm, PAGE_H - 5.5*mm,
                             datetime.now().strftime("%B %Y"))

        # Barre inferieure
        self.setFillColor(C_BG_CARD)
        self.rect(0, 0, PAGE_W, 1.2*cm, fill=1, stroke=0)

        # Ligne separation footer
        self.setStrokeColor(C_BLUE_PRIMARY)
        self.setLineWidth(0.5)
        self.line(1.5*cm, 1.2*cm, PAGE_W - 1.5*cm, 1.2*cm)

        # Footer gauche
        self.setFont("Helvetica", 7)
        self.setFillColor(C_TEXT_LIGHT)
        self.drawString(1.5*cm, 4*mm,
            "Genere le {}  -  TechStack Intel".format(
                datetime.now().strftime("%d/%m/%Y a %H:%M")))

        # Footer droit
        self.setFillColor(C_BLUE_LIGHT)
        self.drawRightString(PAGE_W - 1.5*cm, 4*mm, "techstack-intel.io")

        # Numero de page
        self.setFillColor(C_TEXT_LIGHT)
        self.drawCentredString(PAGE_W / 2, 4*mm, "- {} -".format(page_num))


# ─────────────────────────────────────────
# STYLES TYPOGRAPHIQUES
# ─────────────────────────────────────────
def build_styles():
    s = getSampleStyleSheet()

    s.add(ParagraphStyle("CoverTitle",
        fontName="Helvetica-Bold", fontSize=36,
        textColor=colors.white, leading=42,
        alignment=TA_LEFT, spaceAfter=8))

    s.add(ParagraphStyle("CoverTitle2",
        fontName="Helvetica-Bold", fontSize=36,
        textColor=C_BLUE_PRIMARY, leading=42,
        alignment=TA_LEFT, spaceAfter=16))

    s.add(ParagraphStyle("CoverSubtitle",
        fontName="Helvetica", fontSize=14,
        textColor=colors.HexColor("#93c5fd"), leading=20,
        alignment=TA_LEFT, spaceAfter=4))

    s.add(ParagraphStyle("CoverMeta",
        fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#6b7280"), leading=16,
        alignment=TA_LEFT))

    s.add(ParagraphStyle("SectionTitle",
        fontName="Helvetica-Bold", fontSize=16,
        textColor=C_TEXT_PRIMARY, leading=20,
        spaceBefore=20, spaceAfter=6))

    s.add(ParagraphStyle("SectionSubtitle",
        fontName="Helvetica", fontSize=10,
        textColor=C_TEXT_SECOND, leading=14,
        spaceAfter=12))

    s.add(ParagraphStyle("CompanyName",
        fontName="Helvetica-Bold", fontSize=13,
        textColor=C_BLUE_PRIMARY, leading=18,
        spaceBefore=14, spaceAfter=4))

    s.add(ParagraphStyle("CompanyMeta",
        fontName="Helvetica", fontSize=9,
        textColor=C_TEXT_SECOND, leading=13,
        spaceAfter=8))

    s.add(ParagraphStyle("BodyText2",
        fontName="Helvetica", fontSize=9,
        textColor=C_TEXT_PRIMARY, leading=14))

    s.add(ParagraphStyle("BodyBold",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=C_TEXT_PRIMARY, leading=14))

    s.add(ParagraphStyle("Caption",
        fontName="Helvetica", fontSize=8,
        textColor=C_TEXT_LIGHT, leading=12,
        alignment=TA_CENTER))

    s.add(ParagraphStyle("KpiValue",
        fontName="Helvetica-Bold", fontSize=28,
        textColor=C_BLUE_PRIMARY, leading=32,
        alignment=TA_CENTER))

    s.add(ParagraphStyle("KpiLabel",
        fontName="Helvetica", fontSize=8,
        textColor=C_TEXT_SECOND, leading=12,
        alignment=TA_CENTER))

    s.add(ParagraphStyle("AffLabel",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=C_GREEN_DARK, leading=11))

    s.add(ParagraphStyle("AffComm",
        fontName="Helvetica", fontSize=7,
        textColor=C_GREEN, leading=10))

    s.add(ParagraphStyle("Disclaimer",
        fontName="Helvetica", fontSize=8,
        textColor=C_TEXT_LIGHT, leading=13,
        alignment=TA_CENTER))

    return s


# ─────────────────────────────────────────
# COMPOSANTS UI
# ─────────────────────────────────────────
def divider(color=C_BORDER, thickness=0.5, space_before=4, space_after=12):
    return HRFlowable(
        width="100%", thickness=thickness,
        color=color, spaceAfter=space_after,
        spaceBefore=space_before
    )


def kpi_table(data_list, styles):
    cells = []
    for value, label, _ in data_list:
        cells.append([
            Paragraph(str(value), styles["KpiValue"]),
            Paragraph(label,      styles["KpiLabel"]),
        ])
    col_w = (PAGE_W - 4*cm) / len(data_list)
    t = Table([cells], colWidths=[col_w] * len(data_list))
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_BG_ROW_ALT),
        ('BOX',           (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


def section_header_table(title, subtitle, styles):
    accent = Table([[""]], colWidths=[4*mm], rowHeights=[1.2*cm])
    accent.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_BLUE_PRIMARY),
        ('TOPPADDING',    (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    text_block = [
        Paragraph(title,    styles["SectionTitle"]),
        Paragraph(subtitle, styles["SectionSubtitle"]),
    ]
    t = Table([[accent, text_block]],
              colWidths=[8*mm, PAGE_W - 4*cm - 8*mm])
    t.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',   (1,0), (1,0),   8),
        ('TOPPADDING',    (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    return t


# ─────────────────────────────────────────
# BADGE SOURCE (texte pur, sans emoji)
# ─────────────────────────────────────────
def source_badge(source, styles):
    if source == "wappalyzer":
        color = "#1d4ed8"
        label = "[WEB] wappalyzer"
    elif source == "github_topics":
        color = "#7c3aed"
        label = "[TOP] github_topics"
    else:
        color = "#374151"
        label = "[GIT] github"
    return Paragraph(
        '<font color="{}">{}</font>'.format(color, label),
        styles["BodyText2"]
    )


# ─────────────────────────────────────────
# TABLEAU STACK PAR ENTREPRISE
# ─────────────────────────────────────────
def company_stack_table(stack, styles):
    header = [
        Paragraph("TECHNOLOGIE",          styles["Caption"]),
        Paragraph("SOURCE",               styles["Caption"]),
        Paragraph("CATEGORIE",            styles["Caption"]),
        Paragraph("OPPORTUNITE AFFILIEE", styles["Caption"]),
    ]
    rows = [header]

    for tech in stack:
        name     = tech[0]
        source   = tech[1]
        category = tech[2] or "-"
        aff      = get_affiliate(name)

        if aff:
            aff_cell = [
                Paragraph(aff["label"],                       styles["AffLabel"]),
                Paragraph("Commission : {}".format(aff["commission"]), styles["AffComm"]),
            ]
        else:
            aff_cell = Paragraph("-", styles["Caption"])

        rows.append([
            Paragraph('<b>{}</b>'.format(name), styles["BodyText2"]),
            source_badge(source, styles),
            Paragraph(category, styles["BodyText2"]),
            aff_cell,
        ])

    col_widths = [4.5*cm, 3.2*cm, 4.3*cm, 6.5*cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), C_BG_DARK),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 8),
        ('TOPPADDING',     (0,0), (-1,0), 10),
        ('BOTTOMPADDING',  (0,0), (-1,0), 10),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('RIGHTPADDING',   (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_BG_ROW_NORM, C_BG_ROW_ALT]),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('TOPPADDING',     (0,1), (-1,-1), 7),
        ('BOTTOMPADDING',  (0,1), (-1,-1), 7),
        ('LINEBELOW',      (0,0), (-1,-1), 0.3, C_BORDER),
        ('BOX',            (0,0), (-1,-1), 0.8, C_BORDER_DARK),
        ('BACKGROUND',     (3,1), (3,-1),  C_GREEN_LIGHT),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


# ─────────────────────────────────────────
# TABLEAU RECAPITULATIF GLOBAL
# ─────────────────────────────────────────
def summary_table(companies_data, styles):
    header = [
        Paragraph("ENTREPRISE",   styles["Caption"]),
        Paragraph("TECHS",        styles["Caption"]),
        Paragraph("GITHUB",       styles["Caption"]),
        Paragraph("WAPPALYZER",   styles["Caption"]),
        Paragraph("AFFILIATIONS", styles["Caption"]),
        Paragraph("SCORE",        styles["Caption"]),
    ]
    rows = [header]

    for item in companies_data:
        stack  = item["stack"]
        github = sum(1 for t in stack if t[1] == "github")
        wapp   = sum(1 for t in stack if t[1] == "wappalyzer")
        affs   = sum(1 for t in stack if get_affiliate(t[0]))
        total  = len(stack)
        score  = min(100, int((affs / max(total, 1)) * 100 + (total / 2)))

        if score >= 60:
            score_hex = "#065f46"
        elif score >= 30:
            score_hex = "#92400e"
        else:
            score_hex = "#7f1d1d"

        rows.append([
            Paragraph('<b>{}</b>'.format(item["name"]), styles["BodyText2"]),
            Paragraph(str(total),  styles["BodyText2"]),
            Paragraph(str(github), styles["BodyText2"]),
            Paragraph(str(wapp),   styles["BodyText2"]),
            Paragraph(str(affs),   styles["BodyText2"]),
            Paragraph('<font color="{}"><b>{}/100</b></font>'.format(score_hex, score),
                      styles["BodyText2"]),
        ])

    col_widths = [5*cm, 2*cm, 2.5*cm, 3*cm, 3*cm, 3*cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), C_BG_DARK),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTSIZE',       (0,0), (-1,0), 8),
        ('TOPPADDING',     (0,0), (-1,0), 10),
        ('BOTTOMPADDING',  (0,0), (-1,0), 10),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('ALIGN',          (1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_BG_ROW_NORM, C_BG_ROW_ALT]),
        ('FONTSIZE',       (0,1), (-1,-1), 9),
        ('TOPPADDING',     (0,1), (-1,-1), 9),
        ('BOTTOMPADDING',  (0,1), (-1,-1), 9),
        ('LINEBELOW',      (0,0), (-1,-1), 0.3, C_BORDER),
        ('BOX',            (0,0), (-1,-1), 0.8, C_BORDER_DARK),
        ('BACKGROUND',     (4,1), (4,-1),  C_GREEN_LIGHT),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


# ─────────────────────────────────────────
# PAGE DE COUVERTURE
# ─────────────────────────────────────────
def build_cover(story, styles, companies_data):
    month       = datetime.now().strftime("%B %Y")
    total_techs = sum(len(c["stack"]) for c in companies_data)
    total_affs  = sum(
        sum(1 for t in c["stack"] if get_affiliate(t[0]))
        for c in companies_data
    )

    story += [
        Spacer(1, 1.5*cm),
        Table([[Paragraph(
            'RAPPORT MENSUEL  -  {}'.format(month.upper()),
            styles["CoverMeta"]
        )]], colWidths=[PAGE_W - 4*cm]),
        Spacer(1, 0.5*cm),
        Paragraph("TechStack", styles["CoverTitle"]),
        Paragraph("Intel",     styles["CoverTitle2"]),
        Spacer(1, 0.3*cm),
        Paragraph("Intelligence technologique automatisee", styles["CoverSubtitle"]),
        Spacer(1, 0.2*cm),
        Paragraph(
            "Analyse de {} entreprises  -  "
            "{} technologies detectees  -  "
            "{} opportunites d'affiliation".format(
                len(companies_data), total_techs, total_affs),
            styles["CoverMeta"]
        ),
        Spacer(1, 1.5*cm),
        divider(color=C_BLUE_PRIMARY, thickness=2, space_after=20),
        Spacer(1, 0.5*cm),
        kpi_table([
            (len(companies_data), "Entreprises analysees",  C_BLUE_PRIMARY),
            (total_techs,         "Technologies detectees", C_PURPLE),
            (total_affs,          "Liens affilies actifs",  C_GREEN),
        ], styles),
        Spacer(1, 1.5*cm),
        Paragraph(
            "Ce rapport est genere automatiquement par TechStack Intel. "
            "Les donnees sont collectees via GitHub API et Wappalyzer. "
            "Les opportunites d'affiliation sont identifiees en temps reel.",
            styles["Disclaimer"]
        ),
        PageBreak(),
    ]


# ─────────────────────────────────────────
# GENERATION PRINCIPALE
# ─────────────────────────────────────────
def generate_monthly_report(output_dir=None):
    if output_dir is None:
        output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data')
        )
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(
        output_dir,
        "TechStack_Report_{}.pdf".format(datetime.now().strftime('%Y_%m'))
    )

    styles         = build_styles()
    story          = []
    companies      = get_all_companies()
    companies_data = []

    for c in companies:
        name  = c[1] if isinstance(c, (list, tuple)) else c["name"]
        stack = get_company_stack(name)
        if stack:
            companies_data.append({"name": name, "stack": stack})

    # Couverture
    build_cover(story, styles, companies_data)

    # Vue d'ensemble
    story.append(section_header_table(
        "Vue d'ensemble",
        "Synthese des {} entreprises surveillees - {}".format(
            len(companies_data), datetime.now().strftime('%B %Y')),
        styles
    ))
    story.append(Spacer(1, 0.4*cm))
    story.append(summary_table(companies_data, styles))
    story.append(PageBreak())

    # Detail par entreprise
    story.append(section_header_table(
        "Analyse detaillee",
        "Stack technique complete par entreprise avec opportunites d'affiliation",
        styles
    ))
    story.append(Spacer(1, 0.3*cm))

    for item in companies_data:
        stack      = item["stack"]
        github_cnt = sum(1 for t in stack if t[1] == "github")
        wapp_cnt   = sum(1 for t in stack if t[1] == "wappalyzer")
        aff_cnt    = sum(1 for t in stack if get_affiliate(t[0]))

        story.append(KeepTogether([
            divider(color=C_BORDER, thickness=0.5, space_before=8, space_after=4),
            Paragraph(item['name'], styles["CompanyName"]),
            Paragraph(
                "{} technologies  -  "
                "[GIT] {} GitHub  -  "
                "[WEB] {} Wappalyzer  -  "
                "[AFF] {} affiliations".format(
                    len(stack), github_cnt, wapp_cnt, aff_cnt),
                styles["CompanyMeta"]
            ),
        ]))
        story.append(company_stack_table(stack, styles))
        story.append(Spacer(1, 0.5*cm))

    # Build PDF
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
        title="TechStack Intel - {}".format(datetime.now().strftime('%B %Y')),
        author="TechStack Intel",
        subject="Rapport mensuel stack technique",
    )
    doc.build(story, canvasmaker=PremiumCanvas)

    print("Rapport PDF premium genere : {}".format(filename))
    return filename


# ─────────────────────────────────────────
# TEST DIRECT
# ─────────────────────────────────────────
if __name__ == "__main__":
    generate_monthly_report()
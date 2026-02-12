from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os

# pdf使用微软雅黑字体
# FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
# pdfmetrics.registerFont(TTFont("MSYH", FONT_PATH))


# 使用相对路径（关键！）
FONT_PATH = os.path.join("fonts", "msyh.ttc")  # 或直接写 "fonts/msyh.ttc"

# 将字体添加到 matplotlib 字体管理器
fm.fontManager.addfont(FONT_PATH)

# 设置字体属性
prop = fm.FontProperties(fname=FONT_PATH)
plt.rcParams["font.family"] = prop.get_name()  # 全局生效
# 或者：pdfmetrics.registerFont(TTFont("MSYH", FONT_PATH))  # 如果你必须用 reportlab

def _header_footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("MSYH", 9)
    canvas.setFillColor(colors.grey)

    # 页眉
    canvas.drawString(
        2 * cm,
        A4[1] - 1.5 * cm,
        "家庭资产结构体检报告（仅供个人参考）",
    )

    # 页脚
    canvas.drawRightString(
        A4[0] - 2 * cm,
        1.2 * cm,
        f"第 {doc.page} 页",
    )

    canvas.restoreState()

def generate_pdf(file_path, summary, insights, chart_path):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # 基础样式
    styles["Normal"].fontName = "MSYH"
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 14

    styles.add(
        ParagraphStyle(
            name="TitleCN",
            fontName="MSYH",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionCN",
            fontName="MSYH",
            fontSize=13,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallCN",
            fontName="MSYH",
            fontSize=9,
            leading=12,
            textColor=colors.grey,
        )
    )

    story = []

    # ===== 封面标题 =====
    story.append(Paragraph("家庭资产结构体检报告", styles["TitleCN"]))
    story.append(
        Paragraph(
            f"生成日期：{datetime.now().strftime('%Y-%m-%d')}",
            styles["SmallCN"],
        )
    )
    story.append(Spacer(1, 16))

    # ===== 报告说明 =====
    story.append(Paragraph("报告说明", styles["SectionCN"]))
    story.append(
        Paragraph(
            "本报告基于用户填写的家庭资产信息自动生成，用于帮助用户观察家庭资产结构、流动性及潜在风险，仅作为个人财务管理参考，不构成任何形式的投资建议。",
            styles["Normal"],
        )
    )

    # ===== 核心指标 =====
    story.append(Spacer(1, 12))
    story.append(Paragraph("一、家庭资产核心指标概览", styles["SectionCN"]))

    table_data = [
        ["指标", "金额（元）"],
        ["家庭总资产", f"{summary['total_assets']:,.0f}"],
        ["家庭负债", f"{summary['total_debt']:,.0f}"],
        ["家庭净资产", f"{summary['net_assets']:,.0f}"],
    ]

    table = Table(table_data, colWidths=[6 * cm, 6 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONT", (0, 0), (-1, -1), "MSYH"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    story.append(table)

    # ===== 资产结构图 =====
    story.append(Spacer(1, 16))
    story.append(Paragraph("二、家庭资产结构分布", styles["SectionCN"]))
    story.append(Image(chart_path, width=14 * cm, height=9 * cm))

    # ===== 解读建议 =====
    story.append(Spacer(1, 16))
    story.append(Paragraph("三、资产结构解读与建议", styles["SectionCN"]))

    # （一）结构观察
    story.append(Spacer(1, 8))
    story.append(Paragraph("（一）结构观察", styles["Normal"]))
    for s in insights.get("structure", []):
        story.append(Paragraph(f"• {s}", styles["Normal"]))

    # （二）潜在风险
    story.append(Spacer(1, 8))
    story.append(Paragraph("（二）潜在风险", styles["Normal"]))
    for r in insights.get("risk", []):
        story.append(Paragraph(f"• {r}", styles["Normal"]))

    # （三）优化建议
    story.append(Spacer(1, 8))
    story.append(Paragraph("（三）优化建议", styles["Normal"]))
    for a in insights.get("advice", []):
        story.append(Paragraph(f"• {a}", styles["Normal"]))

    # ===== 免责声明 =====
    story.append(Spacer(1, 24))
    story.append(Paragraph("免责声明", styles["SectionCN"]))
    story.append(
        Paragraph(
            "本报告内容基于用户提供的信息自动生成，仅用于个人资产结构分析与学习交流，不构成任何投资建议或承诺。用户应结合自身实际情况，谨慎决策。",
            styles["SmallCN"],
        )
    )

    doc.build(
        story,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )
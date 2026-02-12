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
import os

# ============================================================
# 中文字体配置（核心修复）
# ============================================================

# 定义字体名称常量
CHINESE_FONT_NAME = "MicrosoftYaHei"
FALLBACK_FONT_NAME = "Helvetica"


# 查找字体文件的函数
def find_font_file():
    """在多个可能的位置查找中文字体文件"""

    # 当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 项目根目录

    possible_paths = [
        # 相对路径（各种可能）
        os.path.join("fonts", "msyh.ttc"),
        os.path.join("fonts", "msyh.ttf"),
        os.path.join(current_dir, "fonts", "msyh.ttc"),
        os.path.join(current_dir, "fonts", "msyh.ttf"),
        os.path.join(project_root, "fonts", "msyh.ttc"),
        os.path.join(project_root, "fonts", "msyh.ttf"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


# 注册中文字体
def register_chinese_font():
    """注册中文字体，返回是否成功"""

    font_path = find_font_file()

    if font_path and os.path.exists(font_path):
        try:
            # 注册字体
            pdfmetrics.registerFont(TTFont(CHINESE_FONT_NAME, font_path))

            # 注册字体族（支持粗体、斜体等）
            pdfmetrics.registerFontFamily(
                CHINESE_FONT_NAME,
                normal=CHINESE_FONT_NAME,
                bold=CHINESE_FONT_NAME,  # 如果有粗体文件可单独指定
                italic=CHINESE_FONT_NAME,
                boldItalic=CHINESE_FONT_NAME
            )
            print(f"✓ 成功注册中文字体: {font_path}")
            return True
        except Exception as e:
            print(f"✗ 注册字体失败: {e}")
            return False
    else:
        print("✗ 找不到中文字体文件，将使用英文字体")
        return False


# 初始化字体
FONT_LOADED = register_chinese_font()
ACTIVE_FONT = CHINESE_FONT_NAME if FONT_LOADED else FALLBACK_FONT_NAME


# ============================================================
# PDF 生成函数
# ============================================================

def _header_footer(canvas, doc):
    """页眉页脚"""
    canvas.saveState()

    # 使用当前激活的字体
    canvas.setFont(ACTIVE_FONT, 9)
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
    """生成PDF报告"""

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # ===== 基础样式 =====
    # 修改 Normal 样式
    styles["Normal"].fontName = ACTIVE_FONT
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 14

    # ===== 自定义样式 =====
    # 标题样式
    styles.add(
        ParagraphStyle(
            name="TitleCN",
            fontName=ACTIVE_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )

    # 章节标题样式
    styles.add(
        ParagraphStyle(
            name="SectionCN",
            fontName=ACTIVE_FONT,
            fontSize=13,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
        )
    )

    # 小字样式
    styles.add(
        ParagraphStyle(
            name="SmallCN",
            fontName=ACTIVE_FONT,
            fontSize=9,
            leading=12,
            textColor=colors.grey,
        )
    )

    # 正文列表样式
    styles.add(
        ParagraphStyle(
            name="ListItem",
            fontName=ACTIVE_FONT,
            fontSize=10,
            leading=14,
            leftIndent=10,
            spaceAfter=2,
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
                ("FONT", (0, 0), (-1, -1), ACTIVE_FONT),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)

    # ===== 资产结构图 =====
    if os.path.exists(chart_path):
        story.append(Spacer(1, 16))
        story.append(Paragraph("二、家庭资产结构分布", styles["SectionCN"]))
        story.append(Image(chart_path, width=14 * cm, height=9 * cm))
    else:
        story.append(Spacer(1, 16))
        story.append(Paragraph("二、家庭资产结构分布", styles["SectionCN"]))
        story.append(Paragraph("（图表文件不存在）", styles["SmallCN"]))

    # ===== 解读建议 =====
    story.append(Spacer(1, 16))
    story.append(Paragraph("三、资产结构解读与建议", styles["SectionCN"]))

    # （一）结构观察
    story.append(Spacer(1, 8))
    story.append(Paragraph("（一）结构观察", styles["Normal"]))
    for s in insights.get("structure", []):
        story.append(Paragraph(f"• {s}", styles["ListItem"]))

    # （二）潜在风险
    story.append(Spacer(1, 8))
    story.append(Paragraph("（二）潜在风险", styles["Normal"]))
    for r in insights.get("risk", []):
        story.append(Paragraph(f"• {r}", styles["ListItem"]))

    # （三）优化建议
    story.append(Spacer(1, 8))
    story.append(Paragraph("（三）优化建议", styles["Normal"]))
    for a in insights.get("advice", []):
        story.append(Paragraph(f"• {a}", styles["ListItem"]))

    # ===== 免责声明 =====
    story.append(Spacer(1, 24))
    story.append(Paragraph("免责声明", styles["SectionCN"]))
    story.append(
        Paragraph(
            "本报告内容基于用户提供的信息自动生成，仅用于个人资产结构分析与学习交流，不构成任何投资建议或承诺。用户应结合自身实际情况，谨慎决策。",
            styles["SmallCN"],
        )
    )

    # 构建PDF
    doc.build(
        story,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )


# ============================================================
# 兼容性：如果你需要在其他文件中导入 FONT_LOADED 状态
# ============================================================
__all__ = ["generate_pdf", "FONT_LOADED", "ACTIVE_FONT"]
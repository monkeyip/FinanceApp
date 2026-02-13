import streamlit as st
from models import FamilyProfile
from insights_engine import generate_structure_insights
import plotly.express as px
from calculator import calculate_summary, asset_breakdown
import plotly.io as pio
import tempfile
from pdf_report import generate_pdf
import os
import plotly.express as px


st.set_page_config(page_title="家庭资产结构体检", layout="centered")
st.title("🏠 家庭资产结构体检")

if "profile" not in st.session_state:
    st.session_state.profile = FamilyProfile()

if "summary" not in st.session_state:
    st.session_state.summary = None

if "breakdown" not in st.session_state:
    st.session_state.breakdown = None

if "fig" not in st.session_state:
    st.session_state.fig = None

if "insights" not in st.session_state:
    st.session_state.insights = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False


profile = st.session_state.profile

st.header("一、填写家庭资产")

with st.expander("💰 现金类"):
    profile.cash.items["活期存款"] = st.number_input("活期存款", min_value=0.0)
    profile.cash.items["备用金"] = st.number_input("备用金", min_value=0.0)

with st.expander("📦 稳健类"):
    profile.stable.items["定期存款"] = st.number_input("定期存款", min_value=0.0)
    profile.stable.items["低风险理财"] = st.number_input("低风险理财", min_value=0.0)

with st.expander("📈 投资类"):
    profile.invest.items["基金/股票"] = st.number_input("基金/股票", min_value=0.0)
    profile.invest.items["其他投资"] = st.number_input("其他投资", min_value=0.0)

with st.expander("🏠 房产类"):
    profile.property.items["自住房"] = st.number_input("自住房市值", min_value=0.0)
    profile.property.items["投资房"] = st.number_input("投资房市值", min_value=0.0)

with st.expander("📉 负债"):
    profile.debt.items["房贷"] = st.number_input("房贷余额", min_value=0.0)
    profile.debt.items["其他负债"] = st.number_input("其他负债", min_value=0.0)


import tempfile
import plotly.io as pio

if "chart_path" not in st.session_state:
    st.session_state.chart_path = None


if st.button("生成我的家庭资产全景图"):
    summary = calculate_summary(profile)
    breakdown = asset_breakdown(profile)

    labels = [k for k, v in breakdown.items() if v > 0]
    values = [v for v in breakdown.values() if v > 0]

    fig = px.pie(
        names=labels,
        values=values,
        title="家庭资产结构分布",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # ✅ 云端优先使用文泉驿微米黑，本地备选微软雅黑
    chinese_font = "WenQuanYi Micro Hei, Microsoft YaHei, '微软雅黑', Arial, sans-serif"

    fig.update_traces(
        textinfo="percent+label",
        textfont=dict(
            size=14,
            color="black",
            family=chinese_font,   # 关键修复
        ),
        hovertemplate="<b>%{label}</b><br>金额：%{value:,.0f}<br>占比：%{percent}<extra></extra>",
    )

    fig.update_layout(
        showlegend=False,
        title=dict(
            text="家庭资产结构分布",
            font=dict(
                family=chinese_font,
                size=18,
                color="black"
            ),
            x=0.5
        )
    )

    insights = generate_structure_insights(breakdown, summary)

    st.session_state.update({
        "summary": summary,
        "breakdown": breakdown,
        "fig": fig,
        "insights": insights,
        "pdf_ready": False,
    })


if st.session_state.summary:
    summary = st.session_state.summary
    breakdown = st.session_state.breakdown
    fig = st.session_state.fig
    insights = st.session_state.insights

    st.header("二、资产结构概览")
    st.metric("总资产", f"{summary['total_assets']:,.0f}")
    st.metric("净资产", f"{summary['net_assets']:,.0f}")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("三、家庭资产结构解读")
    st.subheader("📌 结构观察")
    for s in insights["structure"]:
        st.write("•", s)

    st.subheader("⚠️ 潜在风险")
    for r in insights["risk"]:
        st.write("•", r)

    st.subheader("✅ 优化建议")
    for a in insights["advice"]:
        st.write("•", a)
    # for insight in insights:
    #     st.info(insight)

if st.button("📄 生成家庭资产结构体检报告（PDF）"):
    with st.spinner("正在生成报告，请稍候..."):
        # ✅ 导出前强制设置中文字体（双重保险）
        fig = st.session_state.fig
        chinese_font = "WenQuanYi Micro Hei, Microsoft YaHei, '微软雅黑', Arial, sans-serif"

        fig.update_traces(
            textfont=dict(family=chinese_font)
        )
        fig.update_layout(
            title=dict(font=dict(family=chinese_font)),
            font=dict(family=chinese_font)
        )

        # 1️⃣ 导出饼图
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img:
            pio.write_image(
                fig,  # 使用已更新字体的 fig
                img.name,
                width=800,
                height=500,
                engine="kaleido",
            )
            chart_path = img.name

        # 2️⃣ 生成 PDF（你的 ReportLab 已正常）
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf:
            generate_pdf(
                file_path=pdf.name,
                summary=st.session_state.summary,
                insights=st.session_state.insights,
                chart_path=chart_path,
            )
            st.session_state.pdf_path = pdf.name
            st.session_state.pdf_ready = True

if st.session_state.get("pdf_ready"):
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ 下载 PDF 报告",
            data=f,
            file_name="家庭资产结构体检报告.pdf",
            mime="application/pdf",
        )
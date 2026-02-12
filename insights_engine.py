def generate_structure_insights(breakdown, summary):
    total = summary["total_assets"]

    pct = {k: v / total for k, v in breakdown.items() if total > 0}

    structure = []
    risk = []
    advice = []

    # ========= 结构观察 =========
    if pct.get("房产", 0) > 0.6:
        structure.append("家庭资产以房产为主，占比较高，整体资产结构偏向不动产。")

    if pct.get("金融投资", 0) > 0.3:
        structure.append("家庭在金融投资方面已有一定配置，具备一定的资产多元化基础。")

    if pct.get("现金及活期", 0) < 0.1:
        structure.append("家庭现金及活期资产占比较低，整体流动性偏弱。")

    if not structure:
        structure.append("家庭资产结构较为均衡，各类资产分布相对分散。")

    # ========= 潜在风险 =========
    if pct.get("房产", 0) > 0.7:
        risk.append("资产过度集中于房产，流动性不足，在应对突发支出时灵活性较弱。")

    if pct.get("现金及活期", 0) < 0.05:
        risk.append("短期可用资金偏少，可能影响家庭对突发事件的应对能力。")

    if summary["total_debt"] > 0:
        debt_ratio = summary["total_debt"] / summary["total_assets"]
        if debt_ratio > 0.4:
            risk.append("家庭负债水平相对较高，需关注现金流压力及偿债安全边际。")

    if not risk:
        risk.append("当前资产结构未显示出明显的集中或流动性风险。")

    # ========= 优化建议（不碰具体产品） =========
    if pct.get("现金及活期", 0) < 0.1:
        advice.append("可适当预留一定比例的流动性资产，用于应对家庭短期支出及不确定性。")

    if pct.get("房产", 0) > 0.6:
        advice.append("未来新增资产配置时，可关注提升资产结构的灵活性与分散度。")

    advice.append("建议定期（如每年）对家庭资产结构进行一次整体回顾与调整。")

    return {
        "structure": structure,
        "risk": risk,
        "advice": advice,
    }
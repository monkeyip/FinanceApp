from models import FamilyProfile

def sum_group(group):
    return sum(group.items.values())

def calculate_summary(profile: FamilyProfile):
    total_assets = (
        sum_group(profile.cash)
        + sum_group(profile.stable)
        + sum_group(profile.invest)
        + sum_group(profile.property)
        + sum_group(profile.other)
    )

    total_debt = sum_group(profile.debt)

    return {
        "total_assets": total_assets,
        "total_debt": total_debt,
        "net_assets": total_assets - total_debt,
        "cash_ratio": sum_group(profile.cash) / total_assets if total_assets else 0,
        "invest_ratio": sum_group(profile.invest) / total_assets if total_assets else 0,
        "property_ratio": sum_group(profile.property) / total_assets if total_assets else 0,
    }

def asset_breakdown(profile):
    return {
        "现金类": sum_group(profile.cash),
        "稳健类": sum_group(profile.stable),
        "投资类": sum_group(profile.invest),
        "房产类": sum_group(profile.property),
        "其他资产": sum_group(profile.other),
    }
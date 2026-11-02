"""读取原始公共厕所 CSV，绘制换尿布台经纬度点图；不修改原始数据。"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 保存图片，无需打开绘图窗口
import matplotlib.pyplot as plt
import pandas as pd


DAY = Path(__file__).resolve().parents[1]
ROOT = DAY.parent
SOURCE = ROOT / "data_raw" / "family" / "Public_Restrooms_20261024.csv"
OUTPUT = DAY / "outputs" / "nyc_changing_stations.png"

# 只根据原始字段分类；普通 Yes 不代表位于男厕或女厕。
CATEGORIES = {
    "Yes": ("Yes — restroom placement unspecified", "#197a83", "o"),
    "Yes, in women's restroom only": ("Women's restroom only (explicit label)", "#b45309", "^"),
    "Yes, in men's restroom only": ("Men's restroom only (explicit label)", "#6d55a2", "s"),
    "Yes, in single-stall all gender restroom only": (
        "Single-stall all-gender only (explicit label)", "#287640", "D"
    ),
}


def main():
    # 保留 N/A 文本，避免 pandas 自动将其与空白混为一谈。
    df = pd.read_csv(SOURCE, keep_default_na=False)
    labels = df["Changing Stations"].str.strip().str.strip('"').str.strip()
    confirmed = labels.isin(CATEGORIES)
    no_station = labels.eq("No")
    unclear = ~(confirmed | no_station)
    longitude = pd.to_numeric(df["Longitude"], errors="coerce")
    latitude = pd.to_numeric(df["Latitude"], errors="coerce")
    valid_coords = longitude.between(-180, 180) & latitude.between(-90, 90)

    print(f"Source: {SOURCE}")
    print(f"Total records: {len(df)}")
    print(f"Explicitly labeled Yes: {confirmed.sum()}")
    print(f"Explicitly labeled No: {no_station.sum()}")
    print(f"Blank / N/A / otherwise unclear: {unclear.sum()}")
    print(labels[unclear].replace("", "<blank>").value_counts().to_string())
    print(f"Yes records with invalid or missing coordinates: {(confirmed & ~valid_coords).sum()}")

    fig, ax = plt.subplots(figsize=(10, 10))
    for value, (label, color, marker) in CATEGORIES.items():
        selected = labels.eq(value) & valid_coords
        ax.scatter(
            longitude[selected], latitude[selected], s=24, alpha=0.65,
            color=color, marker=marker, linewidths=0,
            label=f"{label} (n={selected.sum()})",
        )
        print(f"Plotted {value}: {selected.sum()}")

    ax.set(title="NYC Public Restrooms: Changing Stations", xlabel="Longitude", ylabel="Latitude")

    ax.set_aspect(1 / 0.758)
    ax.grid(alpha=0.2)
    ax.legend(loc="best", fontsize=8, framealpha=0.95)
    fig.text(
        0.08, 0.025,
        f"Source: {SOURCE.name}\n"
        f"Blank / N/A / unclear: {unclear.sum()} (excluded); No: {no_station.sum()} (excluded).\n"
        "All operational statuses included; labels do not establish current availability.\n"
        "Longitude/latitude scatter; no basemap. Overlapping points may hide records.",
        fontsize=8, color="#444444",
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()

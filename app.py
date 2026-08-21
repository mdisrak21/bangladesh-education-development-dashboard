import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Bangladesh Education Dashboard",
    page_icon="📚",
    layout="wide"
)

COUNTRY = "BGD"

INDICATORS = {
    "Adult literacy rate (%)": "SE.ADT.LITR.ZS",
    "Education expenditure (% of GDP)": "SE.XPD.TOTL.GD.ZS",
    "Primary school gender parity index": "SE.ENR.PRIM.FM.ZS",
}


@st.cache_data(ttl=3600)
def get_indicator(code):

    url = (
        f"https://api.worldbank.org/v2/"
        f"country/{COUNTRY}/indicator/{code}"
    )

    params = {
        "format": "json",
        "per_page": 1000
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    rows = data[1] if len(data) > 1 else []

    records = []

    for item in rows:

        if item["value"] is not None:

            records.append({
                "year": int(item["date"]),
                "value": item["value"]
            })

    return pd.DataFrame(records).sort_values("year")


st.title("🇧🇩 Bangladesh Education & Development Dashboard")

st.write(
    "An interactive dashboard for exploring public "
    "education indicators for Bangladesh."
)

st.sidebar.header("Dashboard Filters")

st.sidebar.write(
    "Use the filters below to explore the data."
)
selected = st.multiselect(
    "Select indicators",
    list(INDICATORS.keys()),
    default=[
        "Adult literacy rate (%)",
        "Education expenditure (% of GDP)"
    ]
)


if not selected:

    st.warning("Please select at least one indicator.")

    st.stop()
    st.sidebar.success(
    f"{len(selected)} indicator(s) selected"
)


all_data = []


for indicator_name in selected:

    indicator_code = INDICATORS[indicator_name]

    df = get_indicator(indicator_code)

    df["indicator"] = indicator_name

    all_data.append(df)


data = pd.concat(
    all_data,
    ignore_index=True
)


st.subheader("Latest Available Values")


columns = st.columns(len(selected))


for column, indicator_name in zip(columns, selected):

    indicator_data = data[
        data["indicator"] == indicator_name
    ].dropna()

    indicator_data = indicator_data.sort_values("year")

    if not indicator_data.empty:

        latest = indicator_data.iloc[-1]

        column.metric(
            indicator_name,
            f"{latest['value']:.2f}",
            f"Year: {int(latest['year'])}"
        )

st.subheader("📅 Year Range")

available_years = sorted(
    data["year"].unique()
)

if len(available_years) >= 2:

    start_year, end_year = st.slider(
        "Select year range",
        min_value=int(min(available_years)),
        max_value=int(max(available_years)),
        value=(
            int(min(available_years)),
            int(max(available_years))
        )
    )

    filtered_data = data[
        (data["year"] >= start_year) &
        (data["year"] <= end_year)
    ]

else:

    filtered_data = data
st.subheader("Education Indicator Trends")


for indicator_name in selected:

    indicator_data = filtered_data[
    filtered_data["indicator"] == indicator_name
]

    indicator_data = indicator_data.set_index("year")

    st.write(indicator_name)

    st.line_chart(
        indicator_data[["value"]],
        height=300
    )


st.subheader("Dataset")

st.dataframe(
    data.sort_values(
        ["indicator", "year"],
        ascending=[True, False]
    ),
    use_container_width=True
)


st.download_button(
    "Download CSV",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="bangladesh_education_data.csv",
    mime="text/csv"
)

st.subheader("🔎 Key Insights")

for indicator_name in selected:

    indicator_data = data[
        data["indicator"] == indicator_name
    ].dropna()

    indicator_data = indicator_data.sort_values("year")

    if len(indicator_data) >= 2:

        first = indicator_data.iloc[0]
        latest = indicator_data.iloc[-1]

        change = latest["value"] - first["value"]

        if change > 0:
            direction = "increased"
        elif change < 0:
            direction = "decreased"
        else:
            direction = "remained stable"

        st.write(
            f"**{indicator_name}:** "
            f"The indicator {direction} from "
            f"{first['value']:.2f} in {int(first['year'])} "
            f"to {latest['value']:.2f} in {int(latest['year'])}."
        )
st.info(
    "Data source: World Bank Indicators API."
)
st.divider()

st.subheader("📌 About This Project")

st.write("""
This project is an interactive data dashboard designed to explore
education-related indicators for Bangladesh using publicly available
World Bank data.

The dashboard allows users to compare indicators, explore historical
trends, filter data by year, and download the underlying dataset.
""")

st.subheader("🎯 Project Objective")

st.write("""
The main objective is to practice data collection, data cleaning,
API integration, visualization, and evidence-based interpretation
using real-world development data.
""")

st.subheader("🛠️ Technologies Used")

st.write("""
• Python  
• Pandas  
• Streamlit  
• REST API  
• Data Visualization
""")

st.subheader("🌐 Data Source")

st.write("""
World Bank Indicators API
""")

st.caption(
    "This dashboard is intended for descriptive data exploration and educational purposes."
)
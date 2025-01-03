import polars as pl
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots

# Load the CSV file
url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-52/SaaS-businesses-NYSE-NASDAQ.csv"
data = pl.read_csv(url)

# Ensure relevant columns are numeric and drop invalid rows
data = data.with_columns([
    pl.col("IPO Year").cast(pl.Float64).alias("IPO Year"),
    pl.col("Year Founded").cast(pl.Float64).alias("Year Founded")
]).drop_nulls(["IPO Year", "Year Founded"])

# Filter out rows where IPO Year is before Year Founded
data = data.filter(pl.col("IPO Year") >= pl.col("Year Founded"))

# Calculate elapsed time to IPO
data = data.with_columns((pl.col("IPO Year") - pl.col("Year Founded")).alias("Elapsed Time to IPO"))

# Calculate the median elapsed time to IPO for the trailing 5 years for each founding year
data = data.sort("Year Founded").with_columns(
    pl.col("Elapsed Time to IPO").rolling_mean(5, min_periods=1).alias("Median Elapsed Time")
)

# Ensure no NaN values in Year Founded and IPO Year before generating range
data = data.drop_nulls(["Year Founded", "IPO Year"])

# Determine the range of years
min_year_founded = int(data["Year Founded"].min())
max_ipo_year = int(data["IPO Year"].max())

# Continue with Plotly visualization


# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    column_widths=[0.8, 0.2],
    specs=[[{"type": "scatter"}, {"type": "scatter"}]],
    shared_yaxes=True,
    subplot_titles=()  # Disable default subplot titles
)

# Add thin lines and markers for IPOs by founding year
for i, year in enumerate(sorted(data["Year Founded"].unique())):
    color = pc.qualitative.Dark2[i % len(pc.qualitative.Dark2)]
    subset = data.filter(pl.col("Year Founded") == year)
    ipo_years = subset["IPO Year"]
    if ipo_years.len() > 0:
        fig.add_trace(go.Scatter(
            x=[year, ipo_years.max()],
            y=[year, year],
            mode='lines',
            line=dict(width=1.5, color=color),
            showlegend=False
        ), row=1, col=1)
        for ipo_year, count in ipo_years.value_counts().iter_rows():
            fig.add_trace(go.Scatter(
                x=[ipo_year],
                y=[year],
                mode='markers+text',
                marker=dict(size=8, color=color, opacity=0.8),
                text=[str(count)],
                textposition='middle center',
                showlegend=False
            ), row=1, col=1)

# Add circles for median elapsed time to IPO in the second subplot
median_data = data.unique(subset=["Year Founded"]).drop_nulls(["Median Elapsed Time"])
fig.add_trace(go.Scatter(
    x=median_data["Median Elapsed Time"],
    y=median_data["Year Founded"],
    mode='markers',
    marker=dict(size=8, color="darkred", opacity=0.8),
    showlegend=False
), row=1, col=2)

# Add vertical dotted lines for major years
for year in range(min_year_founded, max_ipo_year + 1, 5):
    fig.add_trace(go.Scatter(
        x=[year, year],
        y=[min_year_founded, max_ipo_year],
        mode='lines',
        line=dict(width=1, dash='dot', color='lightgray'),
        showlegend=False
    ), row=1, col=1)

# Style the layout
fig.update_layout(
    title=dict(
        text="SaaS Company IPO Trends: Faster Path from Founding to Market",
        font=dict(family="Arial Black, sans-serif", size=18, color="black"),
        x=0.082, xanchor="left"
    ),
    font=dict(family="Arial, sans-serif", size=12, color="black"),
    xaxis=dict(
        title="<b>IPO Year</b>",
        range=[min_year_founded, max_ipo_year + 1],
        gridcolor="lightgray",
        zerolinecolor="lightgray"
    ),
    xaxis2=dict(
        title="<b>Median IPO Time (Trailing 5)</b>",
        gridcolor="lightgray",
        zerolinecolor="lightgray"
    ),
    yaxis=dict(
        title="<b>Founding Year</b>",
        autorange="reversed",
        gridcolor="lightgray",
        zerolinecolor="lightgray"
    ),
    height=800,
    plot_bgcolor="white",
    paper_bgcolor="white",
    annotations=[
        dict(
            text="Rising IPO Activity",
            xref="paper", yref="paper",
            x=0.0, y=1.01,
            xanchor="left", yanchor="bottom",
            font=dict(size=14, family="Arial Black, sans-serif", color="Teal"),
            showarrow=False
        ),
        dict(
            text="Shrinking Wait Times",
            xref="paper", yref="paper",
            x=0.81, y=1.01,
            xanchor="left", yanchor="bottom",
            font=dict(size=14, family="Arial Black, sans-serif", color="Teal"),
            showarrow=False
        ),
        dict(
            text="<i>Source: https://publicsaascompanies.com/</i>",
            xref="paper", yref="paper",
            x=0.01, y=-0.08,
            xanchor="left",
            font=dict(size=10, family="Arial, sans-serif", color="gray"),
            showarrow=False
        )
    ],
    shapes=[
        dict(
            type="line",
            xref="paper", yref="paper",
            x0=0, x1=1,
            y0=1.07, y1=1.07,
            line=dict(color="black", width=2)
        )
    ]
)

fig.show()
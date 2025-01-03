import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots

# Load the CSV file
url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-52/SaaS-businesses-NYSE-NASDAQ.csv"
data = pd.read_csv(url)

# Ensure relevant columns are numeric and drop invalid rows
data["IPO Year"] = pd.to_numeric(data["IPO Year"], errors="coerce")
data["Year Founded"] = pd.to_numeric(data["Year Founded"], errors="coerce")
data = data.dropna(subset=["IPO Year", "Year Founded"])

# Filter out rows where IPO Year is before Year Founded
data = data[data["IPO Year"] >= data["Year Founded"]]

# Calculate elapsed time to IPO
data["Elapsed Time to IPO"] = data["IPO Year"] - data["Year Founded"]

# Calculate the median elapsed time to IPO for the trailing 5 years for each founding year
data = data.sort_values("Year Founded")
data["Median Elapsed Time"] = (
    data.groupby("Year Founded")["Elapsed Time to IPO"]
    .transform(lambda x: x.rolling(5, min_periods=1).median())
)

# Ensure no NaN values in Year Founded and IPO Year before generating range
valid_years = data.dropna(subset=["Year Founded", "IPO Year"])
min_year_founded = int(valid_years["Year Founded"].min())
max_ipo_year = int(valid_years["IPO Year"].max())

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
    subset = data[data["Year Founded"] == year]
    ipo_years = subset["IPO Year"]
    if not ipo_years.empty:
        fig.add_trace(go.Scatter(
            x=[year, ipo_years.max()],
            y=[year, year],
            mode='lines',
            line=dict(width=1.5, color=color),
            showlegend=False
        ), row=1, col=1)
        for ipo_year, count in ipo_years.value_counts().items():
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
median_data = data.drop_duplicates(subset=["Year Founded"])
median_data = median_data.dropna(subset=["Median Elapsed Time"])
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
        # 1) Subplot 1 title (left subplot)
        dict(
            text="Rising IPO Activity",
            xref="paper", yref="paper",
            x=0.0, y=1.01,
            xanchor="left", yanchor="bottom",
            font=dict(size=14, family="Arial Black, sans-serif", color="Teal"),
            showarrow=False
        ),
        # 2) Subplot 2 title (right subplot)
        dict(
            text="Shrinking Wait Times",
            xref="paper", yref="paper",
            x=0.81, y=1.01,
            xanchor="left", yanchor="bottom",
            font=dict(size=14, family="Arial Black, sans-serif", color="Teal"),
            showarrow=False
        ),
        # 3) Footnote
        dict(
            text="<i>Source: https://publicsaascompanies.com/</i>",
            xref="paper", yref="paper",
            x=0.01, y=-0.08,
            xanchor="left",
            font=dict(size=10, family="Arial, sans-serif", color="gray"),
            showarrow=False
        )
    ],
    # Add a horizontal line above the title
    shapes=[
        dict(
            type="line",
            xref="paper", yref="paper",
            x0=0, x1=1,  # Full width
            y0=1.07, y1=1.07,  # Position above title
            line=dict(color="black", width=2)
        )
    ]
)

fig.show()

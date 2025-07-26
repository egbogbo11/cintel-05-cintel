# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# --------------------------------------------
# Constants
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Reactive calc that updates every few seconds
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    reactive_value_wrapper.get().append(new_dictionary_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    latest_dictionary_entry = new_dictionary_entry

    return deque_snapshot, df, latest_dictionary_entry

# --------------------------------------------
# UI Layout and Display
# --------------------------------------------

ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True)

with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/denisecase/cintel-05-cintel",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://denisecase.github.io/cintel-05-cintel/",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# --------------------------------------------
# Value Box for Current Temp with Styling
# --------------------------------------------

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("snowflake"),
        theme="bg-gradient-cyan-blue",
    ):
        "Current Temperature"

        @render.text
        def display_temp():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} °C"

        "Live from Antarctica 🌨️"

# --------------------------------------------
# Card for Date & Time Display
# --------------------------------------------

with ui.card(full_screen=True):
    ui.card_header("🕒 Current Date & Time")

    @render.text
    def display_time():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        return f"{latest_dictionary_entry['timestamp']}"

# --------------------------------------------
# Card for Most Recent Readings Table
# --------------------------------------------

with ui.card():
    ui.card_header("📋 Most Recent Readings")

    @render.data_frame
    def display_df():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option("display.width", None)
        return render.DataGrid(df, width="100%")

# --------------------------------------------
# Card for Plot with Trend Line
# --------------------------------------------

with ui.card():
    ui.card_header("📈 Temperature Trend Over Time")

    @render_plotly
    def display_plot():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            fig = px.scatter(
                df,
                x="timestamp",
                y="temp",
                title="📉 Temperature Readings with Trend Line",
                labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                color_discrete_sequence=["deepskyblue"]
            )

            x_vals = list(range(len(df)))
            y_vals = df["temp"]
            slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
            df["best_fit_line"] = [slope * x + intercept for x in x_vals]

            fig.add_scatter(
                x=df["timestamp"],
                y=df["best_fit_line"],
                mode="lines",
                line=dict(color="lightgray", dash="dot"),
                name="Regression Line"
            )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                template="plotly_dark",
                font=dict(family="Arial", size=12),
                plot_bgcolor="#1f2c56",
                paper_bgcolor="#1f2c56",
                title_font_size=18
            )

        return fig

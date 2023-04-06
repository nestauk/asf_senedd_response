import pandas as pd
import altair as alt

from asf_senedd_response.config.base_config import *
from nesta_ds_utils.viz.altair.formatting import setup_theme
from asf_senedd_response.utils.formatting import format_number

fig_output_path = {
    "english": "outputs/figures/english/",
    "welsh": "outputs/figures/welsh/",
}

setup_theme()


def generic_plot(
    base_data,
    field,
    title,
    x_label,
    y_label,
    filename,
    expand_y=False,
    x_type="good",
    language="english",
):
    source = pd.DataFrame({"count": base_data[field].value_counts()}).reset_index()

    if x_type == "good":
        order = quality_list[language]
    elif x_type == "tenure":
        order = tenure_list[language]
    else:
        order = ["A", "B", "C", "D", "E", "F", "G"]

    chart = (
        alt.Chart(source)
        .transform_joinaggregate(
            Total="sum(count)",
        )
        .transform_calculate(PercentOfTotal="datum.count / datum.Total")
        .mark_bar()
        .encode(
            x=alt.X("index", sort=order, title=x_label, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "PercentOfTotal:Q",
                axis=alt.Axis(format=".0%"),
                title=y_label,
                scale=alt.Scale(domain=[0, 0.5]) if expand_y == True else alt.Scale(),
            ),
        )
        .properties(
            width=500,
            height=300,
            title=title + " (N = " + format_number(len(base_data)) + ")"
            if type(title) == str
            else title[:-1]
            + [title[-1] + " (N = " + format_number(len(base_data)) + ")"],
        )
    )

    chart.save(fig_output_path[language] + filename + ".html")

    print("Saved: " + filename + ".html")

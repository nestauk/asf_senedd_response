import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

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
    """Create a generic bar chart

    Args:
        base_data (_type_): _description_
        field (_type_): _description_
        title (_type_): _description_
        x_label (_type_): _description_
        y_label (_type_): _description_
        filename (_type_): _description_
        expand_y (bool, optional): _description_. Defaults to False.
        x_type (str, optional): _description_. Defaults to "good".
        language (str, optional): _description_. Defaults to "english".
    """
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


# matplotlib only cycles through 10 colours, so manually defining 11 here to cover all age categories
colors = [
    "#000000",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def age_prop_chart(base_data, title, filename, language="english"):

    text_labels = [
        "Mean energy efficiency: " + str(val)
        for val in base_data["CURRENT_ENERGY_EFFICIENCY"]
    ]
    prop_labels = [str(round(val, 1)) + "%" for val in base_data["proportion"]]
    width = 1

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    ax.bar(
        " ",
        base_data.loc[0, "proportion"],
        width,
        label=base_data.loc[0, "CONSTRUCTION_AGE_BAND"],
        color=colors[0],
    )

    for i in range(1, 11):
        ax.bar(
            " ",
            base_data.loc[i, "proportion"],
            width,
            bottom=base_data.loc[i - 1, "cumul_prop"],
            label=base_data.loc[i, "CONSTRUCTION_AGE_BAND"],
            color=colors[i],
        )

    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100))
    ax.set_ylabel("Percentage of Welsh housing stock", fontweight="bold", fontsize=12)
    ax.set_title(title, fontweight="bold", fontsize=14, pad=20)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        reversed(handles),
        reversed(labels),
        loc="upper right",
        bbox_to_anchor=(1.6, 1),
        fontsize=10,
        title="Age band",
        title_fontproperties={"weight": "bold"},
    )

    rects = ax.patches

    for rect, label in zip(rects, text_labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            rect.get_y() + height / 2,
            label,
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )

    for rect, label in zip(rects, prop_labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() + 0.01,
            rect.get_y() + height / 2,
            label,
            ha="left",
            va="center",
            fontsize=12,
        )

    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    plt.tight_layout()

    plt.savefig(fig_output_path[language] + filename + ".png", bbox_inches="tight")

    print("Saved: " + filename + ".png")

import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from keplergl import KeplerGl

from utils.utils import format_number
from utils.utils import arial

fig_output_path = "outputs/"

alt.themes.register('arial', arial)
alt.themes.enable('arial')

plt.rc('font',family='Arial')


def generic_plot(base_data, field, title, x_label, y_label, filename, expand_y=False, x_type="good"):
    source = pd.DataFrame(
        {"count": base_data[field].value_counts()}
    ).reset_index()
    
    if x_type == "good":
        order = ["Very Poor", "Poor", "Average", "Good", "Very Good"]
    elif x_type == "tenure":
        order = ["Perchen-feddiannaeth", "Rhentu cymdeithasol", "Rhentu preifat", "Anhysbys"]
    else:
        order = ["A", "B", "C", "D", "E", "F", "G"]
    
    chart = alt.Chart(source).transform_joinaggregate(
        Total='sum(count)',
    ).transform_calculate(
        PercentOfTotal="datum.count / datum.Total"
    ).mark_bar().encode(
        x=alt.X('index', sort=order, title=x_label, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('PercentOfTotal:Q', axis=alt.Axis(format='.0%'), title=y_label,
               scale=alt.Scale(domain=[0, 0.5]) if expand_y==True else alt.Scale()),
    ).properties(
        width=500,
        height=300,
        title=title+" (N = "+format_number(len(base_data))+")" if type(title) == str else title[:-1] + [title[-1]+" (N = "+format_number(len(base_data))+")"]
    )
    
#     text = chart.mark_text(
#         align='center',
#         baseline='middle',
#         dy = 10
#     ).encode(
#         text='count:Q'
#     )
#     chart.configure_axis(labelFont='Comic Sans MS')
#     chart.configure_title(font='Comic Sans MS')
    
#     return chart + text
    
    chart.save(fig_output_path + filename + ".html")
    
    print("Saved: " + filename + ".html")



def age_prop_chart(base_data, title, filename):
    
    text_labels = ["Effeithlonrwydd ynni cymedrig: " + str(val) for val in base_data["CURRENT_ENERGY_EFFICIENCY"]]
    prop_labels = [str(round(val, 1)) + "%" for val in base_data["proportion"]]
    width = 1

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.bar(" ", base_data.loc[0, "proportion"], width, label=base_data.loc[0, "CONSTRUCTION_AGE_BAND"])

    for i in range(1, 11):
        ax.bar(" ", base_data.loc[i, "proportion"], width, bottom=base_data.loc[i-1, "cumul_prop"], label=base_data.loc[i, "CONSTRUCTION_AGE_BAND"])

    # for c in ax.containers:
    #     ax.bar_label(c, label_type='center', fmt="%.1f%%")
        
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100))
    ax.set_ylabel("Canran stoc tai Cymru", fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight="bold", fontsize=14, pad=20)
    
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.6, 1), fontsize=10, title="Band oedran", title_fontproperties={"weight":"bold"})

    rects = ax.patches

    for rect, label in zip(rects, text_labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width()/2, rect.get_y()+height/2, label, ha="center", va="center", color="white", fontsize=12
        )

    for rect, label in zip(rects, prop_labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() + 0.01, rect.get_y() + height/2, label, ha="left", va="center", fontsize=12
        )

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    
    plt.tight_layout()
    
    plt.savefig(fig_output_path + filename + ".png", bbox_inches='tight')
    
    print("Saved: " + filename + ".png")


def plot_kepler_graph(base_data, filename):
    
    hex_map = KeplerGl(height=500)
    hex_map.add_data(
        data=base_data[["perc_true", "hex_id"]], name="Heat pump proportions"
    )
    hex_map.save_to_html(fig_output_path + filename + ".html")

    print("Saved: " + filename + ".html")
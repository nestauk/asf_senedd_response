# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: senedd_response
#     language: python
#     name: senedd_response
# ---

# ## Imports

# +
# %load_ext autoreload
# %autoreload 2

from asf_core_data.getters.epc.epc_data import load_england_wales_data
from asf_core_data.getters.epc.epc_data import load_preprocessed_epc_data
from asf_core_data.pipeline.preprocessing import preprocess_epc_data
from asf_core_data.utils.visualisation import easy_plotting, kepler
from asf_core_data.utils.geospatial import data_agglomeration
from asf_core_data.utils.geospatial.data_agglomeration import add_hex_id, get_cat_distr_grouped_by_agglo_f
from asf_core_data.getters.data_getters import load_data

from pathlib import Path
import pandas as pd
import altair as alt
import re
from keplergl import KeplerGl
# -

# ## Get data

# +
data_path = "inputs/wales_epc.csv"
fig_output_path = "outputs/"

if not Path(data_path).is_file():

    print("Loading and preparing the data...")

    wales_epc = preprocess_epc_data.load_and_preprocess_epc_data(
        data_path="S3",
        subset="Wales",
        usecols=None,
        remove_duplicates=False,
        save_data=None,
    )

    wales_epc.to_csv(data_path, index=False)

    print("Done!")

else:

    print("Loading the data...")
    wales_epc = pd.read_csv(data_path)
    print("Done!")

# +
wales_df_noindex = wales_epc.reset_index(drop=True)
wales_df = wales_df_noindex.sort_values("INSPECTION_DATE").groupby("UPRN").tail(1).reset_index(drop=True)

wales_hp = wales_df.loc[wales_df.HP_INSTALLED].reset_index(drop=True)
# wales_hp = wales_hp.sort_values("INSPECTION_DATE").groupby("UPRN").last().reset_index(drop=True)
# -

# ## Plots and stats

# ### Simple stats

# +
print("Number of properties with a heat pump in EPC database:", len(wales_hp))
print("Total number of properties in EPC database:", len(wales_df))

print("Percentage of properties with heat pump:", "{:.2%}".format(len(wales_hp)/len(wales_df)))


# -

# ### Wall construction

# +
def insulation_quality(entry):
    if ("Average thermal transmittance" in entry) | ("Trawsyriannedd thermol cyfartalog" in entry):
        val = float(re.findall(r'\s(-*\d\.*\d*)\s', entry)[0])
        if val < 0.23:
            return "Full"
        elif val < 0.32:
            return "Partial"
        else:
            return "None"
    elif re.search(".*no insulation.*", entry):
        return "None"
    elif re.search(".*partial.*", entry):
        return "Partial"
    else:
        return "Full"

def wall_material(entry):
    if ("Average thermal transmittance" in entry) | ("Trawsyriannedd thermol cyfartalog" in entry):
        return "Unknown"
    elif "System built" in entry:
        return "Unknown"
    elif "Cavity" in entry:
        return "Cavity"
    elif "Timber" in entry:
        return "Timber"
    else:
        return "Solid"

def add_wall_info(df):
    df["Wall insulation type"] = df["WALLS_DESCRIPTION"].map(insulation_quality)
    df["Wall material"] = df["WALLS_DESCRIPTION"].map(wall_material)
    return df


# -

wales_df = add_wall_info(wales_df)
wales_hp = add_wall_info(wales_hp)


def wall_plot(base_data, title):
    source = pd.DataFrame(
        {"count": base_data[["Wall insulation type", "Wall material"]].value_counts()}
    ).reset_index()
    
    return alt.Chart(source).transform_joinaggregate(
        Total='sum(count)',
    ).transform_calculate(
        PercentOfTotal="datum.count / datum.Total * 100"
    ).mark_bar().encode(
    alt.X('sum(PercentOfTotal):Q', title="Percentage"),
    alt.Y('Wall insulation type', sort=["Full", "Partial", "None"]),
    alt.Color("Wall material"),
    order=alt.Order(
          # Sort the segments of the bars by this field
          'Wall material',
          sort='ascending'
        )
    ).properties(
        width=500,
        height=300,
        title=title,
    )


wall_plot(wales_df, "Wall insulation of all properties")

wall_plot(wales_hp, "Wall insulation of properties with heat pumps")


# ### Energy efficiency

# +
def arial():
    font = "Arial"
    
    return {
        "config" : {
             "title": {'font': font},
             "axis": {
                  "labelFont": font,
                  "titleFont": font
             }
        }
    }

alt.themes.register('arial', arial)
alt.themes.enable('arial')

# +
import re

def format_number(n):
    if n>9999:
        return re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", str(n))
    else:
        return str(n)


# +
def generic_plot(base_data, field, title, x_label, y_label, expand_y=False, x_type="good"):
    source = pd.DataFrame(
        {"count": base_data[field].value_counts()}
    ).reset_index()
    
    if x_type == "good":
        order = ["Very Poor", "Poor", "Average", "Good", "Very Good"]
    elif x_type == "tenure":
        order = ["Owner-occupied", "Socially rented", "Privately rented", "Unknown"]
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

    return chart


# +
wales_hp_temp = wales_hp.copy()
wales_hp_temp.TENURE = wales_hp_temp.TENURE.replace({
    "owner-occupied": "Owner-occupied",
    "rental (social)": "Socially rented",
    "rental (private)": "Privately rented",
    "unknown": "Unknown"
})

generic_plot(
    wales_hp_temp,
    "TENURE",
    "Tenure of Welsh properties with heat pumps",
    'Tenure',
    'Percentage of properties',
    x_type="tenure",
    expand_y=True
)
# -

generic_plot(
    wales_hp,
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df,
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of all properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_hp_oo,
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of owner-occupied properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_hp,
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df,
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of all properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_hp_oo,
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of owner-occupied properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df.loc[wales_df.TENURE=='owner-occupied'],
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of all owner-occupied properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_hp,
    "CURRENT_ENERGY_RATING",
    "EPC ratings of properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_df,
    "CURRENT_ENERGY_RATING",
    "EPC ratings of all properties",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_hp_oo,
    "CURRENT_ENERGY_RATING",
    "EPC ratings of owner-occupied properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_df.loc[wales_df.TENURE == 'owner-occupied'],
    "CURRENT_ENERGY_RATING",
    "EPC ratings of all owner-occupied properties",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_hp.loc[wales_hp.TENURE == 'rental (social)'],
    "CURRENT_ENERGY_RATING",
    "EPC ratings of socially rented properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_df.loc[wales_df.TENURE == 'rental (social)'],
    "CURRENT_ENERGY_RATING",
    "EPC ratings of all socially rented properties",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

generic_plot(
    wales_hp.loc[wales_hp.TENURE == 'rental (social)'],
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of socially rented properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df.loc[wales_df.TENURE=='owner-occupied'],
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of all owner-occupied properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df.loc[wales_df.TENURE=='rental (social)'],
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of all socially rented properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_hp.loc[wales_hp.TENURE == 'rental (social)'],
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of socially rented properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df.loc[wales_df.TENURE == 'rental (social)'],
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of all socially rented properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    wales_df.loc[wales_df.TENURE == 'owner-occupied'],
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of all owner-occupied properties",
    'Energy efficiency rating',
    'Percentage of properties',
)

# Reimplementing using matplotlib:

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

wales_hp_oo = wales_hp.loc[wales_hp.TENURE=="owner-occupied"]


def grouped_plot(hp_records, all_records, factor, name, title, y_lim, hp_legend="Properties with heat pumps", all_legend="All properties"):
    
    labels = ["Very Poor", "Poor", "Average", "Good", "Very Good"]

    hp_counts = hp_records[factor].value_counts().loc[labels]
    hp_counts = hp_counts / sum(hp_counts)

    all_counts = all_records[factor].value_counts().loc[labels]
    all_counts = all_counts / sum(all_counts)

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, hp_counts, width, label=hp_legend)
    rects2 = ax.bar(x + width/2, all_counts, width, label=all_legend)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percentage')
    ax.set_xlabel(name)
    ax.set_title(title)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, y_lim)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))

    ax.bar_label(rects1, padding=3, labels=['{:.0%}'.format(x) for x in hp_counts])
    ax.bar_label(rects2, padding=3, labels=['{:.0%}'.format(x) for x in all_counts])

    fig.tight_layout()

    plt.show()


grouped_plot(wales_hp, wales_df, "WALLS_ENERGY_EFF", "Wall energy efficiency", "Comparison of wall energy efficiency", 0.5)

grouped_plot(wales_hp, wales_df, "ROOF_ENERGY_EFF", "Roof energy efficiency", "Comparison of roof energy efficiency", 0.6)

grouped_plot(
    wales_hp.loc[wales_hp.TENURE=='owner-occupied'],
    wales_df.loc[wales_df.TENURE=='owner-occupied'],
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency",
    "Comparison of roof energy efficiency (owner-occupied properties)",
    0.6,
    "Owner-occupied properties\nwith heat pumps",
    "All owner-occupied properties"
)

# +
labels = ["A", "B", "C", "D", "E", "F", "G"]

hp_counts = wales_hp["CURRENT_ENERGY_RATING"].value_counts().loc[labels]
hp_counts = hp_counts / sum(hp_counts)

all_counts = wales_df["CURRENT_ENERGY_RATING"].value_counts().loc[labels]
all_counts = all_counts / sum(all_counts)

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(2*x - width, hp_counts, width, label='Properties with heat pumps')
rects2 = ax.bar(2*x + width, all_counts, width, label='All properties')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage')
ax.set_xlabel('Energy efficiency rating')
ax.set_title('Comparison of energy efficiency ratings')
ax.set_xticks(2*x, labels)
ax.set_ylim(0, 0.5)
ax.legend(loc='upper left')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))

ax.bar_label(rects1, padding=3, labels=['{:.0%}'.format(x) for x in hp_counts])
ax.bar_label(rects2, padding=3, labels=['{:.0%}'.format(x) for x in all_counts])

fig.tight_layout()

plt.show()
# -

wales_hp.TENURE.value_counts()

# ## Maps

pc_df = load_data("S3", "inputs/supplementary_data/geospatial/ukpostcodes_to_coordindates.csv")

pc_df = pc_df.rename(
    columns={
        "postcode": "POSTCODE",
        "latitude": "LATITUDE",
        "longitude": "LONGITUDE",
    }
)

wales_df_coords = pd.merge(wales_df, pc_df, on=["POSTCODE"])

wales_df_hex = add_hex_id(wales_df_coords, 6)

wales_df_hex.loc[wales_df_hex.hex_id=="86195edafffffff"]

hp_hex_counts = wales_df_hex.groupby(["hex_id", "HP_INSTALLED"]).size().unstack(fill_value=0)

hp_hex_counts["total"] = hp_hex_counts[True] + hp_hex_counts[False]
hp_hex_counts["perc_true"] = hp_hex_counts[True] / hp_hex_counts["total"] * 100

hp_hex_counts = hp_hex_counts.reset_index()

hp_hex_counts.head()

hex_map = KeplerGl(height=500)
hex_map.add_data(
    data=hp_hex_counts[["perc_true", "hex_id"]], name="Heat pump proportions"
)
hex_map.config()
hex_map.save_to_html()

hex_map.config

# ## Characteristics of retrofitted homes

wales_hp.CONSTRUCTION_AGE_BAND.value_counts()

wales_hp.loc[wales_hp.CONSTRUCTION_AGE_BAND=="unknown"].TRANSACTION_TYPE.value_counts()

wales_hp["CONSTRUCTION_AGE_BAND"].loc[(wales_hp.CONSTRUCTION_AGE_BAND=='unknown') & (wales_hp.TRANSACTION_TYPE=='new dwelling')] = "2007 onwards"

wales_df["CONSTRUCTION_AGE_BAND"].loc[(wales_df.CONSTRUCTION_AGE_BAND=='unknown') & (wales_df.TRANSACTION_TYPE=='new dwelling')] = "2007 onwards"

wales_hp.CONSTRUCTION_AGE_BAND.value_counts()

retro_hp = wales_hp.loc[~wales_hp.CONSTRUCTION_AGE_BAND.isin(["2007 onwards", "unknown"])]

retro_hp

generic_plot(
    retro_hp,
    "WALLS_ENERGY_EFF",
    "Wall energy efficiency of pre-2007 properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    retro_hp,
    "ROOF_ENERGY_EFF",
    "Roof energy efficiency of pre-2007 properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
)

generic_plot(
    retro_hp,
    "CURRENT_ENERGY_RATING",
    "EPC ratings of pre-2007 properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

# ## EPC by age

age_medians = wales_df.groupby("CONSTRUCTION_AGE_BAND")["CURRENT_ENERGY_EFFICIENCY"].median()

# +
cats = [
    "England and Wales: before 1900",
    "1900-1929",
    "1930-1949",
    "1950-1966",
    "1965-1975",
    "1976-1983",
    "1983-1991",
    "1991-1998",
    "1996-2002",
    "2003-2007",
    "2007 onwards"
]

cats.reverse()

age_medians = age_medians.loc[cats]

age_medians = age_medians.reset_index().replace({"England and Wales: before 1900": "Pre-1900"})
# -

age_medians

# +
fig, ax = plt.subplots()

ax.barh(age_medians.CONSTRUCTION_AGE_BAND, age_medians.CURRENT_ENERGY_EFFICIENCY)
ax.set_xlabel("Energy efficiency score")
ax.set_ylabel("Year of construction")
ax.set_xlim(0, 100)
ax.set_title("Median energy efficiency score of\nall properties by year of construction")
# -

age_means = wales_df.groupby("CONSTRUCTION_AGE_BAND")["CURRENT_ENERGY_EFFICIENCY"].mean()

# +
cats = [
    "England and Wales: before 1900",
    "1900-1929",
    "1930-1949",
    "1950-1966",
    "1965-1975",
    "1976-1983",
    "1983-1991",
    "1991-1998",
    "1996-2002",
    "2003-2007",
    "2007 onwards"
]

cats.reverse()

age_means = age_means.loc[cats]

age_means = age_means.reset_index().replace({"England and Wales: before 1900": "Pre-1900"})

# +
fig, ax = plt.subplots()

ax.barh(age_means.CONSTRUCTION_AGE_BAND, age_means.CURRENT_ENERGY_EFFICIENCY)
ax.set_xlabel("Energy efficiency score")
ax.set_ylabel("Year of construction")
ax.set_xlim(0, 100)
ax.set_title("Mean energy efficiency score of\nall properties by year of construction")
# -

wales_df.CURRENT_ENERGY_EFFICIENCY.hist(bins=100)

age_props = wales_df.loc[wales_df.CONSTRUCTION_AGE_BAND != "unknown"].CONSTRUCTION_AGE_BAND.value_counts(normalize=True)*100

age_props = age_props.reset_index()
age_props = age_props.rename(columns={"index": "CONSTRUCTION_AGE_BAND", "CONSTRUCTION_AGE_BAND": "proportion"})

ages_efficiencies = wales_df.groupby("CONSTRUCTION_AGE_BAND")["CURRENT_ENERGY_EFFICIENCY"].mean().reset_index()

age_data = age_props.merge(ages_efficiencies, on="CONSTRUCTION_AGE_BAND")

age_data["CONSTRUCTION_AGE_BAND"] = age_data["CONSTRUCTION_AGE_BAND"].replace({"England and Wales: before 1900": "Pre-1900"})

age_data = age_data.loc[[2, 0, 5, 1, 4, 7, 6, 9, 8, 10, 3]].reset_index(drop=True)

age_data["CURRENT_ENERGY_EFFICIENCY"] = age_data["CURRENT_ENERGY_EFFICIENCY"].round(1)

age_data["cumul_prop"] = age_data["proportion"].cumsum()

plt.rc('font',family='Arial')

# +
heights = age_data["proportion"]
text_labels = ["Mean energy efficiency: " + str(val) for val in age_data["CURRENT_ENERGY_EFFICIENCY"]]
prop_labels = [str(round(val, 1)) + "%" for val in age_data["proportion"]]
width = 1

fig, ax = plt.subplots()
fig.set_figheight(10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)

ax.bar(" ", age_data.loc[0, "proportion"], width, label=age_data.loc[0, "CONSTRUCTION_AGE_BAND"])

for i in range(1, 11):
    ax.bar(" ", age_data.loc[i, "proportion"], width, bottom=age_data.loc[i-1, "cumul_prop"], label=age_data.loc[i, "CONSTRUCTION_AGE_BAND"])

# for c in ax.containers:
#     ax.bar_label(c, label_type='center', fmt="%.1f%%")
    
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(100))
ax.set_ylabel("Percentage of housing stock", fontweight='bold', fontsize=12)

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.6, 1), fontsize=10, title="Age band", title_fontproperties={"weight":"bold"})

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
    
plt.show()
# -

# ## Deciding on U-values for insulation level

# +
vals = [float(re.findall(r'\s(-*\d\.*\d*)\s', entry)[0]) for entry in wales_df.loc[wales_df.WALLS_DESCRIPTION.str.contains("Average thermal transmittance")].WALLS_DESCRIPTION]

filt_vals = [val for val in vals if 0<val<2]

plt.hist(filt_vals, bins=200)
# -

# ### Testing walls description stuff

# +
wales_hp_newest.value_counts(["WALLS_DESCRIPTION", "Wall insulation type"]).head(20)

wales_hp_newest["Wall material"] = wales_hp_newest["WALLS_DESCRIPTION"].map(wall_material)

wales_hp_newest[["WALLS_DESCRIPTION", "Wall insulation type", "Wall material"]].value_counts().head(20)

wales_hp_newest.loc[wales_hp_newest.walls_material == "unknown"][["WALLS_DESCRIPTION", "Wall insulation type", "Wall material"]].value_counts().head(20)
# -

# # Final plots for document

# ## Key stats

print("Number of heat pumps:", len(wales_hp))

print("Number of properties in EPC:", len(wales_df))

print("Estimated proportion of properties with a heat pump:", "{:.2%}".format(len(wales_hp)/len(wales_df)))

wales_hp.TENURE.value_counts()

# ## All records, EPC

generic_plot(
    wales_df.loc[wales_df.CURRENT_ENERGY_RATING != "unknown"],
    "CURRENT_ENERGY_RATING",
    "EPC ratings of all Welsh properties",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

# ## Owner-occupied and privately rented properties with HPs, EPC

generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(['owner-occupied', 'rental (private)'])],
    "CURRENT_ENERGY_RATING",
    "EPC ratings of owner-occupied and privately rented Welsh properties with heat pumps",
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

# ## Owner-occupied and privately rented properties with HPs, built pre-2007, EPC

generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(['owner-occupied', 'rental (private)']) & (wales_hp.CONSTRUCTION_AGE_BAND != "2007 onwards")],
    "CURRENT_ENERGY_RATING",
    ["EPC ratings of owner-occupied and privately rented Welsh properties", "with heat pumps, built pre-2007"],
    'Energy efficiency rating',
    'Percentage of properties',
    x_type="other"
)

# ## Proportion and average EPC by age band

# +
heights = age_data["proportion"]
text_labels = ["Mean energy efficiency: " + str(val) for val in age_data["CURRENT_ENERGY_EFFICIENCY"]]
prop_labels = [str(round(val, 1)) + "%" for val in age_data["proportion"]]
width = 1

fig, ax = plt.subplots()
fig.set_figheight(10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)

ax.bar(" ", age_data.loc[0, "proportion"], width, label=age_data.loc[0, "CONSTRUCTION_AGE_BAND"])

for i in range(1, 11):
    ax.bar(" ", age_data.loc[i, "proportion"], width, bottom=age_data.loc[i-1, "cumul_prop"], label=age_data.loc[i, "CONSTRUCTION_AGE_BAND"])

# for c in ax.containers:
#     ax.bar_label(c, label_type='center', fmt="%.1f%%")
    
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(100))
ax.set_ylabel("Percentage of Welsh housing stock", fontweight='bold', fontsize=12)

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.6, 1), fontsize=10, title="Age band", title_fontproperties={"weight":"bold"})

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
    
plt.show()
# -

wales_df.ROOF_ENERGY_EFF.value_counts(dropna=False)

len(wales_df.loc[
    wales_df.CURRENT_ENERGY_RATING.isin(["A", "B", "C"])
    & wales_df.WALLS_ENERGY_EFF.isin(["Good", "Very Good"])
])

len(wales_df.loc[
    wales_df.CURRENT_ENERGY_RATING.isin(["A", "B", "C"])
    & wales_df.WALLS_ENERGY_EFF.isin(["Good", "Very Good"])
    & wales_df.ROOF_ENERGY_EFF.isin(["Good", "Very Good"])
])

len(wales_df)

201103/883749

wales_df.loc[wales_df.UPRN==100100028826].INSPECTION_DATE

wales_df_noindex.loc[wales_df_noindex.UPRN==100100028826].INSPECTION_DATE

wales_df.TENURE.value_counts()

wales_df.HP_INSTALLED.sum()

wales_hp.HP_TYPE.value_counts()



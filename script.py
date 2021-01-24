#TODO: store css files & map adjustments in seperate variables

# Importing pandas and data science tools
import pandas as pd
import json
import numpy as np
import plotly.express as px
import math

# Importing dash

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


# Loading external stylesheets & meta-tags

# Starting dash app

# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
app.title = "COVID-19"

print("Reloading...")

#-------------------------------------------------

# Loading the kaggle COVID-19 dataframe, with country-wise information

df = pd.read_csv("data/country_wise_latest.csv")

df["Deaths / 100 Recovered"].replace({float("inf"): 0}, inplace=True)

df["None"] = 0
df["Log-None"] = 0


# Creating logarithmic versions of each continuous column with a "Log-" prefix

continuous = ["Confirmed", "Deaths", "Recovered", "Active", "New cases", "New deaths", "New recovered",
	"Recovered / 100 Cases", "Deaths / 100 Recovered", "Confirmed last week", "1 week change", r"1 week % increase", "Deaths / 100 Cases"]
continuous.sort()



df_sum = pd.DataFrame(df[continuous].sum(axis=0).apply(lambda x: math.floor(x)))
df_sum.reset_index(level=0, inplace=True)
df_sum.rename(columns={"index": "", 0: " "}, inplace = True)

def log_func(x):
	if x > 0:
		return np.log10(x)
	elif x == 0:
		return 0
	elif x < 0:
		return np.log10(abs(x)) * -1
	elif x == float("inf"):
		return 0
	else:
		print("Incorrect input to log_func")

for col in continuous:

	new_name = "Log-%s" % col
	df[new_name] = df[col].apply(log_func)



# Generating labels for the dropdown

column_choices = ["Confirmed", "Deaths", "Recovered", "Active", "New cases", "New deaths", "New recovered",
	"Deaths / 100 Cases", "Recovered / 100 Cases", "Deaths / 100 Recovered", "Confirmed last week", "1 week change",
	r"1 week % increase", "WHO Region"]

column_choices.sort()
column_dropdown_options = []
continuous_dropdown_options = []

for col in column_choices:
	column_dropdown_options.append({"label": col, "value": col})

for col  in continuous:
	continuous_dropdown_options.append({"label": col, "value": col})


# Creating a template for the hover function (currently not available for choropleth maps so commented out)

#hovertemplate = "<b>Deaths:</b> %{Deaths}" + "<b>Region:</b> %s" % "WHO Region" + "<b>Deaths per 100 Recovered:</b> %s" % "Deaths / 100 Recovered" + "<b>Active:</b> %s" % "Active"

# Dropdown styling

"""
cols in df: 'Country/Region', 'Confirmed', 'Deaths', 'Recovered', 'Active',
       'New cases', 'New deaths', 'New recovered', 'Deaths / 100 Cases',
       'Recovered / 100 Cases', 'Deaths / 100 Recovered',
       'Confirmed last week', '1 week change', '1 week % increase',
       'WHO Region'
"""

# Colour changes

map_color = "#8d93ab"
map_text = "#eeeeee"
map_w = 900
map_h = 700
map_secondary_text = "#dbd8e3"

##, Aggrnyl, Bluyl, haline"

# World choropleth map showing deaths

fig = px.choropleth(
	df,
	locations = "Country/Region",
	locationmode = "country names",
	color = "Confirmed last week",
	hover_name = "Country/Region",
	hover_data = ["WHO Region", "Deaths / 100 Recovered", "Confirmed last week", "Active", "Deaths"],
	#color_continuous_scale = 
	)


#-------------------------------------------------


fig.update_layout(
    #paper_bgcolor=,
    #font_color=,
    #geo=dict(bgcolor=),
    width = map_w,
    height = map_h,

    )


#-------------------------------------------------

# Pre-generating the table for the world-wide values


# App layout using bootstrap

app.layout = dbc.Container([

	# Title row

	dbc.Row([
		dbc.Col(html.H1("Coronavirus World Map",
			className = "text-left my-3 mx-4 title-text",
			style = {
				#"color": colors["text"]
			}
			))
		], className = "title-row"),

	# Graph and Options Row

	dbc.Row([

		# Options column on the left
		

		dbc.Col(width = 2, children = [
			html.H4("Data", className = "text-left mx-3 my-3 title-text"), 	
			dbc.RadioItems(
				id = "column-dropdown",
				value = "Deaths",
				className = "mx-3 radio"
			),


			html.H4("Scope", className = "text-left title-text my-3 mx-3"),
			dbc.RadioItems(
					id = "scope-dropdown",
					value = "world",
					options = [
					{"label": "World", "value": "world"},
					{"label": "Europe",  "value": "europe"},
					{"label": "Asia", "value": "asia"},
					{"label": "Africa", "value": "africa"},
					{"label": "North America", "value": "north america"},
					{"label": "South America", "value": "south america"}
					],
					#labelStyle = {"display": "block"},
					className = "mx-3 radio",
				),

			html.H4("Linearity", className = "text-left title-text my-3 mx-3"),
			dbc.RadioItems(
				value="log",
        	    options=[
        	        {"label": "Linear", "value": "linear"},
					{"label": "Logarithmic", "value": "log"}
        	    ],
        	    id="log-radio",
        	    className = "mx-3 radio"
        	)
        ], className = "left-col rounded-right"),

		# World information table

		dbc.Col(width = 2, className = "left-col rounded mx-3", children = [
			html.H4("World-Wide Statistics", className = "text-left mx-3 my-3 title-text"),
			dbc.Row([
				dbc.Table.from_dataframe(df_sum, striped=True, bordered=False, hover=True)

			]),
		]),

		# Graph column on the right

		dbc.Col(width = 6, className = "left-col rounded-left mx-3", children = [
			dbc.Row(className = "map-title", children = [
				dbc.Col([
					html.H2(id = "graph-title", className = "text-center")
				])
			]),

			dcc.Graph(id="covid-choropleth", className = "float-right", figure=fig,
				config = {
					"showTips": True,
					"scrollZoom": False
				}
			),

		])

	], justify = "around"),

	
], fluid = True	)


# Callback to adjust the map

@app.callback(
	[
		Output("covid-choropleth", "figure"), 
		Output("column-dropdown", "options"),
		Output("graph-title", "children")],

	[
		Input("column-dropdown", "value"),
		Input("log-radio", "value"),
		Input("scope-dropdown", "value")
	 ])
def update_figure(col, log_val, scope):
	new_ops = column_dropdown_options

	if col == None:
		col = "None"

	# Changes the column name if it's logarithmic (all log-plotted cols start with "Log-")

	if log_val == "log" and col != "WHO Region":
		col_name = "Log-" + col
	elif log_val == "linear":
		col_name = col
	elif col == "WHO Region":
		col_name = col

	# New copy of choropleth but with a different column

	fig2 = px.choropleth(
		df,
		locations = "Country/Region",
		locationmode = "country names",
		color = col_name,
		scope = scope,
		hover_name = "Country/Region",
		hover_data = ["WHO Region", "Deaths", "Deaths / 100 Recovered", "Confirmed last week", "Active"],
		color_continuous_scale = "ice"
		)

	# Changes the colour key on the side to reflect the logarithmic scales

	if log_val == "log":
		new_ops = continuous_dropdown_options
		fig2.update_layout(
	    	coloraxis_colorbar = dict(
		    	tickvals = [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
		    	ticktext = [
		    	"-10k",
		    	"-1k",
		    	"-100",
		    	"-10"
		    	"0",
		    	"10",
		    	"100",
		    	"1k",
		    	"10k",
		    	"100k",
		    	"1M",
		    	"10M",
		    	"100M"
		    	]
	    	)
	    )

	    # Updates the layout with coloured background, graph size and removes the title from the key

	fig2.update_layout(
		title_x = 0.5,
		paper_bgcolor="rgba(0,0,0,0)",
		font_color= map_secondary_text,
		geo=dict(bgcolor="rgba(0,0,0,0)"),
		coloraxis_colorbar = {"title": None},
		width = map_w,
		height = map_h,
		margin=dict(l=0, r=20, t=20, b=20)
	)


	return fig2, new_ops, col



if __name__ == "__main__":
	app.run_server(debug=True)
   
from math import pi
import pandas as pd
from bokeh.palettes import Viridis
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.embed import components

#data processing to create pie chart for embedding.
#input is dictionary with keys = categories and values = total price on document

def bokeh_pie_chart(x:dict):
    #bokeh uses as a dictionary to create

        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'category'})
        data['angle'] = data['value']/data['value'].sum() * 2*pi

        try:
                data['color'] = Viridis[len(x)]
        except:
                cols = [Viridis[4][n] for n in range(len(x))]
                data['color'] = cols
        #figure size, effects.
        p = figure(height=350, title="Aggregate Document Chart", toolbar_location=None,
                tools="hover", tooltips="@category: $@value", x_range=(-0.5, 1.0))
        
        p.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend_field='category', source=data)
        p.background_fill_color = "#000000"
        p.border_fill_color = "#000000"
        p.background_fill_alpha= 0.0
        p.border_fill_alpha = 0.0
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        script,div = components(p)
        return script,div


# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 16:40:41 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version: 6.0

This module plots the supplied data into a configuration requested by Evantage module

@functions:
    -convertToMercator - converts the map points into Mercator units
    -route_map - plot given route as a line
    -charge_point_map - plots given charge points as triangles
    -hotels_individual - plot given independent hotels as squares
    -hotels_clusters - plot given  hotel clusters as circles
    -start_stop_point_map - plot given start stop points as diamonds
    -makeMamasterPlot - plot route_map,charge_point_map,hotels_individual,hotels_clusters,start_stop_point_map overlayed for holistic view of route
    -makePatchMap - makes patch maps of pandemic and crime data
    -makeMap - master module that determines which map configuration is to be rendered

@version history:
    -v1- plot simple route map
    -v2- overlay hotels and charge points
    -v3- patch map included
    -v4- separate maps for hotels
    -v5- different map layouts depending on user inputs
    -v6- origin and destination points plotted

"""


import numpy as np
import json

import webbrowser

from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON,get_provider
from bokeh.models import ColumnDataSource,HoverTool,GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import output_file,save,show
from bokeh.layouts import row


def convertToMercator(df, lon, lat):
    r = 6378137 # radius of earth in km
    df.loc[:,"x"] = df[lon] * (r * np.pi/180.0)
    df.loc[:,"y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * r
    return df

    
def route_map(plot,df,leg_label='Route Map',color="#003c7b",line_width=1,alpha=1,Labels=[('pandemic risk index','@riskIndex'),('crime risk index','@crimeRiskIndex')]):
    # convert source
    source=ColumnDataSource(df)
    # use supplied labels to create a line render
    r=plot.line(x='x',y='y',line_width =line_width,source=source,color=color,legend_label=leg_label,alpha=alpha)
    # create tooltip for the render
    routeMapHover = HoverTool(tooltips=Labels,mode='mouse',point_policy='follow_mouse',renderers=[r])
    #associate the tooltip and map
    plot.tools.append(routeMapHover)
    # determine legend
    plot.legend.location = "top_right"
    plot.legend.click_policy="hide"
    
def charge_point_map(plot,df,leg_label='Charge points',size=15,color="#018060",alpha=0.4,displayLabels=[('station name','@station_name'),('EV connector types','@ev_connector_types')]):
    # same as route_map except now the markers are discrete triangles of 15 pixels
    source=ColumnDataSource(df)
    r=plot.triangle(x='x',y='y',size=size,source=source,color=color,alpha=alpha,legend_label=leg_label,hover_color='orange')
    charge_point_hover = HoverTool(tooltips=displayLabels,mode='mouse',point_policy='follow_mouse',renderers=[r])
    plot.tools.append(charge_point_hover)
    plot.legend.location = "top_right"
    plot.legend.click_policy="hide"
    
def hotels_individual(plot,df,leg_label='Hotels - independent',size=10,color="#800080",alpha=0.4,displayLabels=[('name','@names'),('price','@price')]):
    # same as route_map except now the markers are discrete squares of 10 pixels sides
    source=ColumnDataSource(df)
    r=plot.square(x='x',y='y',size=size,source=source,color=color,alpha=alpha,legend_label=leg_label,hover_color='orange')
    hotel_hover = HoverTool(tooltips=displayLabels,mode='mouse',point_policy='follow_mouse',renderers=[r])
    plot.tools.append(hotel_hover)
    plot.legend.location = "top_right"
    plot.legend.click_policy="hide"
    
def hotels_clusters(plot,df,leg_label='Hotel - clusters',size=10,color="#eb3498",alpha=0.4,displayLabels=[('name','@names'),('price','@price')]):
    # same as route_map except now the markers are discrete circles of 10 pixel diameter
    source=ColumnDataSource(df)
    r=plot.circle(x='x',y='y',size=size,source=source,color=color,alpha=alpha,legend_label=leg_label,hover_color='orange')
    hotel_hover = HoverTool(tooltips=displayLabels,mode='mouse',point_policy='follow_mouse',renderers=[r])
    plot.tools.append(hotel_hover)
    plot.legend.location = "top_right"
    plot.legend.click_policy="hide"
    
def start_stop_point_map(plot,df,leg_label='Start stop point',size=20,color="#018060",alpha=1,displayLabels=[('Origin','Origin')]):
    # same as route_map except now the markers are discrete diamonds of 20 pixel
    source=ColumnDataSource(df)
    r=plot.diamond_cross(x='x',y='y',size=size,source=source,color=color,alpha=alpha,hover_color='orange')
    pointHover = HoverTool(tooltips=displayLabels,mode='mouse',point_policy='follow_mouse',renderers=[r])
    plot.tools.append(pointHover)
    
def makeMamasterPlot(routeDf,chargeDf,hotelDf,startName="",stopName="",overWriteFlag=True):
    # convert lat lon to Mercator units as tile map uses mercator units
    routeDf=convertToMercator(routeDf,'lon', 'lat')
    chargeDf=convertToMercator(chargeDf,'lon', 'lat')
    hotelDf=convertToMercator(hotelDf,'lon', 'lat')
     
    # CARTODBPOSITRONis the tile provider - bokeh makes api calls to open street map to get the map details whenr rendering,panning,zooming etc..
    tile_provider=get_provider(CARTODBPOSITRON)
    # set units to mercator
    plot=figure(title = 'Route map',x_axis_type="mercator", y_axis_type="mercator",sizing_mode='scale_width')
    plot.add_tile(tile_provider)
    # plot route as a blue line with annotations
    route_map(plot=plot,
        df=routeDf,
        leg_label='Route Map')
    # plot charge points as triangles
    charge_point_map(plot=plot,
        df=chargeDf ,
        leg_label='Charge points')
    
    hotelIndep=hotelDf[hotelDf['latLonCat']=='D'] # d indicates deep coordinates or indpendent hotels refer hotelScrapper module
    hotelCluster=hotelDf[hotelDf['latLonCat']=='H'] # h indicates high level or city/street level mapping these are a collection of hotels in the neigbourhood
    # if either are empty dont plot
    if(~hotelCluster.empty):
        hotels_clusters(plot=plot,
            df=hotelCluster ,
            leg_label='Hotels - clusters')
    if(~hotelIndep.empty):
        hotels_individual(plot=plot,
            df=hotelIndep ,
            leg_label='Hotels - indpendent')
    # plot origin and destination as red diamonds
    start_stop_point_map(plot=plot,
        df=routeDf.iloc[[0]],
        color="#FF0000",
        leg_label='Origin',
        displayLabels=[('Origin',startName)])
    
    start_stop_point_map(plot=plot,
        df=routeDf.iloc[[-1]],
        color="#FF0000",
        leg_label='Destination',
        displayLabels=[('Destination',stopName)]
        )
    return plot # returns the plot object
    
def makePatchMap(routeDf,data_geo,overWriteFlag=True,title = 'Pandemic Risk Map',palette = brewer['YlGnBu'][8],annotation=['@riskIndex','disp_risk_index']):
    # the data has to be in a json format for patch map to pick to up
    merged_json = json.loads(data_geo.to_json())
    json_data = json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson = json_data)
    # setting the color pallete range
    palette = palette
    palette = palette[::-1]
    
    color_mapper = LinearColorMapper(palette = palette, 
                                     low=0, high =5,
                                     nan_color = '#d9d9d9')
    # setting up hover tooltip with risk indices
    hover = HoverTool(tooltips = [ ('County','@county'),('risk index',annotation[0])])
    
    # declaring a color bar of given orietation and size
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
    border_line_color=None,location = (0,0), orientation = 'horizontal')
    # plotting map and enabling bokeh map toold like pan,zoom and reset,also attempting to match aspect ratio
    plot = figure(title = title,sizing_mode='scale_width',tools = "pan,wheel_zoom,box_zoom,reset",match_aspect=True)
    plot.tools.append(hover)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    # coloring the plot area 
    plot.patches('xs','ys', source = geosource,fill_color = {'field' :annotation[1], 
                                                          'transform' : color_mapper}, 
              line_color = 'black', line_width = 0.25, fill_alpha = 1)
    plot.add_layout(color_bar, 'above')
 
    
    return plot # returns plot
    
# master map module
def makeMap(routeDf,chargeDf,hotelDf,data_geo,startName="",stopName="",overWriteFlag=True,mapConfig={'pandemicMap':False,'crimeMap':False}):
    # creates the tile map of the actual route in all scenarios
    masterPlot=makeMamasterPlot(routeDf,chargeDf,hotelDf,startName,stopName,overWriteFlag)
    if(mapConfig['pandemicMap']&mapConfig['crimeMap']): # render other maps depending on passed user inputs
        pandemicRiskPatchMap=makePatchMap(routeDf,data_geo,overWriteFlag)
        crimeRiskPatchMap=makePatchMap(routeDf,data_geo,overWriteFlag,
                    title = 'Crime Risk Map',
                    palette = brewer['YlOrRd'][8],
                    annotation=['@crimeIndex','disp_crime_index'])
        mapCollection=row(masterPlot, pandemicRiskPatchMap,crimeRiskPatchMap)# save plots into a row object
    elif(mapConfig['pandemicMap']):
        pandemicRiskPatchMap=makePatchMap(routeDf,data_geo,overWriteFlag)
        mapCollection=row(masterPlot, pandemicRiskPatchMap)
    elif(mapConfig['crimeMap']):
        pandemicRiskPatchMap=makePatchMap(routeDf,data_geo,overWriteFlag,
                    title = 'Crime Risk Map',
                    palette = brewer['YlOrRd'][8],
                    annotation=['@crimeIndex','disp_crime_index'])
        mapCollection=row(masterPlot, pandemicRiskPatchMap)
    else:
        mapCollection=masterPlot
    if(~overWriteFlag):
        show(mapCollection) # display the plot immediately if file writing is disabled
        return
    # write to an thml file and then open the file
    output_file("group17_evantage.html")
    save(mapCollection)
    webbrowser.open('group17_evantage.html', new=2)# opens in new browser tab

import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
from bokeh.objects import HoverTool, ColumnDataSource
from collections import OrderedDict
import datetime as dt
   

def loadZipComplaints(ComplaintFile):
	filename =  open(ComplaintFile)
	reader = csv.reader(filename, delimiter = ',')
	headers = reader.next()

	zipIndex = headers.index('Incident Zip')
	latColIndex = headers.index('Latitude')
	lngColIndex = headers.index('Longitude')
	agencyIndex = headers.index('Agency')
	complaintIndex = headers.index('Complaint Type')

	complaintsperzip = {}

	for row in reader:
		try:
			complaint = row[complaintIndex]
			zipcode = row[zipIndex]

			if zipcode in complaintsperzip:
				if complaint in complaintsperzip[zipcode]:
					complaintsperzip[zipcode][complaint] += 1
				else:
					complaintsperzip[zipcode][complaint] = 1
			else:
				complaintsperzip[zipcode] = {}
				complaintsperzip[zipcode][complaint] = 1
		except:
			pass

	return {'zip_complaints': complaintsperzip}

def getZipBorough(zipBoroughFilename):
	filename = open(zipBoroughFilename)
	reader = csv.reader(filename, delimiter = ',')
	reader.next()
	return {row[0]: row[1] for row in reader}

def getMedianIncome(ACSFile):
	filename = open(ACSFile)
	reader = csv.reader(filename, delimiter = ',')
	reader.next()

	income = {}

	for row in reader:
		if row[1] == "":
			income[row[0]] = 0 
		else:
			income[row[0]] = int(row[1])

	return income


def drawPlot(shapeFilename, mapPoints, zipBorough):
	dat = shapefile.Reader(shapeFilename)

	zipCodes = []
	topComplaint = []
	complaintCount= []

	polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [], 'zip': [], 'complaint_type': [], 'complaint_count': []}


	colors = {'Water Quality': '#67001f',
			  'Lead': '#d6604d',
			  'Indoor Air Quality': '#fddbc7' ,
			  'Air Quality': '#f7f7f7' , 
			  'Graffiti': '#92c5de',
			  'Rodent': '#2166ac'}

	record_index = 0

	data = {}

	for r in dat.iterRecords():
		currentZip = r[0]

		if currentZip in zipBorough:

			shape = dat.shapeRecord(record_index).shape
			points = shape.points

			lngs = [p[0] for p in points]
			lats = [p[1] for p in points]

			polygons['lat_list'].append(lats)
			polygons['lng_list'].append(lngs)

			if currentZip in mapPoints['zip_complaints']:
				sortedlist = sorted(mapPoints['zip_complaints'][currentZip].items(), key=operator.itemgetter(1), reverse=True)
				complaintType = sortedlist[0][0]
				complaintCount = sortedlist[0][1]
				
				if complaintType in colors:
					color = colors[complaintType]
				else:
					color = 'white'
			else:
				color = 'white'

			polygons['color_list'].append(color)
			polygons['zip'].append(currentZip)
			polygons['complaint_type'].append(complaintType)
			polygons['complaint_count'].append(complaintCount)
		
		record_index += 1

	source = ColumnDataSource(
		data=dict(
			lng=polygons['lng_list'],
			lat=polygons['lat_list'],
			col=polygons['color_list'],
			zipcode=polygons['zip'],
			complaint=polygons['complaint_type'],
			count = polygons['complaint_count'],
		)
	)

	output_file("ComplaintTypes.html", title = "NYC by Zip" )

	TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,resize,hover"

	patches(polygons['lng_list'], polygons['lat_list'], source=source, \
		fill_color = 'col', line_color='black', alpha = .6, \
		tools=TOOLS, plot_width = 1100, plot_height = 900, \
		title = 'Quality of Life Complaints per Zip Code')

	hover = curplot().select(dict(type=HoverTool))
	hover.tooltips = OrderedDict([
		("Zip Code", "@zipcode"),
		("Complaint Type", "@complaint"),
		("Count", "@count"),
	])

	hold()

	for i, area in enumerate(colors.items()):
		scatter(0, 0, color = area[1], size = .8, legend = area[0])

	show()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0] + '1: [complaints] 2: [zip_borough] 3: [shapefile]'
        print '\ne.g.: ' + sys.argv[0] + ' 311nyc.csv zip_borough.csv shape_data/nyshape.shp'
    else:
    	loadZipComplaints(sys.argv[1])
        mapPoints = loadZipComplaints(sys.argv[1])
        zipBorough = getZipBorough(sys.argv[2])
        drawPlot(sys.argv[3], mapPoints, zipBorough)
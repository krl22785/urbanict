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
	complaintsperzip = {}

	for row in reader:
		try:
			zipcode = row[zipIndex]

			if zipcode in complaintsperzip:
				complaintsperzip[zipcode] += 1
			else:
				complaintsperzip[zipcode] = 1
		except:
			pass

	return {'zip_complaints': complaintsperzip}



def getZipBorough(zipBoroughFilename):
	filename = open(zipBoroughFilename)
	reader = csv.reader(filename, delimiter = ',')
	reader.next()
	return {row[0]: row[1] for row in reader}


def testPlot(shapeFilename, mapPoints, zipBorough):
	hi= max(mapPoints['zip_complaints'].values())
	low= min(mapPoints['zip_complaints'].values())

	for z in mapPoints['zip_complaints']:
		x = int(mapPoints['zip_complaints'][z])
		colorIndex = (10*(x-low)/(hi-low))
		print colorIndex


def drawPlot(shapeFilename, mapPoints, zipBorough):
	dat = shapefile.Reader(shapeFilename)

	zipCodes = []
	complaintCount= []

	polygons = {'lat_list': [], 'lng_list': [], 'zip': [], 'complaint_count': [], "lat_bbox": [], "lng_bbox": [], "size": []}

	palette = ['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061']

	hi = max(mapPoints['zip_complaints'].values())
	low = min(mapPoints['zip_complaints'].values())

	record_index = 0

	data = {}

	for r in dat.iterRecords():
		currentZip = r[0]

		if currentZip in zipBorough:

			shape = dat.shapeRecord(record_index).shape
			points = shape.points

			lngs = [p[0] for p in points]
			lats = [p[1] for p in points]

			bbox = shape.bbox

			lats_box = float((bbox[1] + bbox[3])/2)
			lngs_box = float((bbox[0] + bbox[2])/2)


			polygons['lng_bbox'].append(lngs_box)
			polygons['lat_bbox'].append(lats_box)

			polygons['lat_list'].append(lats)
			polygons['lng_list'].append(lngs)

			polygons['zip'].append(currentZip)
			
			
			if currentZip in mapPoints['zip_complaints']:
				complaints = mapPoints['zip_complaints'][currentZip]
				size = int((float(complaints)/hi) * 25)

			polygons['size'].append(size)
			polygons['complaint_count'].append(complaints)
		
		record_index += 1

	source = ColumnDataSource(
		data=dict(
			lng=polygons['lng_list'],
			lat=polygons['lat_list'],
			zipcode=polygons['zip'],
			count = polygons['complaint_count'],
		)
	)

	output_file("ComplaintTypes.html", title = "NYC by Zip" )

	TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,resize,hover"

	patches(polygons['lng_list'], polygons['lat_list'], source=source, \
		fill_color = "#f7f7f7", line_color='black', \
		tools=TOOLS, plot_width = 1100, plot_height = 900, \
		title = 'Quality of Life Complaints per Zip Code', grid_color='gray')

	hover = curplot().select(dict(type=HoverTool))
	hover.tooltips = OrderedDict([
		("Zip Code", "@zipcode"),
		("Count", "@count"),
	])

	hold()

	scatter(polygons['lng_bbox'], polygons['lat_bbox'], size = polygons['size'], alpha = .5,
		fill_color='#2166ac', color='red', fill_alpha=.75, line_alpha=0.1, tools=TOOLS, plot_width=1100, plot_height=700, name="mapPoints")


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
        #testPlot(sys.argv[3], mapPoints, zipBorough)
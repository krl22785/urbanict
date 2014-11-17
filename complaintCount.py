import csv
import sys
from bokeh.plotting import *
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

def getMedianPopulation(ACSFile):
	filename = open(ACSFile)
	reader = csv.reader(filename, delimiter = ',')
	reader.next()

	population = {}

	for row in reader:
		if row[2] == "":
			population[row[0]] = 0
		else:
			population[row[0]] = int(row[2])

	return population

def drawPlot(mapPoints, zipBorough, zipIncome, zipPopulation):
	
	dataPoint = {'zip': [], 'income': [], 'complaints_total': [], "color_list": [], "size": []}
	palette = ['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061']
	size = [1 , 2, 3, 4, 5, 6, 7, 8, 9, 10]


	hi = max(mapPoints['zip_complaints'].values())
	low = min(mapPoints['zip_complaints'].values())

	hi_pop = max(zipPopulation.values())
	low_pop = min(zipPopulation.values())



	for row in mapPoints['zip_complaints']:
		if row in zipBorough:
			if row in zipIncome:
				if row in zipPopulation:

					zipIncome[row]
					dataPoint['zip'].append(row)
					dataPoint['income'].append(int(zipIncome[row])/1000)
					dataPoint['complaints_total'].append(mapPoints['zip_complaints'][row])
				
					x = int(mapPoints['zip_complaints'][row])
					colorIndex = (10*(x-low)/(hi-low))
					dataPoint['color_list'].append(palette[colorIndex])

					y = int(zipPopulation[row])
					sizeIndex = (10*(y-low_pop)/(hi_pop-low_pop))
					dataPoint['size'].append(size[sizeIndex-1])

	output_file("color_scatter.html", title="color_scatter.py example")
	
	hold()

	scatter(dataPoint['income'], dataPoint['complaints_total'], radius = dataPoint['size'],fill_color = dataPoint['color_list'], \
		title = '311 QOL Complaints Based on Median Income', plot_width = 1100, plot_height = 900, \
		line_color=None, background_fill= '#cccccc', alpha = .6)

	xaxis().axis_label='Median Income (in thousands)'
	yaxis().axis_label='311 QOL Complaints'
	grid().grid_line_color='white'

	text(dataPoint['income'], dataPoint['complaints_total'], text = dataPoint['zip'], text_color='black', text_font_size="8pt", angle = 0)
#
	show()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0] + '1: [complaints] 2: [zip_borough] 3. [income]'
        print '\ne.g.: ' + sys.argv[0] + ' 311nyc.csv zip_borough.csv shape_data/nyshape.shp'
    else:
        mapPoints = loadZipComplaints(sys.argv[1])
        zipBorough = getZipBorough(sys.argv[2])
        zipIncome = getMedianIncome(sys.argv[3])
        zipPopulation = getMedianPopulation(sys.argv[3])
        drawPlot(mapPoints, zipBorough, zipIncome, zipPopulation)














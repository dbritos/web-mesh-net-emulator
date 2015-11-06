#!/usr/bin/python2.7
"""
runs on the server, reads form input, prints HTML
"""
import geohash
from geoindex import GeoGridIndex, GeoPoint
import cgi, sys
import mysql.connector
import string
import cgitb
cgitb.enable()
def get_next(numero):
    numero.sort()
    if numero == []: return  1
    else:
        next_numero = len(numero)
        for i in range(0,len(numero)-1):
            if i <> numero[i+1] - 2:
                next_numero = i+1
                break
        return next_numero + 1


dzoom = {18:0.01,17:0.02,16:0.05,15:0.1,14:0.15,13:0.2,12:0.4,11:0.6,11:0.9,10:1.4,9:2.1,8:3,7:4.5,6:6,5:9,4:9,3:9,2:9,1:9}
db = mysql.connector.connect(user='root',password='dgi', database='mesh')
cursor = db.cursor()
form = cgi.FieldStorage()
print("Content-type: text/html")

head = """
<!DOCTYPE html>
<html>
<head>
	<title>Leaflet.draw vector editing handlers</title>
	<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
	<script src="/libs/leaflet-src.js"></script>
	<link rel="stylesheet" href="/libs/leaflet.css" />

	<script src="/src/Leaflet.draw.js"></script>
	<link rel="stylesheet" href="/dist/leaflet.draw.css" />

	<script src="/src/Toolbar.js"></script>
	<script src="/src/Tooltip.js"></script>

	<script src="/src/ext/GeometryUtil.js"></script>
	<script src="/src/ext/LatLngUtil.js"></script>
	<script src="/src/ext/LineUtil.Intersect.js"></script>
	<script src="/src/ext/Polygon.Intersect.js"></script>
	<script src="/src/ext/Polyline.Intersect.js"></script>


	<script src="/src/draw/DrawToolbar.js"></script>
	<script src="/src/draw/handler/Draw.Feature.js"></script>
	<script src="/src/draw/handler/Draw.SimpleShape.js"></script>
	<script src="/src/draw/handler/Draw.Polyline.js"></script>
	<script src="/src/draw/handler/Draw.Circle.js"></script>
	<script src="/src/draw/handler/Draw.Marker.js"></script>
	<script src="/src/draw/handler/Draw.Polygon.js"></script>
	<script src="/src/draw/handler/Draw.Rectangle.js"></script>


	<script src="/src/edit/EditToolbar.js"></script>
	<script src="/src/edit/handler/EditToolbar.Edit.js"></script>
	<script src="/src/edit/handler/EditToolbar.Delete.js"></script>

	<script src="/src/Control.Draw.js"></script>

	<script src="/src/edit/handler/Edit.Poly.js"></script>
	<script src="/src/edit/handler/Edit.SimpleShape.js"></script>
	<script src="/src/edit/handler/Edit.Circle.js"></script>
	<script src="/src/edit/handler/Edit.Rectangle.js"></script>
	<script src="/src/edit/handler/Edit.Marker.js"></script>
</head>
"""
body = """
<body>
	<div id="map" style="width: 800px; height: 600px; border: 1px solid #ccc"></div>

	<script>
		var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
			osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib});
"""


medio = """
// Initialise the draw control and pass it the FeatureGroup of editable layers
var drawControl = new L.Control.Draw({
	draw: {
            polyline: { },
            polygon: false, 
            rectangle: false,
            circle: false,
            marker: false
        },   
});
map.addControl(drawControl);
		var b24ghz = new L.LayerGroup();
		var b50ghz = new L.LayerGroup();
		var routers = new L.LayerGroup();
		var basemap = {
			"Mapa base":osm
		};
		var overlays = {
			"Routers": routers,
			"Banda 2.4GHz": b24ghz,
			"Banda 5.0GHz": b50ghz
		};
		map.on('draw:created', function(event) {
			var layer = event.layer;
			var eltype  = event.layerType
			var band = "0"
			if (map.hasLayer(b24ghz)) {
				var band = band + "2"
			}
			if (map.hasLayer(b50ghz)) {
				var band = band + "5"
			}
			if (eltype == 'polyline') {
				var lat = layer.getLatLngs()
			}
			if (eltype == 'marker') {
				var lat = layer.getLatLng()
			}
"""


fin = """
</body>
</html>
""" 
print(head)

if 'sid' in form:
	c1,c2 = (-31.36023,-64.26264)
	z = 13
	banda = '025'
	lat = 0
	prop = int(form['sid'].value)
	geo_index = GeoGridIndex()
	cursor.execute ("select origen, destino, frecuencia, calidad from link where propietario='%s'" %(prop))
	datapoint = cursor.fetchall ()

	for p in datapoint:
		lat,lon=geohash.decode(p[0])
		geo_index.add_point(GeoPoint(lat,lon))
		lat,lon=geohash.decode(p[1])
		geo_index.add_point(GeoPoint(lat,lon))

	cursor.execute ("select point, name, ip, numeroenlaces from nodo where propietario='%s'" %(prop))
	datanodo = cursor.fetchall ()
	numero = []
	nodos = {}

	for p in datanodo:
		nodos[p[0]] = p[3]
		numero.append(p[2])
	
	if 'center' in form:
		c1,c2 = (form['center'].value)[7:].rstrip(')').split(',')
		z = form['zoom'].value
	elif lat != 0:
		c1,c2 = lat,lon
	print(body)
	print("map = new L.Map('map', {layers: [osm], center: new L.LatLng(" + str(c1) + "," + str(c2) + "), zoom: " + str(z) + "}),drawnItems = L.featureGroup().addTo(map);")
	print(medio)
	print("			document.location = 'link.py?type=' + eltype + '&sid=" + str(prop) +
						"&point=' + lat + '&banda=' + band + '&center=' + map.getCenter() + '&zoom=' + map.getZoom();")
	print("			drawnItems.addLayer(layer);")
	print("		});")	
else:
	print("<body>")
	print("<p><font color='red'>You need to login first to acced to this page</font></p>")


if 'point' in form and 'sid' in form:
	if form['type'].value == 'polyline':
		o1,o2,d1,d2 = (form['point'].value).split(',')[:4]
		o= o1 + ',' + o2
		d= d1 + ',' + d2
		olati,olongi = o[7:].rstrip(')').split(',')
		dlati,dlongi = d[7:].rstrip(')').split(',')
		center_point = GeoPoint(float(olati),float(olongi))
		z = int(form['zoom'].value)
		distance1 = dzoom[z]
		banda = form['banda'].value
		prop = int(form['sid'].value)
		for npoint, distance in geo_index.get_nearest_points(center_point, 10, 'km'):
			if distance < distance1:
				distance1 = distance
				olati,olongi = str(npoint)[6:].rstrip(')').split(',')
		center_point = GeoPoint(float(dlati),float(dlongi))
		distance1 = dzoom[z]
		for npoint, distance in geo_index.get_nearest_points(center_point, 10, 'km'):
			if distance < distance1:
				distance1 = distance
				dlati,dlongi = str(npoint)[6:].rstrip(')').split(',')
		ogh = geohash.encode(float(olati),float(olongi),15)
		dgh = geohash.encode(float(dlati),float(dlongi),15)
		if string.find(banda,'2') > 0 :
			data = (ogh,dgh, 'b24ghz', 'buena',prop)
			if not(data in datapoint):
				insert_stmt = (
					"INSERT INTO link (origen,destino,frecuencia,calidad,propietario) "
					"VALUES (%s, %s, %s, %s, %s)")
				cursor.execute(insert_stmt,data)
				if ogh in nodos.keys():
					cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces + 1 WHERE point  = '%s'" % (ogh))
					nodos[ogh] = nodos[ogh] + 1
				else:
					next_numero = get_next(numero)
					data = (ogh,'nodo', next_numero, 1,prop)
					insert_stmt = (
						"INSERT INTO nodo (point,name,ip,numeroenlaces,propietario) "
						"VALUES (%s, %s, %s, %s, %s)")
					cursor.execute(insert_stmt,data)
					numero.insert(next_numero-1, next_numero) 
					nodos[ogh] = 1
				if dgh in nodos.keys():
					cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces + 1 WHERE point  = '%s'" % (dgh))
					nodos[dgh] = nodos[dgh] + 1
				else:
					next_numero = get_next(numero)
					data = (dgh,'nodo', next_numero, 1, prop)
					insert_stmt = (
						"INSERT INTO nodo (point,name,ip,numeroenlaces, propietario) "
						"VALUES (%s, %s, %s, %s, %s)")
					cursor.execute(insert_stmt,data)
					numero.insert(next_numero-1, next_numero) 
					nodos[dgh] = 1
				db.commit()
				
		if string.find(banda,'5') > 0 :
			data = (ogh,dgh, 'b50ghz', 'buena', prop)
			if not(data in datapoint):
				insert_stmt = (
					"INSERT INTO link (origen,destino,frecuencia,calidad, propietario) "
					"VALUES (%s, %s, %s, %s, %s)")
				cursor.execute(insert_stmt,data)

				if ogh in nodos.keys():
					cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces + 1 WHERE point  = '%s'" % (ogh))
					nodos[ogh] = nodos[ogh] + 1
				else:
					next_numero = get_next(numero)
					data = (ogh,'nodo', next_numero, 1, prop)
					insert_stmt = (
						"INSERT INTO nodo (point,name,ip,numeroenlaces, propietario) "
						"VALUES (%s, %s, %s, %s, %s)")
					cursor.execute(insert_stmt,data)
					numero.insert(next_numero-1, next_numero) 
					nodos[ogh] = 1

				if dgh in nodos.keys():
					cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces + 1 WHERE point  = '%s'" % (dgh))
					nodos[dgh] = nodos[dgh] + 1
				else:
					next_numero = get_next(numero)
					data = (dgh,'nodo', next_numero, 1, prop)
					insert_stmt = (
						"INSERT INTO nodo (point,name,ip,numeroenlaces, propietario) "
						"VALUES (%s, %s, %s, %s, %s)")
					cursor.execute(insert_stmt,data)
					
				db.commit()

	if form['type'].value == 'click':
		o1,o2,d1,d2 = (form['point'].value).split(',')
		o= o1 + ',' + o2
		d= d1 + ',' + d2
		olati,olongi = o[7:].rstrip(')').split(',')
		dlati,dlongi = d[7:].rstrip(')').split(',')
		ogh = geohash.encode(float(olati),float(olongi),15)
		dgh = geohash.encode(float(dlati),float(dlongi),15)
		banda = form['banda'].value
		if  string.find(banda,'2') > 0 :
			data = (ogh,dgh, 'b24ghz','buena')
			if data in datapoint:
				delete_stmt = "DELETE FROM link WHERE origen = %s AND destino = %s AND frecuencia = %s AND calidad = %s"
				cursor.execute(delete_stmt,data)
				if ogh in nodos.keys():
					if nodos[ogh] > 1:
						cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces - 1 WHERE point  = '%s'" % (ogh))
						nodos[ogh] = nodos[ogh] - 1
					else:
						cursor.execute("DELETE FROM nodo WHERE point = '%s'" % (ogh))
				if dgh in nodos.keys():
					if nodos[dgh] > 1:
						cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces - 1 WHERE point  = '%s'" % (dgh))
						nodos[dgh] = nodos[dgh] - 1
					else:
						cursor.execute("DELETE FROM nodo WHERE point = '%s'" % (dgh))			
			db.commit()
		if string.find(banda,'5') > 0 :
			data = (ogh,dgh, 'b50ghz','buena')
			if data in datapoint:
				delete_stmt = "DELETE FROM link WHERE origen = %s AND destino = %s AND frecuencia = %s AND calidad = %s"
				cursor.execute(delete_stmt,data)
				db.commit()
				if ogh in nodos.keys():
					if nodos[ogh] > 1:
						cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces - 1 WHERE point  = '%s'" % (ogh))
						nodos[ogh] = nodos[ogh] - 1
					else:
						cursor.execute("DELETE FROM nodo WHERE point = '%s'" % (ogh))
				if dgh in nodos.keys():
					if nodos[dgh] > 1:
						cursor.execute("UPDATE nodo SET numeroenlaces = numeroenlaces - 1 WHERE point  = '%s'" % (dgh))
						nodos[dgh] = nodos[dgh] - 1
					else:
						cursor.execute("DELETE FROM nodo WHERE point = '%s'" % (dgh))
		db.commit()

if 'sid' in form:
	prop = int(form['sid'].value)
	cursor.execute ("select origen, destino, frecuencia, calidad from link where propietario='%s'" %(prop))
	datapoint = cursor.fetchall ()
	for p in datapoint:
		olati,olongi = geohash.decode(p[0])
		dlati,dlongi = geohash.decode(p[1])
		poly = str(p[0]) + str(p[1]) 
		freq = str(p[2])
		if freq == 'b24ghz':color = '"green"'
		if freq == 'b50ghz':color = '"blue"'
		print("var polyline" + poly + " = new L.Polyline([[ " + str("{:10.8f}".format(olati)) + "," + str("{:10.8f}".format(olongi)) + "],["
							+ str("{:10.8f}".format(dlati)) + "," + str("{:10.8f}".format(dlongi)) + "]],{color:" + color + "});")
		print(freq + ".addLayer(polyline" + str(poly) + ");")

		print("polyline" + str(poly) + ".on('click', function(event) {")
		print("		var band ='0'")
		print("		if (map.hasLayer(b24ghz)) {")
		print("			var band = band + '2'")
		print("	}")
		print("		if (map.hasLayer(b50ghz)) {")
		print("			var band = band + '5'")
		print("	}")
		print("		var eltype = event.type;")
		print("		var poly = event.target;")
		print("		var lat = poly.getLatLngs();")
		print("		console.log('Polyline was edited!' + eltype + lat);")
		print("		document.location = 'link.py?type=' + eltype + '&sid=" + str(prop) +
					"&point=' + lat + '&banda=' + band + '&center=' + map.getCenter() + '&zoom=' + map.getZoom();")
		print("});")
	cursor.execute ("select point, name, ip, numeroenlaces from nodo where propietario='%s'" %(prop))
	datanodo = cursor.fetchall ()
	for p in datanodo:
		olati,olongi = geohash.decode(p[0])
		poly = str(p[0])
		nn = str(p[2])
		lnn = str(p[3])
		print("var marker" + str(poly) + " = new L.marker([ " + str("{:10.8f}".format(olati)) + "," + str("{:10.8f}".format(olongi)) + "]).addTo(routers);")
		print("marker" + str(poly) + ".bindPopup('IP 192.168.100." + nn + "<br> N de enlaces "  + lnn + "').openPopup();")
	print("L.control.layers(basemap,overlays).addTo(map);")
	print("map.addLayer(routers)")
	if string.find(banda,'2') > 0 :print("map.addLayer(b24ghz)")
	if string.find(banda,'5') > 0 :print("map.addLayer(b50ghz)")
	print("</script>")
	print("<form action='uspas.py' method='post'>")
	print("<input type='hidden' name=sid value=" + str(prop)  +">")
	print("<button type='submit'>Return to menu</button>")
	print("</form>")
	print("<form action='uspas.py' method='post'>")
	print("<button type='submit'>Return to login</button>")
	print("</form>")
print("<p><font color='red'>" + str(numero) + "</font></p>")
print(fin)
cursor.close()
db.close()

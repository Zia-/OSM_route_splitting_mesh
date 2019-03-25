import psycopg2
import osgeo.ogr
connection = psycopg2.connect("host='localhost' dbname='<database_name>' user='<postgres_user>' password='<postgres_password>'")
cursor1 = connection.cursor()
cursor2 = connection.cursor()
xmin = <minimum_longitude_in_decimal_degrees>
ymin = <minimum_latitude_in_decimal_degrees>
xmax = <maximum_longitude_in_decimal_degrees>
ymax = <maximum_latitude_in_decimal_degrees>
xmesh = <x_size_of_desired_mesh_in_degrees>
ymesh = <y_size_of_desired_mesh_in_degrees>
epsg = <EPSG_code_for_WGS84_UTM_zone>
try:
    query = "create table mesh_x_"+str(xmesh).replace(".","_")+"_y_"+str(ymesh).replace(".","_")+"(gid BIGSERIAL PRIMARY KEY); SELECT AddGeometryColumn ('mesh_x_"+str(xmesh).replace(".","_")+"_y_"+str(ymesh).replace(".","_")+"','geom',4326,'POLYGON',2);"
    cursor1.execute(query)
    connection.commit()
    query = "with point as (select st_transform(st_geomfromtext('point("+str(xmin)+" "+str(ymin)+")', 4326), "+str(epsg)+") as geom) select st_x(geom), st_y(geom) from point"
    cursor1.execute(query)
    for i in cursor1:
        xmin = i[0]
        ymin = i[1]
    query = "with point as (select st_transform(st_geomfromtext('point("+str(xmax)+" "+str(ymax)+")', 4326), "+str(epsg)+") as geom) select st_x(geom), st_y(geom) from point"
    cursor1.execute(query)
    for i in cursor1:
        xmax = i[0]
        ymax = i[1]
    print "coordinates in EPSG:3857. xmin %s, ymin %s, xmax %s, ymax %s" % (xmin, ymin, xmax, ymax)
    rows = int((ymax-ymin)/ymesh)+1
    columns  = int((xmax-xmin)/xmesh)+1
    x1 = xmin
    y1 = ymin
    row = 1
    column = 1
    while y1<ymax:
        while x1<xmax:
            x2 = x1 + xmesh
            y2 = y1 + ymesh
            query = "insert into mesh_x_"+str(xmesh).replace(".","_")+"_y_"+str(ymesh).replace(".","_")+" (geom) select st_transform(st_setsrid(st_geomfromtext('polygon(("+str(x1)+" "+str(y1)+", "+str(x2)+" "+str(y1)+", "+str(x2)+" "+str(y2)+", "+str(x1)+" "+str(y2)+", "+str(x1)+" "+str(y1)+"))'), "+str(epsg)+"), 4326)"
            cursor1.execute(query)
            connection.commit()
            x1 = x2
            print "mesh box at %s row and %s column created ( total rows = %s and columns = %s)" % (row, column, rows, columns)
            column += 1
        y1 += ymesh
        x1 = xmin
        print "%s rows completed out of %s rows" % (row, rows)
        row += 1
        column = 1
    print "Completed. Mesh table mesh_x_"+str(xmesh).replace(".","_")+"_y_"+str(ymesh).replace(".","_")+" has been generated inside database with %s rows and %s columns" % (rows, columns)
except:
    print "Oops! Some error has occurred. May be there is already a table named mesh_x_"+str(xmesh).replace(".","_")+"_y_"+str(ymesh).replace(".","_")+" inside database" 

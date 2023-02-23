def convert_to_xyz(lat, lon, radius):

    cosLat = math.cos(lat * math.pi / 180.0)
    sinLat = math.sin(lat * math.pi / 180.0)

    cosLon = math.cos(lon * math.pi / 180.0)
    sinLon = math.sin(lon * math.pi / 180.0)

    x = radius * cosLat * cosLon
    y = radius * cosLat * sinLon
    z = radius * sinLat

    return [x, y, z]

def convert_to_xy(lat, lon):
    x = (lon + 180) * (2048 / 360)
    y = ((lat * -1) + 90) * (1025/180)

    return [x,y]
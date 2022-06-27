import math
import numpy
import serial
import sys


def serial_con():
    ser = serial.Serial(port='COM7', baudrate=19200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)
    return ser


def get_bat():
    s = serial_con()
    s.write(b'%R1Q,5039:\r\n')
    out = str(s.readline().decode('UTF8'))
    f = out.find("%R1P")
    cap = out[f + 11:f + 13]
    print("\nBatterieladung: ", cap, " %")


def beep_single():
    s = serial_con()
    s.write(b'%R1Q,11003:\r\n')


def beep_triple():
    s = serial_con()
    s.write(b'%R1Q,11004:\r\n')


def read():
    sc = serial_con()
    s = str(sc.readline().decode('UTF8'))

    hz = s.find('21.')
    v = s.find('22.')
    sst = s.find('31.')
    ost = s.find('81.')
    nord = s.find('82.')
    h = s.find('83.')
    zph = s.find('87.')

    hzv_check = s[hz + 5]
    if hzv_check != "3":
        print("Winkelmaß falsch eingestellt! Auf 360 Grad dezimal stellen!")
        print("\nHauptmenü: Konfig\Allgemeine Einstellungen\Einheiten und Formate")
        # serRs232.close()
        sys.exit()
    else:
        hz = float(s[hz + 7:hz + 15]) / 100000
        v = float(s[v + 7:v + 15]) / 100000
        sst = float(s[sst + 7:sst + 15]) / 1000
        ost = float(s[ost + 7:ost + 15]) / 1000
        nord = float(s[nord + 7:nord + 15]) / 1000
        h = float(s[h + 7:h + 15]) / 1000
        zph = float(s[zph + 7:zph + 15]) / 1000

        p_list = [hz, v, sst, ost, nord, h, zph]
    return p_list


p = math.radians(90)
r = 0.02    # später auf 0.015 ändern

try:
    serial_con()
    print("\n\nSerielle Verbindung erfolgreich\n")
    beep_single()

except serial.SerialException:
    print("\n\nCOM error:", sys.exc_info()[0])
    sys.exit()

get_bat()

print("\nPunkt Nulllinie")
p_null = read()
print("\nStänder links")
p_sl = read()
print("\nStänder rechts")
p_sr = read()

print("Eingabe Stationskoordinaten")
p_tachy_ost = float(input("Ost: (float)"))
p_tachy_nord = float(input("Nord: (float)"))
p_tachy = [p_tachy_ost, p_tachy_nord]
print("p_tachy: " + str(p_tachy))

x1 = numpy.array([p_sl[0] - p_tachy[0], p_sl[1] - p_tachy[1]])
y1 = numpy.array([p_sr[0] - p_tachy[0], p_sr[1] - p_tachy[1]])
dot1 = numpy.dot(x1, y1)
x_modulus1 = numpy.sqrt((x1 * x1).sum())
y_modulus1 = numpy.sqrt((y1 * y1).sum())

cos_angle1 = dot1 / x_modulus1 / y_modulus1
print("cos_angle1: " + str(cos_angle1))
angle1 = numpy.arccos(cos_angle1)  # Winkel in Radiant
print("angle1: " + str(angle1))
sin_angle1 = numpy.sin(angle1)
print("sin_angle1: " + str(sin_angle1))

v = math.sqrt((p_sl[3] - p_tachy[0])**2+(p_sl[4] - p_tachy[1])**2)
print("v: " + str(round(v, 3)))
a = cos_angle1 * v
print("a: " + str(round(a, 3)))

z2 = math.radians(p_null[1])
print("z2: " + str(z2))
z2 = z2 - p
print("z2: " + str(z2))
z2_deg = z2 * (180/math.pi)
print("z2 deg: " + str(round(z2_deg, 5)))
i = a * math.tan(z2)
print("i: " + str(round(i, 3)))

print("Latte")
z = read()
z1 = z[1]
print("z1: " + str(z1))
z1 = math.radians(z1)
alpha = math.radians(90) - z1

b = a * math.tan(alpha)
y = r * math.tan(alpha / 2)
y_mm = round(y * 1000, 3)
print("\ny: " + str(y_mm) + " mm")
x = y * math.tan(alpha)
print("x: " + str(round(x * 1000, 3)) + " mm")

h = i + b - x
h = round(h, 3)
print("\nHöhe: " + str(h) + " m")

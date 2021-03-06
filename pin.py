#!/usr/bin/python

# Raspberry Pi pin configuration:
lcd_rs        = 25  # GPIO
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 22
lcd_d6        = 18
lcd_d7        = 17

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

#    3V3  (1) (2)  5V
#  GPIO2  (3) (4)  5V
#  GPIO3  (5) (6)  GND
#  GPIO4  (7) (8)  GPIO14
#    GND  (9) (10) GPIO15
# GPIO17 (11) (12) GPIO18
# GPIO27 (13) (14) GND
# GPIO22 (15) (16) GPIO23
#    3V3 (17) (18) GPIO24
# GPIO10 (19) (20) GND
#  GPIO9 (21) (22) GPIO25
# GPIO11 (23) (24) GPIO8
#    GND (25) (26) GPIO7
#  GPIO0 (27) (28) GPIO1
#  GPIO5 (29) (30) GND
#  GPIO6 (31) (32) GPIO12
# GPIO13 (33) (34) GND
# GPIO19 (35) (36) GPIO16
# GPIO26 (37) (38) GPIO20
#    GND (39) (40) GPIO21


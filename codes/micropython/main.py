# coding: utf-8


# WiFi network _________________________
def wait_for_wifi():
    import network

    network.WLAN(network.AP_IF).active(False)
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        # sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            pass			
	
    print('Network configuration:', sta_if.ifconfig())


wait_for_wifi()


# Signal boot successfully ___________
import led
led.blink_on_board_led(times = 2)

# Display ____________________________

import display_ssd1306_i2c as display
display = display.Display(width = 128, height = 32)
import ntp_clock
ntp_clock.Clock(display).run()

# import machine
# import ws2812_clock
# pin_np = machine.Pin(13, machine.Pin.OUT)
# display = ws2812_clock.Clock(data_pin = pin_np,
#                              pixels_count = 60,
#                              start_idx = 30,
#                              bar_mode = True)
# import ntp_clock
# ntp_clock.Clock(display).run()

# import wf8266kd
# display = wf8266kd.WF8266KD()
# import ntp_clock
# ntp_clock.Clock(display).run()

# import wf8266t
# display = wf8266t.WF8266T()
# import ntp_clock
# ntp_clock.Clock(display, buzzer = display.buzzer).run()

# import max_matrices
# display = max_matrices.Matrices()
# import ntp_clock
# ntp_clock.Clock(display).run()

# import qs30_1
# display = qs30_1.QS30_1(columns = 1, intensity = 0)
# import ntp_clock
# ntp_clock.Clock(display).run()

# as MQTT node _______________________
# import node
# node.main()

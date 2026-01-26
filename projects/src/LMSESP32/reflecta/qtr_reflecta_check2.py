from machine import ADC, Pin
import time

adc1 = ADC(Pin(26))
adc2 = ADC(Pin(27))
adc1.atten(ADC.ATTN_11DB)
adc2.atten(ADC.ATTN_11DB)

while True:
    print(adc1.read(), adc2.read())
    time.sleep_ms(100)

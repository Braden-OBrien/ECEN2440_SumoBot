import time

def sample_battery(bat_sample_time, pin, ref_pin=None, adc_ref=3.3, vol_div=3):
    bat_samples = []
    #ref_samples = []
    start_time = time.ticks_ms()
    while (time.ticks_ms() - start_time < bat_sample_time):
        bat_samples.append(pin.read_u16())
        #ref_samples.append(ref_pin.read_u16())
        
    return vol_div*adc_ref*(sum(bat_samples)/len(bat_samples))/65535
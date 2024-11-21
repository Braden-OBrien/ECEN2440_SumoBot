import time

def sample_battery(bat_sample_time, pin, ref_pin=None, adc_ref=3.3, vol_div=3, phys_offset=0.2423):
    """
    Samples the battery for specified time at the specified ADC pin:
        bat_sample_time: time (in ms) to sample the battery
        pin: ADC pin input for sampling
        adc_ref: the voltage value connected to ADC_REF pin. 3.3V by default
        vol_div: the voltage divider multiplier. In our case we have our battery voltage divided to a third for sampling
        phys_offset: the offset by the physical system. This is a measured value dependent on resistor values/gnd offset
    """
    bat_samples = []
    #ref_samples = []
    start_time = time.ticks_ms()
    while (time.ticks_ms() - start_time < bat_sample_time):
        bat_samples.append(pin.read_u16())
        #ref_samples.append(ref_pin.read_u16())
        
    return vol_div*adc_ref*(sum(bat_samples)/len(bat_samples))/65535
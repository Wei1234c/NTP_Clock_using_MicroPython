import socket
import ustruct as struct
import time


def getNTPTime(host = "pool.ntp.org", CLIENT_RECEIVE_TIME_OUT_SECONDS = 30):
        
    port = 123
    buf = 1024
    msg = b'\x1b' +  b'\0' * 47

    address = socket.getaddrinfo(host,port)[-1][-1]        
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
    
    client.sendto(msg, address)
        
    client.settimeout(CLIENT_RECEIVE_TIME_OUT_SECONDS)         
    msg, address = client.recvfrom(buf)
    
    ntp_time = struct.unpack( "!12I", msg )[10]
    
    # reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800 # 1970-01-01 00:00:00    
    ntp_time -= TIME1970
    
    return ntp_time 
    
        
def set_upython_RTC(current_time):
    # convert format from time.localtime to machine.RTC().datetime()
    current_time = current_time[:3] + (current_time[-2],) + current_time[-5:-2] + (0,)  
    
    import machine
    # (year, month, day, weekday, hours, minutes, seconds, subseconds)
    machine.RTC().datetime(current_time)
    
    
def calibrate_time_upython():
    try:
        ntp_time = getNTPTime()
        u_python_base_time = 946656000  # 1486641774 - 539985774    
        ntp_time -= u_python_base_time  
        
        # (year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])
        current_time = time.localtime(ntp_time)    
        set_upython_RTC(current_time)
        print('\n[Time calibrated]\n')
    except Exception as e:
        print('\n[Time calibration failed]\n')
        print(e)

    
if __name__ == "__main__":
   print('Current Time:', calibrate_time_upython())
   # print('Current Time:', calibrate_time_cpython())
            

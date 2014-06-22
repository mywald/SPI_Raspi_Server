import spidev
import time
import RPi.GPIO as GPIO

#Function to send Data to RFM12B
def send (spi, cmd, txt):
 print "Sending: " + str(cmd) + "=" + txt
 response = spi.xfer2(cmd)
 print "Received: " + str(response)
 return response

def isReadyToSend ():
  resp = GPIO.input(18)
  print "nIRQ: " + str(resp)
  return resp == 1
  
def sendDataByte (spi, data, text): 
  sendRegisterExpectsByte = False
  while not sendRegisterExpectsByte:
#  while isReadyToSend(): 
    stat = send(spi, [0x00,0x00], "Read Status register")
#    send(spi, [0x80,0x08], "Disable FIFO Register")
#    send(spi, [0x80,0xD8], "Enable FIFO Register")
    sendRegisterExpectsByte = stat[0] & 0b10000000
#    time.sleep(0.0001)

  send(spi, [0xB8,data], text)
  return

def sendDataToAddress (address, data): 
    print "---------------"

    while not isReadyToSend():
      print "wait till no interrupt present"
      time.sleep(0.1)
      send(spi, [0x00,0x00], "Read Status register")
      send(spi, [0x80,0x08], "Disable FIFO Register")
      send(spi, [0x80,0xD8], "Enable FIFO Register")

    send(spi, [0x82,0x38], "enable transmitter, enable xtal, enable PLL synthesizer")

    sendDataByte(spi, 0xAA, "PREAMBLE senden")
    sendDataByte(spi, 0xAA, "PREAMBLE senden")
    sendDataByte(spi, 0xAA, "PREAMBLE senden")
    sendDataByte(spi, 0x2D, "HI Byte senden")
    sendDataByte(spi, 0xD4, "LOW Byte for Frame-Detection senden")

    sendDataByte(spi, address, "Adresse als Nutzdaten-Byte senden")
    sendDataByte(spi, address, "Adresse als Nutzdaten-Byte senden")
    sendDataByte(spi, address, "Adresse als Nutzdaten-Byte senden")
    sendDataByte(spi, data, "Nutzdaten Byte senden")
    sendDataByte(spi, data, "Nutzdaten Byte senden")
    sendDataByte(spi, data, "Nutzdaten Byte senden")

    sendDataByte(spi, 0xAA, "PREAMBLE senden")
    sendDataByte(spi, 0xAA, "PREAMBLE senden")

#    time.sleep(0.1)

    send(spi, [0x82,0x08], "turn off transmitter")
    send(spi, [0x00,0x00], "Read Status register")
    return

#Configrue GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN)

#Configure RFM12B
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=(10000000)
spi.cshigh=False 
print "Hz: "+str(spi.max_speed_hz)
print "LSB first: "+str(spi.lsbfirst)
try: 
 send(spi, [0x00,0x00], "Read status register")
 send(spi, [0x80,0xD8], "Enable send and receive Registers, 433MHz, 12.5pF")
 send(spi, [0x82,0x08], "enable xtal")
 #send(spi, [0xC6,0x47], "Bitrate")
 send(spi, [0xA6,0x40], "Frequency")
# send(spi, [0xC6,0x23], "Bitrate 9.6kBit")
# send(spi, [0xC6,0xFF], "Bitrate 1.34kBit")
 send(spi, [0xC6,0xA0], "Bitrate")
 #Empfaengersteuerung
 #send(spi, [0x94,0xA0], "VDI, Fast, 134kHz, 0dBm,-103dBm")
 send(spi, [0x94,0xC0], "VDI, Fast, 67kHz, 0dBm,-103dBm")
 send(spi, [0xC2,0xAC], "Data Filter & Clock Recovery")
 #send(spi, [0xCC,0x77], "Taktgenerator")
 send(spi, [0xCC,0x76], "Taktgenerator")
 #Sendersteuerung
 send(spi, [0xCA,0x83], "FIFO8, SYNC")
 send(spi, [0xCE,0xD4], "Synch Pattern")
 send(spi, [0xC4,0x87], "Auto Frequency Control")
 send(spi, [0x98,0x20], "!mp,Frequenzhub=45khz, MAX OUT")
 #send(spi, [0x98,0x50], "!mp,9810=30kHz, MAX OUT")
 send(spi, [0xE0,0x00], "Wakeup Timer not used")
 send(spi, [0xC8,0x00], "Low Duty cycle Not use")
 send(spi, [0xC0,0x00], "1.0MHz, 2.2V")
 time.sleep(0.1)
 send(spi, [0x00,0x00], "Read Status register")
 while True: 
    sendDataToAddress(0x23, 0x99)
    time.sleep(5)
    sendDataToAddress(0x23, 0x88)
    time.sleep(5)
except KeyboardInterrupt:
 spi.close() 

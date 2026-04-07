from machine import Pin, PWM, ADC
import _thread
import time

bz = PWM(Pin(19))
bz.duty(0)

adc1= ADC(Pin(34))
adc2= ADC(Pin(14))
adc1.width(ADC.WIDTH_12BIT)
adc2.width(ADC.WIDTH_10BIT)
adc1.atten(ADC.ATTN_11DB)

servoL= PWM(Pin(15), freq=50) 
servoU= PWM(Pin(4), freq=50)

ledr=Pin(23,Pin.OUT)
ledv=Pin(22,Pin.OUT)
btn1=Pin(21,Pin.IN,Pin.PULL_DOWN)
btn2=Pin(18,Pin.IN,Pin.PULL_DOWN)


modoreset= False
modoauto= False 

def interupauto(pin):
    global modoauto
    modoauto= True
btn1.irq(trigger=Pin.IRQ_RISING,handler=interupauto)

def interupreset(pin):
    global modoreset
    modoreset= True
btn2.irq(trigger=Pin.IRQ_RISING,handler=interupreset)

def mover_servoL(angulo):
    """
    Convierte el ángulo (0° a 180°) en el ciclo útil (duty) apropiado.
    Duty para ESP32 (0-1023 o 0-65535 según versión).
    """
    # Mapear el ángulo al duty (ajustar valores según el servo)
    min_duty = 26 # ~0.5 ms
    max_duty = 127  # ~2.5 ms
    duty = min_duty + (angulo / 180) * (max_duty - min_duty)
    servoL.duty(int(duty))
def mover_servoU(angulo):
    # Mapear el ángulo al duty (ajustar valores según el servo)
    min_duty = 26   # ~0.5 ms
    max_duty = 127   # ~2.5 ms
    duty = min_duty + (angulo / 180) * (max_duty - min_duty)
    servoU.duty(int(duty))
# Prueba: barrido de 0° a 180° y de regreso


def rebote(pin,debounce_ms=50):
  if pin.value()==1:
    time.sleep_ms(debounce_ms)
    if pin.value()==1:
      return True
  return False   
# Automatica 
def automaticaRe():
    raw1= adc1.read()
    raw2= adc2.read()
    val1 = (raw1/4095)*180
    val2= (raw2/1023)*180
    ledr.value(1)
    ledv.value(0)
    print ('Modo Reinicio')
    while val1 >0 or val2>0:
        if val1 > 0:
            val1-=10
            if val1<0:
                val1=0
        if val2>0:
            val2-=10
            if val2<0:
                val2=0
        mover_servoL(val1)
        mover_servoU(val2)
        print("ServoL:",val1, "| ServoU:",val2)
        time.sleep_ms(1000)
    ledr.value(0)
    ledv.value(1)
    print('Reinicio Completad0 * Volviendo a modo manual ')
    global modoreset 
    modoreset= False


def reproducir_melodia():
    notas = [330,523,330,523,330,523,330,523,330,523,330]
    duraciones = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

    for f,t in zip(notas, duraciones):
        bz.duty(512)
        bz.freq(f)
        time.sleep(t)
        bz.duty(0)
        time.sleep(0.05)


# Automatica Secuencia 
def secuencia_auto():
    secuencia=[    
        (90,45), # son todos los pasos que va hacer los servos 
        (30,130),
        (120,50),
        (180,180),
        (0,0),
        ]
    ledr.value(1)
    ledv.value(0)
    print ('Modo Automatio Iniciado')
    for (L,U) in secuencia:
        mover_servoL(L)
        mover_servoU(U)
        print("ServoL:",L, "| ServoU:",U)
        time.sleep_ms(1000)
    ledr.value(0)
    ledv.value(1)
    print('Rutina Completada * Volviendo a modo manual ')
    global modoauto
    modoauto= False

def buz_secuencia():
    _thread.start_new_thread(reproducir_melodia, ())
    secuencia_auto()
    time.sleep(0.5)
def buz_reinicio():
    _thread.start_new_thread(reproducir_melodia, ())
    automaticaRe()
    time.sleep(0.5)
# para sincronizar con el ultimo movimiento 
raw1= adc1.read()
raw2= adc2.read()
val1 = (raw1/4095)*180
val2= (raw2/1023)*180
mover_servoL(val1)
mover_servoU(val2)

ledv.value(1) # inicia en modo manual 

while True:
    if modoauto:
        modoauto= False # resetea la bandera 
        if rebote(btn1):
            buz_secuencia()
    elif modoreset:
        modoreset= False # resetea la bandera 
        if rebote(btn2):
            buz_reinicio()
    else:
        raw1= adc1.read()
        raw2= adc2.read()
        val1 = (raw1/4095)*180
        val2= (raw2/1023)*180
        print("1 ",val1,"\n 2 ",val2)
        mover_servoL(val1)
        mover_servoU(val2)
        time.sleep_ms(100)
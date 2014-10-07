#include "mbed.h"

Serial pc(USBTX, USBRX); // tx, rx

AnalogIn steering_pot(p15);
AnalogIn batt24(p16);
AnalogIn batt48(p17);
AnalogOut throttle(p18);

DigitalOut break_(p11);
DigitalOut direction(p12);
DigitalOut power_en(p13);

InterruptIn throttle_in(p21); // 주황
InterruptIn elev_in(p23); //굵은흰색, 얆은 흰색은 5v
InterruptIn rudo_in(p24); //파랑

DigitalOut motor_on_relay(p30); // brake 용

DigitalOut led1(LED1); // RX LED
DigitalOut led2(LED2); // TX LED
DigitalOut led4(LED4); // DEBUG LED


void init_relay_brake()
{
  motor_on_relay = 0;
  led4 = 0;
}

Timer motor_on_relay_timer;
int relay_on_delay_second = 1;
float motor_throttle = 0.0;

Timer motor_off_relay_timer;
int relay_off_delay_second = 2.5;
 
// void throttle_set_(float _throttle)
// {
//   // motor relay on
//   // wait 2 // if already relay on, do not need wait
// //  if (motor_on_relay == 0) {
//  //   motor_on_relay = 1;
//   //   wait(relay_on_delay_second);
//    //} else {
//     // motor_on_relay = 1;
//    //}
//  
//   motor_on_relay = 1;
//   wait(relay_on_delay_second);
//   throttle = _throttle;
//   led4 = 1;
// }

void throttle_set(float _throttle)
{
  motor_on_relay = 1;
  motor_throttle = _throttle; // it just save for delayed throttle.
  motor_on_relay_timer.start();
}

void throttle_clear_()
{
  throttle = 0;
  led4 = 0;
  wait(relay_on_delay_second*1.5);
  motor_on_relay = 0;
}

void throttle_clear()
{
  throttle = 0;
  led4 = 0;
  // wait 2
  // relay off
  // wait(relay_on_delay_second*1.5);
  // motor_on_relay = 0;
  motor_off_relay_timer.start();
}

void relay_break_process() {
  if (motor_on_relay_timer.read_ms() >= relay_on_delay_second*1000) {
    throttle = motor_throttle;
    led4 = 1;
    motor_on_relay_timer.stop();
    motor_on_relay_timer.reset();
  }
  if (motor_off_relay_timer.read_ms() >= relay_off_delay_second*1000) {
    motor_on_relay = 0;
    motor_off_relay_timer.stop();
    motor_off_relay_timer.reset();
 }
}

void push(float _throttle) 
{
  break_ = 0;
  direction = 0;
  wait(0.02);
  // throttle = _throttle;
  throttle_set(_throttle);
}

void _stop()
{
  break_ = 0;
  wait(0.04);
  direction = 0;
  // throttle = 0;
  throttle_clear();
}

void _break()
{
  direction = 0;
  break_ = 1;
  // throttle = 0;
  throttle_clear(); // 필요 없을듯. 이건 체크 필요.
  wait(0.02);
}

void relay_on()
{
  direction = 0;
  // break_ = 1;
  throttle = 0;
  motor_on_relay = 1;
}

void pull(float _throttle)
{
  break_ = 0;
  direction = 1;
  wait(0.04);
  // throttle = _throttle;
  throttle_set(_throttle);
}

void Tx_interrupt();
void Rx_interrupt();
void send_line();
void read_line();
 
 
// Circular buffers for serial TX and RX data - used by interrupt routines
const int buffer_size = 255;
// might need to increase buffer size for high baud rates
char tx_buffer[buffer_size];
char rx_buffer[buffer_size];
// Circular buffer pointers
// volatile makes read-modify-write atomic 
volatile int tx_in=0;
volatile int tx_out=0;
volatile int rx_in=0;
volatile int rx_out=0;
// Line buffers for sprintf and sscanf
char tx_line[80];
char rx_line[80];
 
// Copy tx line buffer to large tx buffer for tx interrupt routine
void send_line() {
    int i;
    char temp_char;
    bool empty;
    i = 0;
// Start Critical Section - don't interrupt while changing global buffer variables
    NVIC_DisableIRQ(UART1_IRQn);
    empty = (tx_in == tx_out);
    while ((i==0) || (tx_line[i-1] != '\n')) {
// Wait if buffer full
        if (((tx_in + 1) % buffer_size) == tx_out) {
// End Critical Section - need to let interrupt routine empty buffer by sending
            NVIC_EnableIRQ(UART1_IRQn);
            while (((tx_in + 1) % buffer_size) == tx_out) {
            }
// Start Critical Section - don't interrupt while changing global buffer variables
            NVIC_DisableIRQ(UART1_IRQn);
        }
        tx_buffer[tx_in] = tx_line[i];
        i++;
        tx_in = (tx_in + 1) % buffer_size;
    }
    if (pc.writeable() && (empty)) {
        temp_char = tx_buffer[tx_out];
        tx_out = (tx_out + 1) % buffer_size;
// Send first character to start tx interrupts, if stopped
        pc.putc(temp_char);
    }
// End Critical Section
    NVIC_EnableIRQ(UART1_IRQn);
    return;
}
 
 
// Read a line from the large rx buffer from rx interrupt routine
void read_line() {
    int i;
    i = 0;
// Start Critical Section - don't interrupt while changing global buffer variables
    NVIC_DisableIRQ(UART1_IRQn);
// Loop reading rx buffer characters until end of line character
    while ((i==0) || (rx_line[i-1] != '\r')) {
// Wait if buffer empty
        if (rx_in == rx_out) {
// End Critical Section - need to allow rx interrupt to get new characters for buffer
            NVIC_EnableIRQ(UART1_IRQn);
            while (rx_in == rx_out) {
            }
// Start Critical Section - don't interrupt while changing global buffer variables
            NVIC_DisableIRQ(UART1_IRQn);
        }
        rx_line[i] = rx_buffer[rx_out];
        i++;
        rx_out = (rx_out + 1) % buffer_size;
    }
// End Critical Section
    NVIC_EnableIRQ(UART1_IRQn);
    rx_line[i-1] = 0;
    return;
}
 
 
// Interupt Routine to read in data from serial port
void Rx_interrupt() {
    led1=1;
// Loop just in case more than one character is in UART's receive FIFO buffer
// Stop if buffer full
    while ((pc.readable()) && (((rx_in + 1) % buffer_size) != rx_out)) {
        rx_buffer[rx_in] = pc.getc();
// Uncomment to Echo to USB serial to watch data flow
//        monitor_pc.putc(rx_buffer[rx_in]);
        rx_in = (rx_in + 1) % buffer_size;
    }
    led1=0;
    return;
}
 

// Interupt Routine to write out data to serial port
void Tx_interrupt() {
    led2=1;
// Loop to fill more than one character in UART's transmit FIFO buffer
// Stop if buffer empty
    while ((pc.writeable()) && (tx_in != tx_out)) {
        pc.putc(tx_buffer[tx_out]);
        tx_out = (tx_out + 1) % buffer_size;
    }
    led2=0;
    return;
}

bool newline_detected = false;

void init_serial_interrupt()
{
  pc.baud(9600);
  pc.attach(&Rx_interrupt, Serial::RxIrq);
  pc.attach(&Tx_interrupt, Serial::TxIrq);
}

// void wait_for_new_command()
// {
  // while (! newline_detected ) ;    
// }

typedef enum {
  PUSH,
  PULL,
  TURN_RIGHT,
  TURN_LEFT,
  STOP,
  BREAK,
  RELAY
} COMMAND_t;

COMMAND_t parse_command(char* line) 
{
  if (line[0] == 'w')
    return PUSH;
  if (line[0] == 'x')
    return PULL;
  if (line[0] == 'd')
    return TURN_RIGHT;
  if (line[0] == 'a')
    return TURN_LEFT;
  if (line[0] == 's')
    return STOP;
  if (line[0] == 'b')
    return BREAK;
  if (line[0] == 'r')
    return RELAY;
}

int parse_args(char* line)
{
  char* buf = line+2;
  int r = 0;
  char c = *buf;
  if ( 0 <= c && c <= '9')
    r = c - '0';
  *buf++;
  while ( '0'<= *buf && *buf <= '9') {
    r = r*10 + (*buf++ - '0');
  }
  return r;
}

void execute(COMMAND_t cmd, int value)
{
  
  float throttle = float(value) * 0.01; // value range is 0-100, throttle range is 0~1.0
  if (cmd == STOP)
    _stop();
  if (cmd == PUSH)
    push(throttle); 
  if (cmd == PULL)
    pull(throttle);
  if (cmd == TURN_RIGHT || cmd == TURN_LEFT)
    push(throttle);
  if (cmd == BREAK)
    _break();
  if (cmd == RELAY)
    relay_on();
}

int read_voltage24()
{
  // return batt24 = (2.4/3.3)
  float x;
  x = batt24;
  x = batt24;
  x = batt24;
  return int(batt24*330.0); // if batt24 is 24voltage, then return 240
}
int read_voltage48()
{
  // return batt48 = ((48*3/54)/3.3)
  // batt48 *3.3*54.0/3.0 * 10
  float x;
  x = batt48;
  x = batt48;
  x = batt48;
  return int(batt48*594.0); // if batt48 is 48voltage, then return 480
}

int read_pot()
{ 
  float x;
  x = steering_pot;
  x = steering_pot;
  x = steering_pot;
  return int(steering_pot*330.0); // if pot is 3.3voltage, then return 330
}

Timer throttle_timer;           // define timer object
int throttle_in_count = 0;

void throttle_in_rise() {
  throttle_timer.reset();
}

void throttle_in_fall() {
  throttle_in_count = throttle_timer.read_us();
  throttle_timer.reset();
}

Timer rudo_timer;           // define timer object
int rudo_in_count = 0;

void rudo_in_rise() {
  rudo_timer.reset();
}

void rudo_in_fall() {
  rudo_in_count = rudo_timer.read_us();
  rudo_timer.reset();
}

Timer elev_timer;           // define timer object
int elev_in_count = 0;

void elev_in_rise() {
  elev_timer.reset();
}

void elev_in_fall() {
  elev_in_count = elev_timer.read_us();
  elev_timer.reset();
}

void init_rc()
{
    throttle_timer.start();     // start timer counting
    throttle_in.rise(&throttle_in_rise);  // attach the address of the flip function to the rising edge
    throttle_in.fall(&throttle_in_fall);  // attach the address of the flip function to the rising edge

    rudo_timer.start();     // start timer counting
    rudo_in.rise(&rudo_in_rise);
    rudo_in.fall(&rudo_in_fall);

    elev_timer.start();     // start timer counting
    elev_in.rise(&elev_in_rise);
    elev_in.fall(&elev_in_fall);
}

Ticker tx_ticker;

void tx_emitter_task() 
{
    sprintf(tx_line,"%d,%d,%d,%d,%d,%d\r\n",read_pot(), read_voltage24(), read_voltage48(), throttle_in_count, rudo_in_count, elev_in_count);
    send_line();
}

void init_tx_emitter() 
{
  tx_ticker.attach(&tx_emitter_task, 0.3);
}

Ticker delayed_break_ticker;

void delayed_break_task() 
{
    relay_break_process();
}

void init_relay_brake_ticker() 
{
  delayed_break_ticker.attach(&delayed_break_task, 0.1);
}

int main() {
  int i=0;
  int rx_i=0;
  COMMAND_t command;
  int args;

  init_rc();
  init_serial_interrupt();
  init_tx_emitter();

  init_relay_brake();
  init_relay_brake_ticker();

  while(1) {
    read_line();
    command = parse_command(rx_line);
    args = parse_args(rx_line);
    execute(command, args);
  }

  return 0;
}

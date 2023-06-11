
PROCESSOR 10F200

; PIC10F200 Configuration Bit Settings

; Assembly source line config statements

; CONFIG
  CONFIG  WDTE = OFF            ; Watchdog Timer (WDT disabled)
  CONFIG  CP = OFF              ; Code Protect (Code protection off)
  CONFIG  MCLRE = OFF           ; Master Clear Enable (GP3/MCLR pin fuction is digital I/O, MCLR internally tied to VDD)

; config statements should precede project file includes.
#include <xc.inc>


PSECT resetVect, class=CODE, delta=2
resetVect:
    PAGESEL main
    goto main
    
    
PSECT code, delta=2
main:
    
    movlw 0b00001100 ; first four zeros are irrelevent. 
		     ; last four GP3, GP2, GP1, GP0
		     ; 1 will set to input, 0 will set to output
		     ; GP3 is input only.
       
    tris 6 ;the 6 sets tris to the value stored in W
    nop
    


mainloop:
    bcf GP0 ; sets the output to low
    call HOLDloop ;loops for a low signal form the UART
    movlw 4   ;This should delay about 0.4 ms --4^3/153600 s--
    call delay
    bsf GP0
    call HOLDloop
    movlw 4
    call delay
    nop
    goto mainloop
    nop

    
HOLDloop:
    btfsc GP2 ; the transmit line in UART rests in the high state. 
    goto HOLDloop
    retlw 0
    
    
delay: ; this is a three-layer nested loop.
    movwf 0x12
out_out_loop:
    movwf 0x11
outer_loop:
    movwf 0x10
delay_loop:
    decfsz 0x10, 1
    goto delay_loop
    decfsz 0x11, 1
    goto outer_loop
    decfsz 0x12, 1
    goto out_out_loop
    retlw 0 ; the return sets the working register to zero. 
    nop
    
END resetVect 

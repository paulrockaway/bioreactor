/*
MSP430 Code
 */

#include <msp430g2553.h>		

#define FALSE 0
#define TRUE 1

#define manifoldA BIT1
#define manifoldB BIT2
#define manifoldC BIT3
#define manifoldD BIT4

#define wastepumps BIT7
#define reactorApump BIT6
#define reactorBpump BIT5
#define reactorCpump BIT4
#define reactorDpump BIT3

int state = 0;
char statelist[4] = {'A','B','C','D'};
int currentreading =0;
char outlist[5];
int ON = 0;
int pwmcounter = 0;

const unsigned long smclk_freq = 16000000;      // SMCLK frequency in hertz
const unsigned long bps = 9600;                 // Async serial bit rate

char readlist[27];

int wastepwr = 0;

int reactorAthreash = 0;
int reactorApwr = 0;
int reactorAonpwr = 0;
int reactorAoffpwr = 0;

int reactorBthreash = 0;
int reactorBpwr = 0;
int reactorBonpwr = 0;
int reactorBoffpwr = 0;

int reactorCthreash = 0;
int reactorCpwr = 0;
int reactorConpwr = 0;
int reactorCoffpwr = 0;

int reactorDthreash = 0;
int reactorDpwr = 0;
int reactorDonpwr = 0;
int reactorDoffpwr = 0;

void out(data){									//function to output characters through the hardware uart
	while (!(IFG2 & UCA0TXIFG));
	UCA0TXBUF = data;
}


void main(void){
	WDTCTL = WDTPW + WDTHOLD; //stop the watchdog

	//clock
	BCSCTL1 = CALBC1_16MHZ;						//run the 16 MHz clock
	DCOCTL = CALDCO_16MHZ;
	P1SEL = BIT1 + BIT2 ;                     // P1.1 = RXD, P1.2=TXD
	P1SEL2 = BIT1 + BIT2 ;                     // P1.1 = RXD, P1.2=TXD
	UCA0CTL1 |= UCSSEL_2;     
	

	CCTL0 = CCIE;						//select what the interrupt counts up to
	TACTL = TASSEL_1 + MC_1 + ID_3;		//select the clock to use to interrupt
	CCR0 = 65500;
	
	/*Setup UART*/
	const unsigned long brd = (smclk_freq + (bps >> 1)) / bps; // Bit rate divisor

	UCA0BR1 = (brd >> 12) & 0xFF;               // High byte of whole divisor
	UCA0BR0 = (brd >> 4) & 0xFF;                // Low byte of whole divisor
	UCA0MCTL = ((brd << 4) & 0xF0) | UCOS16;    // Fractional divisor, oversampling mode

	UCA0CTL1 &= ~UCSWRST;                     // **Initialize USCI state machine**
	IE2 |= UCA0RXIE;                          // Enable USCI_A0 RX interrupt
	__bis_SR_register(GIE);			// interrupts enabled	


	/*Setup ADC*/
	ADC10CTL0 &= ~ENC;
	ADC10CTL0 =  ADC10SHT_2 + ADC10IE + ADC10ON + SREF_0;
	ADC10AE0 |= BIT0;


	/*Setup Pins*/
        P1DIR |= wastepumps | reactorApump | reactorBpump | reactorCpump | reactorDpump;
        P1OUT &= wastepumps | reactorApump | reactorBpump | reactorCpump | reactorDpump;
        P1SEL &= wastepumps | reactorApump | reactorBpump | reactorCpump | reactorDpump;
        
        P2DIR |= manifoldA | manifoldB | manifoldC | manifoldD;
        P2OUT &= manifoldA | manifoldB | manifoldC | manifoldD;
        P2SEL &= manifoldA | manifoldB | manifoldC | manifoldD;
        while (1){
                if (ON == FALSE){
                        P1OUT &= wastepumps | reactorApump | reactorBpump | reactorCpump | reactorDpump;
                        P2OUT &= manifoldA | manifoldB | manifoldC | manifoldD;
                        LPM3;
                }
        }

}

#pragma vector = TIMER0_A0_VECTOR //interrupt by main clock
__interrupt void pwm(void){
        if ( ON == TRUE){
                if (pwmcounter == 0){
                        P1OUT = wastepumps | reactorApump | reactorBpump | reactorCpump | reactorDpump;
                }
                
                if (pwmcounter == wastepumps){
                        P1OUT &= ~wastepumps;
                }
                if (pwmcounter == reactorApump){
                        P1OUT &= ~reactorApump;
                }
                if (pwmcounter == reactorBpump){
                        P1OUT &= ~reactorBpump;
                }
                if (pwmcounter == reactorCpump){
                        P1OUT &= ~reactorCpump;
                }
                if (pwmcounter == reactorDpump){
                        P1OUT &= ~reactorDpump;
                }
                pwmcounter += 1;
                if (pwmcounter == 10000){
                        pwmcounter = 0;
                }
         }
        
}

#pragma vector = TIMER0_A0_VECTOR //interrupt by main clock
__interrupt void update(void){
	//read adc and build message and update manifold
	ADC10CTL0 |= ENC+ ADC10SC; //Get ADC reading
	currentreading = ADC10MEM;
	if (state == 0){
	        if (currentreading > reactorAthreash){
	                reactorApwr = reactorAonpwr;
	        }
	        else{
	                reactorApwr = reactorAoffpwr;
	        }
	        outlist[0] = statelist[state];
	        outlist[1] = ((currentreading & 0xFF00)>>8)& 0x00FF;
	        outlist[2] = currentreading & 0x00FF;
	        outlist[3] = ((reactorApwr & 0xFF00)>>8)& 0x00FF;
	        outlist[4] = reactorApwr & 0x00FF;
	        
	        //P2OUT = manifoldB;
	}
	else if (state == 1){
	        if (currentreading > reactorBthreash){
	                reactorBpwr = reactorBonpwr;
	        }
	        else{
	                reactorBpwr = reactorBoffpwr;
	        }
	        outlist[0] = statelist[state];
	        outlist[1] = ((currentreading & 0xFF00)>>8)& 0x00FF;
	        outlist[2] = currentreading & 0x00FF;
	        outlist[3] = ((reactorBpwr & 0xFF00)>>8)& 0x00FF;
	        outlist[4] = reactorBpwr & 0x00FF;
	        
	        //P2OUT = manifoldC;
	}
	else if (state == 2){
	        if (currentreading > reactorCthreash){
	                reactorCpwr = reactorConpwr;
	        }
	        else{
	                reactorCpwr = reactorCoffpwr;
	        }
	        outlist[0] = statelist[state];
	        outlist[1] = ((currentreading & 0xFF00)>>8)& 0x00FF;
	        outlist[2] = currentreading & 0x00FF;
	        outlist[3] = ((reactorCpwr & 0xFF00)>>8)& 0x00FF;
	        outlist[4] = reactorCpwr & 0x00FF;
	        
	        //P2OUT = manifoldD;
	}
	else if (state == 3){
	        if (currentreading > reactorDthreash){
	                reactorDpwr = reactorDonpwr;
	        }
	        else{
	                reactorDpwr = reactorDoffpwr;
	        }
	        outlist[0] = statelist[state];
	        outlist[1] = ((currentreading & 0xFF00)>>8)& 0x00FF;
	        outlist[2] = currentreading & 0x00FF;
	        outlist[3] = ((reactorDpwr & 0xFF00)>>8)& 0x00FF;
	        outlist[4] = reactorDpwr & 0x00FF;
	        
	        //P2OUT = manifoldA;
	}
	///send data
	int x;
	for ( x = 5; x >0; x--){
	        out(outlist[x]);
	}
	
	state += 1;
	if (state > 3){
	        state = 0;
	}
	//Send waste pump power
	if (state == 0){
	        outlist[0] = 'W';
	        outlist[1] = 'N';
	        outlist[2] = 'N';
	        outlist[3] = ((wastepwr & 0xFF00)>>8)& 0x00FF;
	        outlist[4] = wastepwr & 0x00FF;
	        for ( x = 5; x >0; x--){
	                out(outlist[x]);
	        }
	}
	        
}

#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
	out(UCA0RXBUF);	
	if (UCAORXBUF == '\n'){
	        if (readlist[0] == 't' && readlist[1] =='r' && readlist[2] =='a' && readlist[3] == 'r' && readlist[4] == 't' && readlist[5] == 's'){
	                if (ON == TRUE){
	                        ON = FALSE;
	                        out('s');out('t');out('o');out('p');out('\n');
	                }
	                else {
	                        ON = TRUE;
	                        out('s');out('t');out('a');out('r');out('t');out('\n');
	                }
	        }
	        else if (readlist[0] == 't' && readlist[1] =='s' && readlist[2] =='e' && readlist[3] == 't' ){
	                
	        }
	        else {
	                wastepwr = (readlist[0]<<8)&readlist[1];
	                reactorDoffpwr = (readlist[2]<<8)&readlist[3];
	                reactorDonpwr = (readlist[4]<<8)&readlist[5];
	                reactorDthreash = (readlist[6]<<8)&readlist[7];
	                reactorCoffpwr = (readlist[8]<<8)&readlist[9];
	                reactorConpwr = (readlist[10]<<8)&readlist[11];
	                reactorCthreash = (readlist[12]<<8)&readlist[13];
	                reactorBoffpwr = (readlist[14]<<8)&readlist[15];
	                reactorBonpwr = (readlist[16]<<8)&readlist[17];
	                reactorBthreash = (readlist[18]<<8)&readlist[19];
	                reactorAoffpwr = (readlist[20]<<8)&readlist[21];
	                reactorAonpwr = (readlist[22]<<8)&readlist[23];
	                reactorAthreash = (readlist[24]<<8)&readlist[25];
	        }
	                
	        
	}
	int i;
	for (i = 26; i>0; i--){
	        readlist[i] = readlist[i-1];
	}
	readlist[0] = UCAORXBUF;
	
}	
/*
#pragma vector = ADC10_VECTOR //interrupt by ADC clock
__interrupt void ADC(void){
        ADC10CTL0 |= ENC+ ADC10SC; //Get ADC reading
	currentreading = ADC10MEM;
	

}*/

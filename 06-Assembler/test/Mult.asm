// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
// Initialize the result to zero
    @2
    M=0          // initialize the result R2=0

// Initialize a multiplier to the value of R1, which indicates how many time R0 needs to be added to the result
    @1
    D=M          // get the value of R1
    @multiplier
    M=D          // initialize a multiplier to the value of R1

// The main loop which add R0 to the result R2 for the times of multiplier
(LOOP)
    @multiplier
    D=M
    @END
    D;JLE        // if multiplier<=0 goto END

    @0
    D=M          // get the multiplicand R0
    @2
    M=D+M        // add the the multiplicand to the result R2

    @multiplier
    M=M-1        // decrease the multiplier by 1
    @LOOP
    0;JMP        // goto the main LOOP

(END)
    @END
    0;JMP        // infinite loop
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Initialize a pixel pointer to indicate the current pixel address
    @SCREEN 
    D=A 
    @ptr          // ptr refers to a memory location which stores current pixel address
    M=D           // initialize ptr to the first pixel of screen

// The main loop which checks if there is a keyboard input
// Goto KEY if a key has been pressed and goto NO_KEY otherwise
(LOOP)
    @KBD 
    D=M           // read the data from keyboard register
    @KEY 
    D;JNE         // if key goto KEY 
    @NO_KEY
    0;JMP         // else goto NO_KEY

// If KEY, set the current pixel to black
// Goto LOOP if ptr has reached KBD-1. Otherwise move to next pixel then goto LOOP
(KEY)
    @ptr 
    D=M           // get the address of current pixel 
    A=D 
    M=-1          // set the current pixel to black 
    @KBD 
    D=D-A
    @LOOP
    D+1;JEQ       // if ptr+1-KBD=0, no need to increment ptr, goto LOOP directly
    @ptr 
    M=M+1         // otherwise increment ptr by 1 and goto LOOP
    @LOOP
    0;JMP

// If NO_KEY, set the current pixel to white
// Goto LOOP if ptr has reached SCREEN. Otherwise move back one pixel then goto LOOP 
(NO_KEY)
    @ptr 
    D=M           // get the address of current pixel
    A=D
    M=0           // set the current pixel to white 
    @SCREEN
    D=D-A
    @LOOP
    D;JEQ         // if ptr-SCREEN=0, no need to decrease ptr, goto LOOP
    @ptr
    M=M-1         // otherwise decrease ptr by 1 and goto LOOP
    @LOOP
    0;JMP
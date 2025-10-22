pragma circom 2.1.8;

template Mul3() {

    signal input a;
    signal input b;
    signal input c;

    signal output out;

    signal i;

    a * b === 1;   // Force a * b === 1
    i <-- a * b;   // i must be equal 1, there is no constrain
    out <== i * c; // out must equal c since i === 1
}

component main{public [a, b, c]} = Mul3();
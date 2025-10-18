pragma circom 2.0.0;

template ProductProof(){
    signal input a;
    signal input b;
    signal output c;
    // TODO: revise
    c <== a * b;
}

component main = ProductProof();	

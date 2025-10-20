pragma circom 2.0.0;

template MoneyMoneyMoney(){
    signal input balance;
    signal input withdrawal;
    signal output newBalance;
    
    balance -= withdrawal;
    newBalance <== balance - withdrawal;
}

component main = ProductProof();	

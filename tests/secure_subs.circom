pragma circom 2.0.0;

template MoneyMoneyMoney(){

   signal input currentBalance;
   signal input withdrawAmount;
   signal output newBalance;
    
    // Ensure that both values are positive.
    component n2b1 = Num2Bits(64);
    n2b1.in <== withdrawAmount;

    component n2b2 = Num2Bits(64);
    n2b2.in <== currentBalance;

    // Ensure that withdrawAmount <= currentBalance.
    component lt = LessThan(64);
    lt.in[0] = withdrawAmount;
    lt.in[1] = currentBalance + 1;
    lt.out === 1;

    newBalance <== currentBalance - withdrawAmount;

}

component main = MoneyMoneyMoney();	

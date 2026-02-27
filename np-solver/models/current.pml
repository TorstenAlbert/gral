/* TSP Hamiltonian Cycle Verification — 51 cities */
byte tour[51];
byte visited[51];

proctype VerifyTour() {
    byte i = 0;
    byte valid = 1;
    do
    :: i < 51 ->
        if
        :: visited[tour[i]] == 1 -> valid = 0
        :: else -> visited[tour[i]] = 1
        fi;
        i++;
    :: i >= 51 -> break
    od;
    assert(valid == 1);
}

init {
    tour[0] = 26;
    tour[1] = 50;
    tour[2] = 45;
    tour[3] = 11;
    tour[4] = 46;
    tour[5] = 17;
    tour[6] = 3;
    tour[7] = 16;
    tour[8] = 36;
    tour[9] = 4;
    tour[10] = 37;
    tour[11] = 10;
    tour[12] = 31;
    tour[13] = 0;
    tour[14] = 21;
    tour[15] = 7;
    tour[16] = 25;
    tour[17] = 30;
    tour[18] = 27;
    tour[19] = 2;
    tour[20] = 35;
    tour[21] = 34;
    tour[22] = 19;
    tour[23] = 1;
    tour[24] = 28;
    tour[25] = 20;
    tour[26] = 15;
    tour[27] = 49;
    tour[28] = 33;
    tour[29] = 29;
    tour[30] = 8;
    tour[31] = 48;
    tour[32] = 9;
    tour[33] = 38;
    tour[34] = 32;
    tour[35] = 44;
    tour[36] = 14;
    tour[37] = 43;
    tour[38] = 41;
    tour[39] = 39;
    tour[40] = 18;
    tour[41] = 40;
    tour[42] = 12;
    tour[43] = 24;
    tour[44] = 13;
    tour[45] = 23;
    tour[46] = 42;
    tour[47] = 6;
    tour[48] = 22;
    tour[49] = 47;
    tour[50] = 5;
    run VerifyTour();
}

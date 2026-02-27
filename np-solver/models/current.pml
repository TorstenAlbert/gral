/* TSP Hamiltonian Cycle Verification — 6 cities */
byte tour[6];
byte visited[6];

proctype VerifyTour() {
    byte i = 0;
    byte valid = 1;
    do
    :: i < 6 ->
        if
        :: visited[tour[i]] == 1 -> valid = 0
        :: else -> visited[tour[i]] = 1
        fi;
        i++;
    :: i >= 6 -> break
    od;
    assert(valid == 1);
}

init {
    tour[0] = 1;
    tour[1] = 3;
    tour[2] = 5;
    tour[3] = 4;
    tour[4] = 2;
    tour[5] = 0;
    run VerifyTour();
}

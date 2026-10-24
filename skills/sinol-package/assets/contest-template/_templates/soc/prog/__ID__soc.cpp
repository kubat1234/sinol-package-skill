// Interactor. sinol-make / sio2 run it as:
//   __ID__soc <num_processes> <read_fd_0> <write_fd_0> [<read_fd_1> <write_fd_1> ...]
// stdin  = the test (in/__ID__*.in), never visible to the solution,
// stdout = verdict in the checker format:
//   line 1: OK or WRONG, line 2: comment, line 3: percent of points (empty = 100).
// Solution i reads from <write_fd_i> and writes to <read_fd_i> through its own
// stdin/stdout, and gets i as argv[1].
#include <bits/stdc++.h>
using namespace std;

// TEMPLATE: replace the protocol.

const int QUERY_LIMIT = 30;

[[noreturn]] void verdict(bool ok, const string& comment, int percent = 100) {
    if (ok) printf("OK\n%s\n%d\n", comment.c_str(), percent);
    else printf("WRONG\n%s\n", comment.c_str());
    exit(0);
}

int main(int argc, char* argv[]) {
    signal(SIGPIPE, SIG_IGN);  // the solution may exit early - handle it as WRONG, not a crash
    assert(argc >= 4 && atoi(argv[1]) == 1);
    FILE* from = fdopen(atoi(argv[2]), "r");
    FILE* to = fdopen(atoi(argv[3]), "w");

    long long n, x;
    if (scanf("%lld %lld", &n, &x) != 2) return 1;  // broken test -> system error

    fprintf(to, "%lld\n", n);
    fflush(to);

    for (int q = 1;; ++q) {
        char c;
        long long y;
        if (fscanf(from, " %c", &c) != 1) verdict(false, "Program zakończył działanie przed odgadnięciem liczby");
        if (c != '?' || fscanf(from, "%lld", &y) != 1) verdict(false, "Niepoprawny format zapytania");
        if (y < 1 || y > n) verdict(false, "Zapytanie spoza zakresu");
        if (q > QUERY_LIMIT) verdict(false, "Przekroczono limit zapytań");
        if (y == x) {
            fprintf(to, "=\n");
            fflush(to);
            verdict(true, "Zapytań: " + to_string(q));
        }
        fprintf(to, "%c\n", x < y ? '<' : '>');
        fflush(to);
    }
}

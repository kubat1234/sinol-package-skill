// Sample interactor for contestants: talks with your program through its stdin/stdout.
// The interactor on the server checks more (e.g. the query limit).
//   g++ -O2 -o __ID__soc __ID__soc.cpp && g++ -O2 -o __ID__ __ID__.cpp
//   mkfifo fifo && ./__ID__soc 100 42 < fifo | ./__ID__ > fifo; rm fifo
#include <cstdio>
#include <cstdlib>

// TEMPLATE: replace the protocol (the same as in prog/__ID__soc.cpp).

int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "użycie: %s n x\n", argv[0]);
        return 1;
    }
    long long n = atoll(argv[1]), x = atoll(argv[2]);
    printf("%lld\n", n);
    fflush(stdout);
    for (int q = 1;; ++q) {
        char c;
        long long y;
        if (scanf(" %c %lld", &c, &y) != 2 || c != '?') {
            fprintf(stderr, "Niepoprawny format zapytania\n");
            return 1;
        }
        if (y == x) {
            printf("=\n");
            fflush(stdout);
            fprintf(stderr, "OK, zapytań: %d\n", q);
            return 0;
        }
        printf("%c\n", x < y ? '<' : '>');
        fflush(stdout);
    }
}

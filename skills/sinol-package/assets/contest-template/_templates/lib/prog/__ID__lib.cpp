// Library: reads the test, runs the contestant's maks_suma(), prints the result.
// The printed text is compared with out/__ID__*.out (no checker needed).
// Any rule violation prints a message instead of the answer, so it is a WA.
#include <bits/stdc++.h>
#include "__ID__lib.h"
using namespace std;

// TEMPLATE: replace the interface.

namespace {
int n;
vector<long long> a;
vector<int> reads;

[[noreturn]] void violation(const char* msg) {
    printf("NARUSZENIE ZASAD: %s\n", msg);
    exit(0);
}
}  // namespace

int dlugosc() { return n; }

long long element(int i) {
    if (i < 1 || i > n) violation("indeks poza zakresem");
    if (++reads[i] > 2) violation("element odczytany więcej niż dwa razy");
    return a[i];
}

int main() {
    if (scanf("%d", &n) != 1) return 1;
    a.assign(n + 1, 0);
    reads.assign(n + 1, 0);
    for (int i = 1; i <= n; ++i)
        if (scanf("%lld", &a[i]) != 1) return 1;
    fclose(stdin);  // the contestant must use element(), not read the input
    long long answer = maks_suma();
    printf("%lld\n", answer);
}

// Sample library for contestants: reads a test in the input format and prints the
// result of maks_suma(). The library on the server also checks the rules.
// g++ -O2 -o __ID__ __ID__.cpp __ID__lib.cpp && ./__ID__ < __ID__0.in
#include <cstdio>
#include <vector>
#include "__ID__lib.h"

static int n;
static std::vector<long long> a;

int dlugosc() { return n; }
long long element(int i) { return a[i]; }

int main() {
    if (scanf("%d", &n) != 1) return 1;
    a.assign(n + 1, 0);
    for (int i = 1; i <= n; ++i)
        if (scanf("%lld", &a[i]) != 1) return 1;
    printf("%lld\n", maks_suma());
}

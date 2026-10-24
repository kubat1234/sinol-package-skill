// Input generator: every test of the package, the statement example included
// (nothing in in/ is committed). sinol-make gen runs it inside in/.
//   ./__ID__ingen --list    which line made which test, with its arguments and size
// gen.h: https://github.com/kubat1234/sinol-gen (docs/guide.md, docs/reference.md)
#include <bits/stdc++.h>
#include "gen.h"
using namespace std;
using gen::ll;

// TEMPLATE: a test is "n x": the range and the hidden number (only the interactor
// reads it). Replace the generators and the tests.

const ll N1 = 20, N2 = 1'000'000'000;

enum Where { RANDOM, FIRST, LAST, MIDDLE };

void hidden(gen::Rng& R, ostream& out, ll n, Where where) {
    ll x = where == FIRST ? 1 : where == LAST ? n : where == MIDDLE ? (n + 1) / 2 : R.range(1LL, n);
    gen::line(out, n, x);
}

int main(int argc, char* argv[]) {
    gen::Generator g("__ID__", argc, argv);

    g.example("10 7");                                   // __ID__0.in    the example from the statement
    g.ocen(hidden, N1, RANDOM);                          // __ID__1ocen.in public test

    g.group(1);                                          // n <= 20
    g.test("1 1");                                       // by hand
    for (Where w : {FIRST, LAST, RANDOM}) g.test(hidden, N1, w);

    g.group(2);                                          // n <= 10^9
    for (Where w : {FIRST, LAST, MIDDLE, RANDOM}) g.test(hidden, N2, w);
    g.test(hidden, gen::near(N2, 1000), RANDOM);

    return g.done();
}

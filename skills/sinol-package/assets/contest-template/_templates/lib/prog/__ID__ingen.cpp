// Input generator: every test of the package, the statement example included
// (nothing in in/ is committed). sinol-make gen runs it inside in/.
//   ./__ID__ingen --list    which line made which test, with its arguments and size
// gen.h: https://github.com/kubat1234/sinol-gen (docs/guide.md, docs/reference.md)
#include <bits/stdc++.h>
#include "gen.h"
using namespace std;
using gen::ll;

// TEMPLATE: example for "n, then n numbers" - replace the generators and the tests.

const int MAXN1 = 1000, MAXN = 200'000;
const ll MAXV1 = 1'000'000, MAXV = 1'000'000'000;

// n numbers from [lo, hi]
void random_arr(gen::Rng& R, ostream& out, int n, ll lo, ll hi) {
    gen::line(out, n);
    gen::print_line(out, R.array(n, lo, hi));
}

int main(int argc, char* argv[]) {
    gen::Generator g("__ID__", argc, argv);

    g.example({"3", "1 -2 3"});                          // __ID__0.in    the example from the statement
    g.ocen(random_arr, 10, -10, 10);                     // __ID__1ocen.in public test

    g.group(1);                                          // n <= 1000, |a_i| <= 10^6
    g.test({"1", "-5"});                                 // by hand
    g.test(random_arr, MAXN1, -MAXV1, MAXV1);
    g.test(random_arr, gen::near(MAXN1), -MAXV1, -1);    // n from [990, 1000], all negative

    g.group(2);                                          // n <= 200 000, |a_i| <= 10^9
    for (ll v : {1'000LL, MAXV}) g.test(random_arr, MAXN, -v, v);
    g.test(random_arr, MAXN, MAXV, MAXV);                // the answer overflows int

    return g.done();
}

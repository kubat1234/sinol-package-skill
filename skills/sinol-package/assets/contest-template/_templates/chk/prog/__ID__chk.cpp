// Output checker. Called as: __ID__chk <in> <contestant out> <model out>
// Prints to stdout:
//   line 1: OK or WRONG
//   line 2: comment shown to the contestant (may be empty)
//   line 3: percent of points for OK (e.g. 100, 50); empty = 100
#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

// TEMPLATE: example - one number, compared with the model's answer.

[[noreturn]] void verdict(bool ok, const string& comment, int percent = 100) {
    if (ok) cout << "OK\n" << comment << '\n' << percent << '\n';
    else cout << "WRONG\n" << comment << '\n';
    exit(0);
}

// Any formatting problem in the contestant's output is a WRONG answer.
void wrong_format(const char* msg, int line, int /*position*/) {
    verdict(false, "Błąd formatu w wierszu " + to_string(line) + ": " + msg);
}

int main(int argc, char* argv[]) {
    assert(argc == 4);
    ifstream test_in(argv[1]), model(argv[3]);  // the test and the model's output: trusted
    long long expected;
    model >> expected;

    oi::Scanner out(argv[2], wrong_format, oi::PL);  // the contestant's output: check everything
    out.skipWhitespaces();
    long long got = out.readLL();
    out.skipWhitespaces();
    out.readEof();

    if (got != expected) verdict(false, "Oczekiwano " + to_string(expected) + ", wczytano " + to_string(got));
    verdict(true, "");
}

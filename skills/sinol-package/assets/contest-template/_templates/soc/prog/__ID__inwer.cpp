// Input verifier. sinol-make passes the test file name as argv[1].
#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

// TEMPLATE: replace the limits and the reading code.

const map<int, long long> MAX_N = {{0, 1'000'000'000}, {1, 20}, {2, 1'000'000'000}};

// "__ID__2c.in" -> 2, "__ID__1ocen.in" -> 0, "__ID__0a.in" -> 0
int group_of(string name) {
    name = name.substr(name.rfind('/') + 1);
    if (name.find("ocen") != string::npos) return 0;
    size_t i = 3, j = i;
    while (j < name.size() && isdigit(name[j])) j++;
    return stoi(name.substr(i, j - i));
}

int main(int argc, char* argv[]) {
    int group = argc > 1 ? group_of(argv[1]) : 0;
    assert(MAX_N.count(group));

    oi::Scanner in(stdin, oi::PL);
    long long n = in.readLL(1, MAX_N.at(group));
    in.readSpace();
    long long x = in.readLL(1, n);
    in.readEoln();
    in.readEof();

    cout << "OK group=" << group << " n=" << n << " x=" << x << '\n';
}

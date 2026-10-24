// Library interface given to contestants (attach it to the statement).
#pragma once

// Provided by the library:
int dlugosc();              // n
long long element(int i);   // a_i, 1 <= i <= n; each a_i may be read at most twice

// Implemented by the contestant:
long long maks_suma();

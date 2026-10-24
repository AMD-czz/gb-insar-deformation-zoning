# Runtime environments

`paper_runtime_environment.json` is an archived record of the original timing experiment, not a new validation result. It includes stages absent from the public package. The paper reports Python 3.14.2, Windows 11, Intel Core Ultra 7 255HX, single thread.

`VALIDATION_ENVIRONMENT.json` records the interpreter/library versions used to check v1.1. Requirements pin that environment. See ../VALIDATION.md for executed commands and results. Other Python/OS combinations are untested.

SARscape 5.6.0 and proprietary radar decoding are not bundled. Compilation, sample size, file cache, and hardware affect runtime. This package does not reproduce archived end-to-end wall-clock times.

# This file intentionally replaces stock boot.py only after `just mp-backup`.
# `just mp-stop` restores the original boot.py from remote boot.stock.py.

import gc


gc.collect()
exec(open("main.py").read(), globals())

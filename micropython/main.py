import sys

from cyberbrick_esc.app import main


try:
    main()
except KeyboardInterrupt:
    raise
except Exception as exc:
    print("CyberBrick ESC MicroPython app stopped:")
    sys.print_exception(exc)

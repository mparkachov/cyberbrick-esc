cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(cyberbrick_esc)

target_include_directories(app PRIVATE include)
target_sources(app PRIVATE
  src/main.c
  src/motor_output.c
  src/pwm_input.c
  src/safety.c
)


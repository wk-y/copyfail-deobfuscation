void _start() __noreturn {
  syscall(sys_setuid{0x69}, 0);
  syscall(sys_execve{0x3b}, "/bin/sh", nullptr, nullptr);
  syscall(sys_exit{0x3c}, 0);
  /* no return */
}

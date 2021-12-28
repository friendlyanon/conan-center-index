# ---- Autotools style compile checks ----

include(CheckFunctionExists)
include(CheckIncludeFile)
include(CheckTypeSize)

macro(to_define name)
  string(MAKE_C_IDENTIFIER "${name}" to_define_result)
  string(TOUPPER "${to_define_result}" to_define_result)
endmacro()

macro(check_include header)
  to_define("${header}")
  check_include_file("${header}" "HAVE_${to_define_result}")
endmacro()

macro(check_function function)
  to_define("${function}")
  check_function_exists("${function}" "HAVE_${to_define_result}")
endmacro()

macro(check_type type var)
  check_type_size("${type}" "${var}" BUILTIN_TYPES_ONLY)
endmacro()

macro(set_if condition var value)
  if(${condition})
    set("${var}" "${value}")
  endif()
endmacro()

check_include(crypt.h)
check_include(des.h)
check_include(dirent.h)
check_include(dlfcn.h)
check_include(fcntl.h)

# FIXME: add krb5 to CCI
# These affect the gssapi plugin
# check_include(gssapi.h)
# check_include(gssapi/gssapi.h)
# check_include(gssapi/gssapi_ext.h)
# check_include(gssapi/gssapi_krb5.h)

check_include(inttypes.h)

# FIXME: add krb5 to CCI
# This only affects saslauthd/mechanisms.h
# check_include(krb5.h)

check_include(limits.h)
check_include(malloc.h)
check_include(memory.h)
check_include(ndir.h)
check_include(paths.h)
check_include(stdarg.h)
check_include(stdint.h)
check_include(stdlib.h)
check_include(string.h)
check_include(strings.h)
check_include(sys/dir.h)
check_include(sys/file.h)
check_include(sys/ndir.h)
check_include(sys/param.h)
check_include(sys/socket.h)
check_include(sys/stat.h)
check_include(sys/time.h)
check_include(sys/types.h)
check_include(sys/uio.h)
check_include(sys/wait.h)
check_include(sysexits.h)
check_include(syslog.h)
check_include(unistd.h)
check_include(varargs.h)
check_include(ws2tcpip.h)

check_function(asprintf)
check_function(dn_expand)
check_function(dns_lookup)
check_function(getaddrinfo)
check_function(getdomainname)
check_function(gethostname)
check_function(getnameinfo)
check_function(getpassphrase)
check_function(getpwnam)
check_function(getspnam)
check_function(getsubopt)
check_function(gettimeofday)
check_function(inet_aton)
check_function(jrand48)
check_function(memcpy)
check_function(mkdir)
check_function(select)
check_function(snprintf)

set(CMAKE_REQUIRED_LIBRARIES "")
set_if(WIN32 CMAKE_REQUIRED_LIBRARIES Ws2_32)

check_function(socket)

set(CMAKE_REQUIRED_LIBRARIES "")

check_function(strchr)
check_function(strdup)
check_function(strerror)
check_function(strlcat)
check_function(strlcpy)
check_function(strspn)
check_function(strstr)
check_function(strtol)
check_function(syslog)
check_function(vsnprintf)

foreach(
    pair
    gid_t\;int
    mode_t\;int
)
  list(GET pair 0 type)
  list(GET pair 1 type_to_use)
  to_define("${type}")
  check_type_size("${type}" "${to_define_result}_TYPE")
  set_if("NOT;HAVE_${to_define_result}_TYPE" "${type}" "${type_to_use}")
endforeach()

set(CMAKE_EXTRA_INCLUDE_FILES "")
set_if(HAVE_SYS_SOCKET_H CMAKE_EXTRA_INCLUDE_FILES sys/socket.h)
set_if(HAVE_WS2TCPIP_H CMAKE_EXTRA_INCLUDE_FILES ws2tcpip.h)

check_type("struct sockaddr" STRUCT_SOCKADDR_STORAGE)
check_type("((struct sockaddr*)0)->sa_len" SOCKADDR_SA_LEN)
check_type("((struct sockaddr_storage*)0)->ss_family" SS_FAMILY)
check_type(socklen_t SOCKLEN_T)

set(CMAKE_EXTRA_INCLUDE_FILES "")

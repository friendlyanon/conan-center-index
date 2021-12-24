cmake_minimum_required(VERSION 3.1)

project(openldap_wrapper VERSION "${CONAN_openldap_VERSION}" LANGUAGES C)

# ---- Dependencies ----

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}")
set(THREADS_PREFER_PTHREAD_FLAG YES CACHE STRING "")

find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)

# ---- Variables ----

include(variables.cmake)

# ---- Autotools style compile checks ----

include(compile-checks.cmake)

# ---- Configure headers ----

foreach(header portable lber_types ldap_config ldap_features)
  message(STATUS "Processing ${header}.hin")
  file(READ "${PROJECT_SOURCE_DIR}/source_subfolder/include/${header}.hin" content)
  if(header STREQUAL "portable")
    string(REPLACE "#undef LDAP_DEBUG" "$<$<CONFIG:Debug>:#define LDAP_DEBUG>" content "${content}")
  endif()
  string(REGEX REPLACE "#[ \t]*undef ([^\r\n ]+)" "#cmakedefine \\1 @\\1@" content "${content}")
  string(REGEX REPLACE "%([A-Za-z0-9_]+)%" "@\\1@" content "${content}")
  string(CONFIGURE "${content}" content @ONLY)
  file(WRITE "${PROJECT_BINARY_DIR}/intermediate/${header}.hin" "${content}")
  file(GENERATE OUTPUT "${PROJECT_BINARY_DIR}/configured/$<CONFIG>/${header}.h" INPUT "${PROJECT_BINARY_DIR}/intermediate/${header}.hin")
  message(STATUS "Processing ${header}.hin - done")
endforeach()

# ---- Library targets ----

set(src source_subfolder/libraries/libldap)
add_library(
    ldap
    "${src}/bind.c"
    "${src}/open.c"
    "${src}/result.c"
    "${src}/error.c"
    "${src}/compare.c"
    "${src}/search.c"
    "${src}/controls.c"
    "${src}/messages.c"
    "${src}/references.c"
    "${src}/extended.c"
    "${src}/cyrus.c"
    "${src}/modify.c"
    "${src}/add.c"
    "${src}/modrdn.c"
    "${src}/delete.c"
    "${src}/abandon.c"
    "${src}/sasl.c"
    "${src}/sbind.c"
    "${src}/unbind.c"
    "${src}/cancel.c"
    "${src}/filter.c"
    "${src}/free.c"
    "${src}/sort.c"
    "${src}/passwd.c"
    "${src}/whoami.c"
    "${src}/vc.c"
    "${src}/getdn.c"
    "${src}/getentry.c"
    "${src}/getattr.c"
    "${src}/getvalues.c"
    "${src}/addentry.c"
    "${src}/request.c"
    "${src}/os-ip.c"
    "${src}/url.c"
    "${src}/pagectrl.c"
    "${src}/sortctrl.c"
    "${src}/vlvctrl.c"
    "${src}/init.c"
    "${src}/options.c"
    "${src}/print.c"
    "${src}/string.c"
    "${src}/util-int.c"
    "${src}/schema.c"
    "${src}/charray.c"
    "${src}/os-local.c"
    "${src}/dnssrv.c"
    "${src}/utf-8.c"
    "${src}/utf-8-conv.c"
    "${src}/tls2.c"
    "${src}/tls_o.c"
    "${src}/tls_g.c"
    "${src}/turn.c"
    "${src}/ppolicy.c"
    "${src}/dds.c"
    "${src}/txn.c"
    "${src}/ldap_sync.c"
    "${src}/stctrl.c"
    "${src}/assertion.c"
    "${src}/deref.c"
    "${src}/ldifutil.c"
    "${src}/ldif.c"
    "${src}/fetch.c"
    "${src}/lbase64.c"
    "${src}/msctrl.c"
    "${src}/psearchctrl.c"
    "${src}/threads.c"
    "${src}/rdwr.c"
    "${src}/tpool.c"
    "${src}/rq.c"
    "${src}/thr_posix.c"
    "${src}/thr_thr.c"
    "${src}/thr_nt.c"
    "${src}/thr_pth.c"
    "${src}/thr_debug.c"
    "${src}/account_usability.c"
    "${src}/avl.c"
    "${src}/tavl.c"
)

set(src source_subfolder/libraries/liblber)
add_library(
    lber
    "${src}/assert.c"
    "${src}/decode.c"
    "${src}/encode.c"
    "${src}/io.c"
    "${src}/bprint.c"
    "${src}/debug.c"
    "${src}/memory.c"
    "${src}/options.c"
    "${src}/sockbuf.c"
)

if(WIN32)
  target_sources(lber PRIVATE "${src}/nt_err.c")
else()
  target_sources(lber PRIVATE "${src}/stdio.c")
endif()

foreach(tgt ldap lber)
  target_include_directories("${tgt}" PRIVATE source_subfolder/include "${PROJECT_BINARY_DIR}/configured/$<CONFIG>")
endforeach()

if(WIN32)
  target_link_libraries(lber PRIVATE Ws2_32)
endif()
target_link_libraries(lber PRIVATE OpenSSL::Crypto)
target_link_libraries(ldap PRIVATE lber Threads::Threads OpenSSL::SSL OpenSSL::Crypto)
set_target_properties(ldap lber PROPERTIES VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}")

# ---- Install ----

include(GNUInstallDirs)

install(
    TARGETS ldap lber
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

# The autotools build seems to only install these headers:
#   lber.h
#   lber_types.h
#   ldap.h
#   ldap_cdefs.h
#   ldap_features.h
#   ldap_schema.h
#   ldap_utf8.h
#   ldif.h
#   openldap.h
#   slapi-plugin.h
# However, the package used as reference has the whole include folder.
install(
    DIRECTORY
    source_subfolder/include/
    "${PROJECT_BINARY_DIR}/configured/$<CONFIG>/"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/openldap"
    FILES_MATCHING PATTERN *.h
)

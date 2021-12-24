# ---- Variables independent of autotools style compile checks ----

if(CMAKE_USE_PTHREADS_INIT)
  set(HAVE_PTHREADS 10)
endif()

set(BINDIR "bin")
set(SBINDIR "bin")
set(DATADIR "share")
set(SYSCONFDIR "")
set(LIBEXECDIR "lib")
set(MODULEDIR "")
set(RUNDIR "")
set(LOCALEDIR "")

if(MSVC) # This would be an _MSC_VER check in code
  add_definitions(-Dstrncasecmp=_strnicmp -Dstrcasecmp=_stricmp)
endif()

set(REENTRANT 1)
set(_REENTRANT 1)
set(LDAP_API_FEATURE_X_OPENLDAP_REENTRANT 1)

set(THREADSAFE 1)
set(_THREADSAFE 1)
set(THREAD_SAFE 1)
set(_THREAD_SAFE 1)
set(LDAP_API_FEATURE_X_OPENLDAP_THREAD_SAFE 1)

set(CTIME_R_NARGS 2)
set(ENABLE_REWRITE 1)

if(WIN32)
  set(EXEEXT [[".exe"]])
  set(HAVE_NT_EVENT_LOG 1)
  set(HAVE_NT_SERVICE_MANAGER 1)
  set(HAVE_NT_THREADS 1)
  if(MSVC_VERSION LESS "1900")
    set(snprintf _snprintf)
    set(HAVE_SNPRINTF 0)
  else()
    set(HAVE_SNPRINTF 1)
  endif()
endif()

set(HAVE_TLS 1)
set(HAVE_OPENSSL 1)
set(HAVE_OPENSSL_CRL 1)
set(USE_MP_BIGNUM 1)
set(HAVE_OPENSSL_BN_H 1)
set(HAVE_OPENSSL_CRYPTO_H 1)
set(HAVE_OPENSSL_SSL_H 1)

# set(HAVE_SASL 1)
# set(HAVE_SASL_VERSION 1)
# set(HAVE_SASL_SASL_H 1)
# set(HAVE_SASL_H 1)

set(LBER_SOCKET_T int)

# Space is included so configure doesn't discard variables with 0
set(LDAP_VENDOR_VERSION_MAJOR " ${PROJECT_VERSION_MAJOR}")
set(LDAP_VENDOR_VERSION_MINOR " ${PROJECT_VERSION_MINOR}")
set(LDAP_VENDOR_VERSION_PATCH " ${PROJECT_VERSION_PATCH}")

math(EXPR LDAP_VENDOR_VERSION "\
${PROJECT_VERSION_MAJOR} * 10000 + \
${PROJECT_VERSION_MINOR} * 100 + \
${PROJECT_VERSION_PATCH}")

set(RETSIGTYPE void)
set(STDC_HEADERS 1)
set(ber_socklen_t int)

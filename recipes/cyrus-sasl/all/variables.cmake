# ---- Variables independent of autotools style compile checks ----

if(MSVC) # This would be an _MSC_VER check in code
  add_definitions(-Dstrncasecmp=_strnicmp -Dstrcasecmp=_stricmp)
  set(HAVE_SNPRINTF 1)
  if(MSVC_VERSION LESS "1900")
    set(HAVE_SNPRINTF 0)
  endif()
endif()

math(EXPR PACKAGE_VERSION "\
${PROJECT_VERSION_MAJOR} * 10000 + \
${PROJECT_VERSION_MINOR} * 100 + \
${PROJECT_VERSION_PATCH}")

set(VERSION "${PACKAGE_VERSION}")
set(name cyrus-sasl)
set(PACKAGE "${name}")
set(PACKAGE_NAME "${name}")
set(PACKAGE_STRING "${name}-${PROJECT_VERSION}")

set(RETSIGTYPE void)

set(cyrus-sasl_PLUGINDIR "${CMAKE_INSTALL_BINDIR}/sasl2" CACHE PATH "")
set(PLUGINDIR "${cyrus-sasl_PLUGINDIR}")
set(CONFIGDIR "${cyrus-sasl_PLUGINDIR}")

set(GETXXNAM_R_5ARG 1 CACHE STRING "")

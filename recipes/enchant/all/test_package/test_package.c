#include <openldap/openldap.h>
#include <stddef.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  ldap_rdnfree(NULL);

  return 0;
}

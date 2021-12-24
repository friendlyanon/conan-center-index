#include <openldap/openldap.h>
#include <stddef.h>

int main()
{
  ldap_rdnfree(NULL);

  return 0;
}

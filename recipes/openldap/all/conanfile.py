from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">= 1.33.0"


class OpenLDAPConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP Software is an open source implementation of the Lightweight Directory Access Protocol"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    topics = "ldap",
    license = "OLDAP-2.8"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake_find_package",
    requires = "openssl/1.1.1m",
    exports_sources = "CMakeLists.txt", "*.cmake", "*.h.in", "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_openldap_VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", "licenses", self._source_subfolder)
        self.copy("LICENSE", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        pass

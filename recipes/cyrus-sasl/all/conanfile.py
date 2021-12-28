import functools
import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class CyrusSaslConan(ConanFile):
    name = "cyrus-sasl"
    license = "BSD-4-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cyrusimap.org/sasl/"
    description = (
        "This is the Cyrus SASL API implementation. "
        "It can be used on the client or server side "
        "to provide authentication and authorization services."
    )

    topics = ("SASL", "authentication", "authorization")
    settings = ("os", "compiler", "build_type", "arch")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_cram": [True, False],
        "with_digest": [True, False],
        "with_scram": [True, False],
        "with_otp": [True, False],
        "with_krb4": [True, False],
        "with_gssapi": [True, False],
        "with_plain": [True, False],
        "with_anon": [True, False],
        "with_postgresql": [True, False],
        "with_mysql": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_cram": True,
        "with_digest": True,
        "with_scram": True,
        "with_otp": True,
        "with_krb4": True,
        "with_gssapi": False, # FIXME: should be True
        "with_plain": True,
        "with_anon": True,
        "with_postgresql": False,
        "with_mysql": False,
        "with_sqlite3": False,
    }
    exports_sources = ("CMakeLists.txt",)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1k")
        if self.options.with_postgresql:
            self.requires("libpq/13.3")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.25")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.36.0")
        if self.options.with_gssapi:
            raise ConanInvalidConfiguration("with_gssapi requires krb5 recipe, not yet available in CCI")
            self.requires("krb5/1.18.3")

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.get(**get_args, destination=root, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_cyrus-sasl_VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        info = self.cpp_info
        info.names["pkg_config"] = "libsasl2"
        info.libs = ["sasl2"]
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import contextlib
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
        "threads": ["auto", "nt", "posix", "pth", "lwp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": "auto",
    }
    requires = "openssl/1.1.1m", "libevent/2.1.12", "libsodium/1.0.18", "pcre2/10.37"
    exports_sources = "proxy", "proxy-libtool", "patches/*"

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.threads == "auto":
            self.options.threads = "nt" if self.settings.os == "Windows" else "posix"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self._settings_build.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--disable-slapd",  # FIXME: separate package?
            "--with-tls=openssl",
            "--with-mp=longlong",
            "--with-argon2=libsodium",
            "--without-systemd",
            "--without-cyrus-sasl",
            f"--with-threads={self.options.threads}",
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-dynamic={}".format(yes_no(self.options.shared)),
            "ac_cv_header_regex_h=yes",
            "ac_cv_search_regfree=-lpcre2-posix -lpcre2-8",
            "ol_cv_c_posix_regex=yes",
        ]
        if self._is_msvc:
            args.extend([
                "ac_cv_func_snprintf=yes",
            ])
        autotools.configure(args=args)
        if self._is_msvc:
            libtool = os.path.join(self.build_folder, "libtool")
            os.rename(libtool, os.path.join(self.build_folder, "libtool_"))
            os.rename(os.path.join(self.build_folder, "proxy-libtool"), libtool)
        return autotools

    @contextlib.contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self):
                libpath_wrapper = tools.unix_path(os.path.abspath("proxy"))
                automake_wrapper = tools.unix_path(self.deps_user_info["automake"].compile)
                lib_wrapper = tools.unix_path(self.deps_user_info["automake"].ar_lib)
                build_dir = tools.unix_path(self.build_folder)
                env = {
                    "CC": f"{libpath_wrapper} {automake_wrapper} cl -nologo",
                    "CFLAGS": "-DHAVE_TIME_T",
                    "LD": "link",
                    "NM": "dumpbin -symbols",
                    "STRIP": ":",
                    "AR": f"{libpath_wrapper} {lib_wrapper} lib",
                    "RANLIB": ":",
                    "LDAP_PROXY_PATH": f"{build_dir}/proxy",
                    "LDAP_LIBTOOL_PATH": f"{build_dir}/libtool_",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make(target="depend")
            autotools.make()

    def package(self):
        self.copy("COPYRIGHT", "licenses")
        self.copy("LICENSE", "licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        pass

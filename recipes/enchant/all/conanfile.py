import functools
import os
from contextlib import contextmanager

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"

providers = {
    "with_hunspell": "hunspell/1.7.0",
    "with_nuspell": "",
    "with_aspell": "",
    "with_hspell": "",
    "with_voikko": "",
    "with_applespell": "",
    "with_zemberek": "",
}

default_provider = "with_hunspell"


class EnchantConan(ConanFile):
    name = "enchant"
    description = (
        "Enchant aims to provide a simple but comprehensive abstraction for "
        "dealing with different spell checking libraries in a consistent way."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://abiword.github.io/enchant/"
    topics = ("enchant", "spell", "spell-check")
    license = "LGPL-2.1-or-later"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        **{k: [True, False] for k in providers.keys()},
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        **{k: k == default_provider for k in providers.keys()},
    }
    generators = "pkg_config"
    requires = "glib/2.70.1"
    exports_sources = "proxy"

    def _opt(self, k):
        opts = self.options
        return opts[k] if isinstance(opts, dict) else opts.get_safe(k)

    def validate(self):
        for k in set(providers.keys()) - {default_provider}:
            if self._opt(k):
                raise ConanInvalidConfiguration(
                    "Only the hunspell provider is supported for now"
                )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        for k, v in providers.items():
            if self._opt(k):
                self.requires(v)

    @property
    def _is_msvc(self):
        return self.settings.compiler in ("Visual Studio", "msvc")

    def build_requirements(self):
        if self._is_msvc:
            self.build_requires("pkgconf/1.7.4")
            if not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    @contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self):
                proxy = tools.unix_path(os.path.abspath("proxy"))
                env = {
                    "CC": f"{proxy} cl -nologo",
                    "CXX": f"{proxy} cl -nologo /Zc:__cplusplus",
                    "LD": "link -nologo",
                    "AR": "lib -nologo",
                    "PKG_CONFIG": tools.unix_path(tools.which("pkgconf")),
                    "PKG_CONFIG_PATH": tools.unix_path(os.path.abspath(".")),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        win_bash = tools.os_info.is_windows
        autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
        shared = self.options.shared
        args = [
            *[
                "--" + k.replace("_", "-") + ("" if self._opt(k) else "=no")
                for k in providers.keys()
            ],
            "--{}-shared".format("enable" if shared else "disable"),
            "--{}-static".format("disable" if shared else "enable"),
            "--with-pic={}".format("yes" if self._opt("fPIC") else "no"),
            "--disable-dependency-tracking",
            "--disable-gcc-warnings",
        ]
        if not self._is_msvc:
            args.append("--enable-relocatable")
        autotools.configure(args=args)
        return autotools

    def build(self):
        with self._build_context():
            self._configure_autotools().make()

    def package(self):
        with self._build_context():
            self._configure_autotools().install()
        self.copy("COPYING.LIB", "licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

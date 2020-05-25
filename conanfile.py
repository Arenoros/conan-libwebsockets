import os
from conans import ConanFile, CMake, tools


class LibwebsocketsConan(ConanFile):
    name = "libwebsockets"
    version = "4.0"
    description = "Canonical libwebsockets.org websocket library"
    url = "https://github.com/bincrafters/conan-libwebsockets"
    homepage = "https://github.com/warmcat/libwebsockets"
    license = "LGPL-2.1"
    topics = ("conan", "libwebsockets", "websocket")
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": ["mbedtls", "openssl", False],
        'lws_with_plugins' : [True, False],
        "lws_with_libuv": [True, False],
        "lws_with_libevent": [True, False],
        "lws_with_zlib": [True, False],
        "lws_with_ipv6" : [True, False],
        "lws_with_ranges" : [True, False],
        "lws_with_mqtt" : [True, False],
        "lws_with_http2" : [True, False],
        "lws_with_lwsws" : [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'ssl': False,
        'lws_with_plugins' : False,
        'lws_with_libuv': False,
        'lws_with_libevent': False,
        'lws_with_zlib': False,
        "lws_with_ipv6" :  False,
        "lws_with_ranges" :  False,
        "lws_with_mqtt" :  False,
        "lws_with_http2" :  False,
        "lws_with_lwsws" :  False
    }
    with_mbedtls = False
    with_ssl = False
    with_builtin_sha1=True
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.lws_with_libuv or self.options.lws_with_plugins:
            self.requires.add("libuv/1.34.2")
        if self.options.lws_with_libevent:
            self.requires.add("libevent/2.1.11")
        if self.options.lws_with_zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.ssl:
            self.with_ssl = True
            if self.options.ssl == "openssl":
                self.requires.add("openssl/1.1.1e")
                self.with_builtin_sha1 = False
            elif self.options.ssl == "mbedtls":
                self.requires.add("mbedtls/2.16.3-apache")
                self.with_mbedtls = True

    def source(self):
        tools.get(f'{self.homepage}/archive/v{self.version}-stable.tar.gz')
        extracted_dir = f'{self.name}-{self.version}-stable'
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LWS_WITHOUT_TESTAPPS"] = True
        cmake.definitions["LWS_LINK_TESTAPPS_DYNAMIC"] = True
        cmake.definitions["LWS_WITH_SHARED"] = self.options.shared
        cmake.definitions["LWS_WITH_STATIC"] = not self.options.shared
        cmake.definitions["LWS_WITH_LIBUV"] = self.options.lws_with_libuv
        cmake.definitions["LWS_WITH_LIBEVENT"] = self.options.lws_with_libevent

        cmake.definitions["LWS_WITH_ZLIB"] = self.options.lws_with_zlib
        cmake.definitions["LWS_WITH_BUNDLED_ZLIB"] = False
        cmake.definitions["LWS_WITHOUT_EXTENSIONS"] = not self.options.lws_with_zlib
        cmake.definitions["LWS_WITH_ZIP_FOPS"] = self.options.lws_with_zlib

        cmake.definitions["LWS_WITH_SSL"] = self.with_ssl
        cmake.definitions["LWS_WITH_MBEDTLS"] = self.with_mbedtls
        cmake.definitions["LWS_WITHOUT_BUILTIN_SHA1"] = not self.with_builtin_sha1

        cmake.definitions["LWS_IPV6"] = self.options.lws_with_ipv6
        cmake.definitions["LWS_WITH_RANGES"] = self.options.lws_with_ranges
        cmake.definitions["LWS_ROLE_MQTT"] = self.options.lws_with_mqtt
        cmake.definitions["LWS_WITH_HTTP2"] = self.options.lws_with_http2
        cmake.definitions["LWS_WITH_LWSWS"] = self.options.lws_with_lwsws

        cmake.definitions["LWS_WITH_PLUGINS"] = self.options.lws_with_plugins 

        if not self.options.shared and self.settings.os != "Windows":
            cmake.definitions["LWS_STATIC_PIC"] = self.options.fPIC

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])

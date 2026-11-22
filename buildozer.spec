
[app]

title = Control de Ventas
package.name = controlventas
package.domain = com.estacion

source.dir = .
source.include_exts = py,kv,png,jpg,atlas

version = 1.0

requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 36
android.minapi = 24
android.ndk = 28c
android.ndk_api = 24
android.accept_sdk_license = True

android.archs = arm64-v8a

p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1

[app]

title = Control de Ventas
package.name = controlventas
package.domain = com.estacion

source.dir = .
source.include_exts = py,kv,png,jpg,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 24
android.ndk = 27b
android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1

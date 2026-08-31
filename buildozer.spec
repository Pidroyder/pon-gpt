[app]
title = PonGPT
package.name = pongpt
package.domain = org.pongpt
icon.filename = icon.png
presplash.filename = presplash.png
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md
version = 1.0.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pillow,numpy,opencv,filetype==1.2.0,httpx==0.27.2,certifi,idna,sniffio,anyio,h11,httpcore,typing_extensions,exceptiongroup,ollama==0.3.3,picwish==0.6.0,SpeechRecognition
orientation = portrait
fullscreen = True
android.archs = arm64-v8a
android.api = 34
android.minapi = 24
android.accept_sdk_license = True
android.add_jars = mlkit-all.jar,OcrBridge.jar,lifecycle-extra.jar,javax.inject-1.jar,androidx-collection.jar,androidx-core.jar,firebase-encoders.jar,exifinterface.jar
android.meta_data = com.google.android.gms.version=12451000
android.add_aars = mlkit-natives.aar
android.add_gradle_repositories = flatDir { dirs 'libs' }
p4a.branch = master
p4a.commit = e155baf9f94ef6ef0589541210e9cdb20f960d52
android.permissions = INTERNET,RECORD_AUDIO,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.redirect_stdout = False

[buildozer]
log_level = 2
warn_on_root = 1

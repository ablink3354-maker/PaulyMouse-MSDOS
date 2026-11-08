param(
 [string]$Sdk=$env:ANDROID_HOME,
 [string]$Jdk=$env:JAVA_HOME,
 [string]$Python='python',
 [string]$StorePassword=$env:PAULY_STORE_PASSWORD,
 [switch]$ReuseGameArchive
)
if(!$Sdk){$Sdk=Join-Path $env:LOCALAPPDATA 'Android/Sdk'}
if(!$Jdk){$Jdk='C:/Program Files/Android/Android Studio/jbr'}
if(!$StorePassword){throw 'Define PAULY_STORE_PASSWORD o usa -StorePassword con la contraseña de TU clave local.'}
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$stage=Join-Path $PSScriptRoot 'build'
$tools=Join-Path $Sdk 'build-tools/35.0.0'
$android=Join-Path $Sdk 'platforms/android-35/android.jar'
New-Item -ItemType Directory -Force "$stage/classes","$stage/dex","$stage/stubs" | Out-Null
& "$Jdk/bin/javac.exe" -encoding UTF-8 -source 8 -target 8 -classpath $android -d "$stage/stubs" "$PSScriptRoot/compile-stubs/org/scummvm/scummvm/ScummVMActivity.java"
if($LASTEXITCODE){throw 'Compile-only stub failed'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
if(Test-Path "$stage/stubs.jar"){Remove-Item -LiteralPath "$stage/stubs.jar"}
[IO.Compression.ZipFile]::CreateFromDirectory("$stage/stubs","$stage/stubs.jar")
$files=@(Get-ChildItem "$PSScriptRoot/java" -Recurse -Filter '*.java').FullName
& "$Jdk/bin/javac.exe" -encoding UTF-8 -source 8 -target 8 -classpath "$android;$stage/stubs" -d "$stage/classes" @files
if($LASTEXITCODE){throw 'Java compilation failed'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
if(Test-Path "$stage/classes.jar"){Remove-Item -LiteralPath "$stage/classes.jar"}
[IO.Compression.ZipFile]::CreateFromDirectory("$stage/classes","$stage/classes.jar")
& "$Jdk/bin/java.exe" -cp "$tools/lib/d8.jar" com.android.tools.r8.D8 --min-api 23 --lib $android --classpath "$stage/stubs.jar" --output "$stage/dex" "$stage/classes.jar"
if($LASTEXITCODE){throw 'DEX compilation failed'}
if($ReuseGameArchive){& $Python "$PSScriptRoot/package-native.py" --reuse-game}
else {& $Python "$PSScriptRoot/package-native.py"}
if($LASTEXITCODE){throw 'Packaging failed'}
& "$tools/zipalign.exe" -f -p 4 "$stage/unsigned.apk" "$stage/aligned.apk"
if($LASTEXITCODE){throw 'Alignment failed'}
New-Item -ItemType Directory -Force (Join-Path $root 'dist') | Out-Null
$out=Join-Path $root 'dist/Pauly-Mouse-v0.4-es.apk'
& "$Jdk/bin/java.exe" -jar "$tools/lib/apksigner.jar" sign --ks "$root/signing/local-signing.jks" --ks-key-alias pauly --ks-pass pass:$StorePassword --key-pass pass:$StorePassword --out $out "$stage/aligned.apk"
if($LASTEXITCODE){throw 'Signing failed'}
& "$Jdk/bin/java.exe" -jar "$tools/lib/apksigner.jar" verify --verbose $out
if($LASTEXITCODE){throw 'Signature verification failed'}

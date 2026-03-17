@echo off
chcp 65001 >nul

REM 使用指定的 Python 3.12
set PYTHON_EXE=E:\runtime\Python312\python.exe

REM 打包模式：默认 onedir（启动更快）；传入 onefile 可切换单文件
set "BUILD_MODE=%~1"
if "%BUILD_MODE%"=="" set "BUILD_MODE=onedir"
set "PYI_BUNDLE_ARG=--onedir"
if /I "%BUILD_MODE%"=="onefile" set "PYI_BUNDLE_ARG=--onefile"

REM 统一从 settings.json 读取配置（不再通过命令行参数覆盖）
if not exist config mkdir config
if not exist config\settings.json (
    > config\settings.json (
        echo {
        echo   "app": {"name": "桌面管理程序", "logo_text": "DM", "icon_path": "resources/icon.png"},
        echo   "startup_page_url": ""
        echo }
    )
)

for /f "usebackq delims=" %%i in (`%PYTHON_EXE% -c "import json, pathlib; p=pathlib.Path('config/settings.json'); d=json.loads(p.read_text(encoding='utf-8')); print(d.get('app',{}).get('name','桌面管理程序'))"`) do set "APP_NAME=%%i"
for /f "usebackq delims=" %%i in (`%PYTHON_EXE% -c "import json, pathlib; p=pathlib.Path('config/settings.json'); d=json.loads(p.read_text(encoding='utf-8')); print(d.get('app',{}).get('icon_path','resources/icon.png'))"`) do set "APP_ICON_PATH=%%i"

if "%APP_NAME%"=="" set "APP_NAME=桌面管理程序"
if "%APP_ICON_PATH%"=="" set "APP_ICON_PATH=resources/icon.png"

set "ICON_EXT=%APP_ICON_PATH:~-4%"
set "ICON_OPTION="
if /I "%ICON_EXT%"==".ico" set "ICON_OPTION=--icon %APP_ICON_PATH%"
if /I "%ICON_EXT%"==".exe" set "ICON_OPTION=--icon %APP_ICON_PATH%"

echo ===== %APP_NAME% 打包工具（模式：%BUILD_MODE%） =====
echo.
if "%ICON_OPTION%"=="" (
    echo 提示：settings.json 中 app.icon_path 不是 .ico/.exe，已跳过 EXE 图标参数（运行时窗口图标仍可使用该路径）。
)

REM 确认 PyInstaller 已可用
echo 使用 PyInstaller 版本:
%PYTHON_EXE% -m PyInstaller --version
echo.

echo 开始打包...
echo 注意：打包过程可能需要几分钟，请耐心等待...
echo.

REM 打包命令 - 默认目录模式（启动更快），可切换 onefile
%PYTHON_EXE% -m PyInstaller ^
    --windowed ^
    %PYI_BUNDLE_ARG% ^
    --name "%APP_NAME%" ^
    %ICON_OPTION% ^
    --add-data "01-登录.html;." ^
    --add-data "02-主页面.html;." ^
    --add-data "03-设置.html;." ^
    --add-data "resources;resources" ^
    --add-data "config\settings.json;config" ^
    --add-data "components;components" ^
    --add-data "utils;utils" ^
    --hidden-import PyQt6.QtWebEngineWidgets ^
    --hidden-import PyQt6.QtWebEngineCore ^
    --hidden-import PyQt6.QtWebEngine ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtNetwork ^
    --hidden-import PyQt6.QtWebChannel ^
    --paths "E:\runtime\Python312\Lib\site-packages\PyQt6\Qt6\bin" ^
    main.py

if errorlevel 1 (
    echo.
    echo 打包失败！请检查上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ===== 打包完成 =====
echo 可执行文件位置: dist\%APP_NAME%\%APP_NAME%.exe （onefile 模式时为 dist\%APP_NAME%.exe）
echo.

if /I "%BUILD_MODE%"=="onedir" (
    echo.
    echo 正在生成单文件分发压缩包...
    powershell -NoProfile -Command "if (Test-Path 'dist\%APP_NAME%.zip') { Remove-Item 'dist\%APP_NAME%.zip' -Force }; Compress-Archive -Path 'dist\%APP_NAME%\*' -DestinationPath 'dist\%APP_NAME%.zip' -Force"
    if errorlevel 1 (
        echo 警告：压缩包生成失败，可直接分发 dist\%APP_NAME% 文件夹。
    ) else (
        echo 压缩包位置: dist\%APP_NAME%.zip
    )
)
echo 提示：如果遇到缺少模块的错误，可能需要添加更多的 --hidden-import 参数
echo.
pause

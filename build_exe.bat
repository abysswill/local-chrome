@echo off
chcp 65001 >nul

REM 使用指定的 Python 3.12
set PYTHON_EXE=E:\runtime\Python312\python.exe

REM 可选：设置程序名称 / 启动地址 / logo文字 / 图标路径
REM 用法：build_exe.bat "https://example.com/login" "桌面管理程序" "DM" "resources/icon.png"
set "STARTUP_PAGE_URL=%~1"
set "APP_NAME=%~2"
set "APP_LOGO_TEXT=%~3"
set "APP_ICON_PATH=%~4"
if "%APP_NAME%"=="" set "APP_NAME=桌面管理程序"
if "%APP_LOGO_TEXT%"=="" set "APP_LOGO_TEXT=DM"
if "%APP_ICON_PATH%"=="" set "APP_ICON_PATH=resources/icon.png"

echo ===== %APP_NAME% 打包工具 =====
echo.
if not "%STARTUP_PAGE_URL%"=="" (
    if not exist config mkdir config
    > config\settings.json (
        echo {
        echo   "app": {"name": "%APP_NAME%", "logo_text": "%APP_LOGO_TEXT%", "icon_path": "%APP_ICON_PATH%"},
        echo   "startup_page_url": "%STARTUP_PAGE_URL%"
        echo }
    )
    echo 已写入启动页面地址: %STARTUP_PAGE_URL%
) else (
    echo 未设置启动页面地址，默认使用 01-登录.html
)

REM 确保 settings.json 存在（仅打包该文件，避免把运行时缓存目录打进包）
if not exist config mkdir config
if not exist config\settings.json (
    > config\settings.json (
        echo {
        echo   "app": {"name": "%APP_NAME%", "logo_text": "%APP_LOGO_TEXT%", "icon_path": "%APP_ICON_PATH%"},
        echo   "startup_page_url": ""
        echo }
    )
)

REM 确认 PyInstaller 已可用
echo 使用 PyInstaller 版本:
%PYTHON_EXE% -m PyInstaller --version
echo.


echo 开始打包...
echo 注意：打包过程可能需要几分钟，请耐心等待...
echo.

REM 打包命令 - 单文件模式，修复 Qt WebEngine DLL 问题
%PYTHON_EXE% -m PyInstaller ^
    --windowed ^
    --onefile ^
    --name "%APP_NAME%" ^
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
echo 可执行文件位置: dist\%APP_NAME%.exe
echo.
echo 提示：如果遇到缺少模块的错误，可能需要添加更多的 --hidden-import 参数
echo.
pause

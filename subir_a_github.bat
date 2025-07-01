@echo off
echo Configurando Git...

REM CAMBIAR los datos de usuario según corresponda
git config --global user.name "El Pastorcito"
git config --global user.email "elpastorcito.belgrano@gmail.com"

echo Eliminando origin anterior si existe...
git remote remove origin

echo Inicializando repositorio...
git init
git add .
git commit -m "Primera versión"
git branch -M main

REM CAMBIAR esta URL por la del repositorio real en GitHub
git remote add origin https://github.com/elpastorcito/recibo_viandas.git

echo Subiendo a GitHub...
git push -u origin main

echo Listo. Presioná una tecla para cerrar...
pause



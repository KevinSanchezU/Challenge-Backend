# Backend proyect - FLASK API
REST API que permite la suba y descarga de archivos en la nube con el servicio de AWS S3, con autenticación basada en JWT y gestion de base de datos con SQLAlchemy

## Estado del proyecto
Actualmente en desarrollo.

Implementación de funcionalidades basicas como subida y bajada de archivos

Autenticación de usuarios y admin

Falta implementar la base de datos, pruebas, documentación y optimizaciones para el despliegue a producción


## Tecnologias
- Lenguaje: Python
- Framework: Flask
- Servicio de almacenamiento: Amazon S3
- Autenticación: JWT con flask-jwt-extended
- Base de datos: SQLAlchemy

## Como usar

Es necesario crear un archivo '.env' en la raiz del proyecto con sus propias variables de entorno, hay un archivo .env_ejemplo.txt que presenta un archivo .env de ejemplo

Los usuarios aceptados son "usuario1", contraseña "1234" o "admin" contraseña "admin"

Debe hacerse un POST al endpoint "/" con el siguiente formato json:

{
	"username": "usuario1",
	"password": "1234"
}

Esto nos devolvera un TOKEN que debemos usar para poder acceder a los demas endpoints

"/access_granted" - Metodo GET que devuelve información de los archivos subidos en la nube

"/access_granted" - Metodo POST que sube archivos a la nube

"/access_granted/<file_name>" - Metodo GET que descarga el archivo <file_name> a una carpeta previamente creada "downloads/"

"/stats" - Metodo GET solo accesible para usuario admin

CREATE DATABASE app_finanzas;
USE DATABASE app_finanzas;

CREATE TABLE `usuarios` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(255) UNIQUE,
  `correo` VARCHAR(255) UNIQUE,
  `clave` VARCHAR(255) NOT NULL
);

CREATE TABLE `Categoria` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` VARCHAR(255),
     `tipo` INT
);

CREATE TABLE `divisa` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `simbolo` VARCHAR(255) NOT NULL
);


CREATE TABLE `ingresos` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `categoria_id` INTEGER,
  `divisa_id` INTEGER,
  `usuario_id` INTEGER,
  `cantidad` DECIMAL(10, 2) NOT NULL,
  `fecha` DATE NOT NULL,
  FOREIGN KEY (`categoria_id`) REFERENCES `Categoria` (`id`),
  FOREIGN KEY (`divisa_id`) REFERENCES `divisa` (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
);

CREATE TABLE `egresos` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `categoria_id` INTEGER,
  `usuario_id` INTEGER,
  `divisa_id` INTEGER,
  `cantidad` DECIMAL(10, 2) NOT NULL,
  `habitual` INTEGER NOT NULL,
  `fecha_pago` DATE,
  `fecha` DATE,
  `estado` INTEGER,
  FOREIGN KEY (`categoria_id`) REFERENCES `Categoria` (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`divisa_id`) REFERENCES `divisa` (`id`)
);

CREATE TABLE `movimientos` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `usuario_id` INTEGER,
  `divisa_id` INTEGER,
  `cantidad` DECIMAL(10, 2) NOT NULL,
  `concepto` VARCHAR(255),
  `tipo` VARCHAR(255) NOT NULL,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`divisa_id`) REFERENCES `divisa` (`id`)
);

CREATE TABLE `notificacion` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `usuario_id` INTEGER,
  `descripcion` VARCHAR(255),
  `medio` VARCHAR(255) NOT NULL,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
);

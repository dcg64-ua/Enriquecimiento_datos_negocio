USE enriquecimiento_datos_negocio;

CREATE TABLE `html` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` varchar(2083) NOT NULL,
  `html` longtext NOT NULL,
  `profundidad` int DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : mar. 27 mai 2025 à 09:17
-- Version du serveur : 9.1.0
-- Version de PHP : 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `vote_user`
--

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `firstname` varchar(100) NOT NULL,
  `lastname` varchar(100) NOT NULL,
  `password_user` varchar(255) NOT NULL,
  `role` enum('student','teacher') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `firstname`, `lastname`, `password_user`, `role`) VALUES
(1, 'Alice', 'Martin', 'hashedpassword1', 'teacher'),
(2, 'Bob', 'Durand', 'hashedpassword2', 'teacher'),
(3, 'Emma', 'Leroy', 'hashedpassword3', 'student'),
(4, 'Lucas', 'Moreau', 'hashedpassword4', 'student'),
(5, 'Chloé', 'Petit', 'hashedpassword5', 'student'),
(6, 'Nathan', 'Roux', 'hashedpassword6', 'student'),
(7, 'Léa', 'Faure', 'hashedpassword7', 'student'),
(8, 'Louis', 'Garnier', 'hashedpassword8', 'student'),
(9, 'Manon', 'Blanc', 'hashedpassword9', 'student'),
(10, 'Jules', 'Henry', 'hashedpassword10', 'student'),
(11, 'Camille', 'Lemoine', 'hashedpassword11', 'student'),
(12, 'Mathis', 'Michel', 'hashedpassword12', 'student'),
(13, 'Sarah', 'Fernandez', 'hashedpassword13', 'student'),
(14, 'Enzo', 'Garcia', 'hashedpassword14', 'student'),
(15, 'Louise', 'Perrin', 'hashedpassword15', 'student'),
(16, 'Hugo', 'Martinez', 'hashedpassword16', 'student'),
(17, 'Clara', 'Chevalier', 'hashedpassword17', 'student'),
(18, 'Ethan', 'Dupuis', 'hashedpassword18', 'student'),
(19, 'Inès', 'Robin', 'hashedpassword19', 'student'),
(20, 'Noah', 'Colin', 'hashedpassword20', 'student'),
(21, 'Julia', 'Marchand', 'hashedpassword21', 'student'),
(22, 'Maxime', 'Gauthier', 'hashedpassword22', 'student');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

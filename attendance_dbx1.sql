-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 16, 2026 at 10:49 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `attendance_dbx1`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('a7f2c1d9b8e4');

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `check_in_time` datetime DEFAULT NULL,
  `check_out_time` datetime DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `working_hours` float DEFAULT NULL,
  `overtime_hours` float DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `check_in_photo` varchar(255) DEFAULT NULL,
  `check_out_photo` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `check_in_time_2` datetime DEFAULT NULL,
  `check_out_time_2` datetime DEFAULT NULL,
  `check_in_photo_2` varchar(255) DEFAULT NULL,
  `check_out_photo_2` varchar(255) DEFAULT NULL,
  `overtime_check_in_time` datetime DEFAULT NULL,
  `overtime_check_out_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `employee_id`, `date`, `check_in_time`, `check_out_time`, `status`, `working_hours`, `overtime_hours`, `notes`, `check_in_photo`, `check_out_photo`, `created_at`, `updated_at`, `check_in_time_2`, `check_out_time_2`, `check_in_photo_2`, `check_out_photo_2`, `overtime_check_in_time`, `overtime_check_out_time`) VALUES
(122, 27, '2026-05-24', NULL, NULL, 'absent', 0, 0, NULL, NULL, NULL, '2026-06-03 09:37:10', '2026-06-03 09:37:10', NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `departments`
--

CREATE TABLE `departments` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `manager_id` int(11) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `display_order` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `id` int(11) NOT NULL,
  `employee_code` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `face_encoding` blob DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `hire_date` date DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`id`, `employee_code`, `name`, `email`, `phone`, `department_id`, `department`, `position`, `face_encoding`, `photo_path`, `is_active`, `hire_date`, `notes`, `created_at`, `updated_at`) VALUES
(27, 'NV002', 'Phạm Thị A', '202220@eaut.edu.vn', '0333614541', NULL, NULL, 'Công nhân', NULL, NULL, 1, '2026-05-05', NULL, '2026-05-20 13:47:52', '2026-05-20 13:47:52'),
(28, 'NV003', 'Phạm Thị B', '2022201@eaut.edu.vn', '0333614541', NULL, NULL, 'gallery', NULL, NULL, 1, '2026-05-05', NULL, '2026-05-20 13:49:15', '2026-05-20 13:49:15'),
(30, 'NV005', 'Phạm Thị D', '2022012@eaut.edu.vn', '0333614541', NULL, NULL, 'developer', NULL, NULL, 1, '2026-05-05', NULL, '2026-05-20 13:50:09', '2026-05-20 13:50:09'),
(31, 'NV006', 'Phạm Thị D', '202012@eaut.edu.vn', '0333614541', NULL, NULL, 'developer', NULL, NULL, 1, '2026-05-05', NULL, '2026-05-20 13:50:21', '2026-05-20 13:50:21'),
(32, 'NV007', 'Phạm Thị E', '20239558@gmail.com', '0333614541', NULL, NULL, 'developer', NULL, NULL, 1, '2026-05-05', NULL, '2026-05-20 13:50:56', '2026-05-20 13:50:56'),
(33, 'NV008', 'Phạm Thị F', '514546@mail.com', '0333614541', NULL, NULL, 'test', NULL, NULL, 1, NULL, NULL, '2026-05-20 13:51:30', '2026-05-24 09:17:59'),
(37, 'NV010', 'Phạm Thị F', '51454776@mail.com', '0333614541', NULL, NULL, 'top-banner', NULL, NULL, 1, NULL, NULL, '2026-05-24 09:18:21', '2026-05-24 09:18:21'),
(41, 'NV011', 'Phạm Thị Thảo', '20222082@eaut.edu.vn', '0333614541', NULL, NULL, 'None', NULL, NULL, 1, NULL, NULL, '2026-06-16 11:45:19', '2026-06-16 14:06:45'),
(42, 'NV012', 'Phạm Thị Thảo', '2022208222@eaut.edu.vn', '0333614541', NULL, NULL, 'None', NULL, NULL, 1, NULL, NULL, '2026-06-16 11:48:59', '2026-06-16 14:06:14');

-- --------------------------------------------------------

--
-- Table structure for table `face_embeddings`
--

CREATE TABLE `face_embeddings` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `employee_code` varchar(20) NOT NULL,
  `embedding_data` blob NOT NULL,
  `embedding_type` varchar(50) DEFAULT NULL,
  `embedding_shape` varchar(50) DEFAULT NULL,
  `variant_type` varchar(50) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `quality_score` float DEFAULT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `face_embeddings`
--

INSERT INTO `face_embeddings` (`id`, `employee_id`, `employee_code`, `embedding_data`, `embedding_type`, `embedding_shape`, `variant_type`, `description`, `photo_path`, `quality_score`, `is_primary`, `is_active`, `created_at`, `updated_at`) VALUES
(54, 41, 'NV011', 0x8004958b040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014b80859468038c0564747970659493948c02663894898887945294284b038c013c944e4e4e4affffffff4affffffff4b007494628942000400000000002023d4c2bf000000807db1bd3f000000203353b23f000000004ca89ebf000000c0e3a3bcbf00000000577dbcbf000000c0529d9dbf000000c0badbb8bf00000060f3afc03f0000004037a3b2bf000000e05c21d23f00000020e518b4bf000000409d4fcdbf000000a0bb38bdbf0000000022ac9a3f00000020dd2ec73f000000c0ef02c8bf00000040b8c2c0bf00000000360d6d3f00000020c5f993bf000000c0c65fa93f000000203b6e99bf00000000b6958c3f000000a076a1b63f00000020c86d96bf000000c06a97d9bf000000009d35bcbf000000403749c4bf000000801413a53f00000000817aadbf000000c0ae4d90bf000000407f4db93f000000e05e4dc9bf00000040c12ec0bf00000080a9129f3f00000020cb30b53f00000080ae2a723f0000008017bdb03f000000e00d06c93f000000e0627a9a3f0000002023a0c6bf000000e0496d993f000000c06836a33f0000002046ced13f0000000068f0b83f00000060aa8fbe3f00000000d3fda73f000000401dbeb8bf000000e03636b13f000000e05cf5c2bf000000c02498b23f00000080ab47c63f000000c02d27c13f0000006047fab83f000000001edda8bf00000020de6ccbbf0000004019a4b23f000000c0cfcba23f000000c09a2ecebf00000040db85b53f000000604a62c13f000000c02856b4bf000000807d64afbf00000040b6af933f00000060e5e4d73f000000a00fbeaf3f000000c03c60c5bf000000a0e586bebf0000004048c9bc3f00000040954ab8bf000000205ddeafbf000000007518af3f000000a06880cabf000000c07a3ec1bf000000a07f6bd3bf000000809c1cbc3f00000060c993db3f000000a0708ca23f000000c00f20cbbf000000407cf6983f000000809b69c2bf000000200d9a9cbf000000204504a33f000000e068c2c63f000000407614acbf000000c06ae6993f000000807b23b3bf000000c0abf37bbf000000402b68b63f000000409cdd97bf000000c039a291bf000000a0429bce3f000000c024c8883f00000040a171c53f000000209a6d933f000000209360a03f000000c06d3aacbf000000a05d14afbf000000001c7bbdbf00000040a542aebf000000c0f8018cbf00000040450ab1bf000000c08bd1acbf000000006082b23f000000a0de17c9bf000000409a83c23f000000c009ca8f3f000000c0aac1a13f00000000bffeacbf00000040a9a3b13f000000804c43b0bf000000006e13babf00000080d200bc3f000000a03e44d0bf000000407d94d13f000000009570cc3f00000080001ab53f000000c0b081c13f000000603f87ba3f000000806863b23f00000000f22d85bf000000404eaba7bf00000000a7d2c4bf0000000026b083bf0000008053e0be3f000000c0267ca3bf000000e0f915ab3f0000002074a2993f947494622e, 'standard', '(128,)', 'default', 'Auto 3-angle - Chính diện', NULL, NULL, 1, 1, '2026-06-16 14:06:41', '2026-06-16 14:06:41'),
(55, 41, 'NV011', 0x8004958b040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014b80859468038c0564747970659493948c02663894898887945294284b038c013c944e4e4e4affffffff4affffffff4b007494628942000400000000002073cbc0bf00000060f686c33f000000a06abab63f00000020465da2bf000000205008bfbf0000002026e4b9bf00000020bcf698bf00000000e670b5bf00000000ea9fc43f000000a0c92eb1bf000000c00f3fd33f0000004045e0b6bf000000a032a3cbbf000000000aa1b9bf000000c089cea43f00000060f01cca3f0000002027bdcdbf00000040d6fdc3bf00000080dee593bf000000403e75b4bf000000408f71a23f00000060119a96bf000000e02e2191bf00000080d213bb3f0000000035ada7bf000000205ba3d9bf000000c028dcbbbf0000004094f6c4bf000000401ee9ae3f00000040f570b5bf00000000d18c66bf000000a0430cb63f000000209d53cabf00000060d433bdbf00000020d3fc933f00000080dd42943f000000c01418693f000000c0f1f6853f000000e0eeeac73f000000401a40933f00000060223cc4bf000000008ea6a03f000000a01504b13f00000080e9cfd13f000000c08034b63f000000c07f06bb3f00000040b813b03f000000207b41b3bf000000409c26b63f000000c074b7c1bf000000c0cdfaa43f000000c00b26c63f000000a040b6c23f00000040f90db73f00000040e06194bf000000e0b58dcdbf000000805834ad3f000000801a8faa3f00000020ab27cdbf000000c03b27b53f000000c02bf9bf3f000000c04131bbbf000000a08657b8bf00000060f07c68bf000000200869d83f000000202c3db33f000000a04b5ac2bf00000080e936c3bf000000800f47bc3f000000c07aafb1bf00000060d26eb2bf0000000024f2b23f00000020ae32cabf00000060ad2cbebf000000a09a9fd4bf00000000df95bc3f000000409b35db3f00000040879b9a3f000000e03150cbbf0000000088a7a73f000000a0c1dbbfbf00000020450f923f0000004055d09f3f00000060372cc73f0000006056e1b6bf0000002075ab903f000000a065f0b9bf000000800de37b3f000000a0b566b33f000000a0e88c93bf00000020bee697bf000000c08076cb3f00000080ab16803f000000c027f8c13f00000060202573bf00000000b0ce733f000000c01f6bb4bf00000000d645b1bf00000000aa05b6bf000000205321adbf0000008092c97a3f000000003cab7dbf00000060001cb4bf000000c0863daf3f000000605b57c8bf000000805c3ebc3f00000080f83e8a3f000000a0ea9a913f00000060bf2cb8bf00000040d90eb13f000000404716a6bf000000a0e674b5bf0000002015a8b63f000000c05fcfd2bf000000c0e548ce3f000000208569cb3f0000006064b1aa3f000000e0920dc33f000000c0e460b33f000000c0b909ad3f000000c05449a1bf000000406e42a8bf00000040578ac4bf000000e088fa87bf000000e04693c13f000000401439a6bf00000060d600a83f00000040f8fe853f947494622e, 'standard', '(128,)', 'profile_left', 'Auto 3-angle - Nghiêng trái', NULL, NULL, 0, 1, '2026-06-16 14:06:42', '2026-06-16 14:06:42'),
(56, 41, 'NV011', 0x8004958b040000000000008c156e756d70792e636f72652e6d756c74696172726179948c0c5f7265636f6e7374727563749493948c056e756d7079948c076e6461727261799493944b0085944301629487945294284b014b80859468038c0564747970659493948c02663894898887945294284b038c013c944e4e4e4affffffff4affffffff4b00749462894200040000000000606f0ac2bf00000040b9a2c23f000000207c43b73f00000060fa1db0bf000000009723bebf00000040ccd0b8bf000000404f209bbf000000400877c1bf000000607fa4bb3f00000000556cb8bf000000806553d43f000000406377b8bf000000603711cebf000000a06e90c0bf000000006de1943f00000040b654c93f000000006d5ac9bf0000004089f1c1bf000000a067e296bf000000805b6b96bf000000a0a3cca53f0000006039429abf0000008027a6a63f00000080e438b43f000000409d3da8bf00000080f3a4d8bf000000e0630dc0bf0000006007bdc0bf00000040f40d903f00000020e419a0bf000000801f619fbf000000000818ac3f000000001247ccbf000000a02ad5b4bf0000006004d384bf000000e0f1f79f3f000000a02e2aa2bf000000c0db59a73f0000006066fbc53f000000e0c0de9a3f000000204193c8bf000000404e489d3f0000006064f3a53f0000008055e8d03f000000c0c4dab63f00000060c337c03f00000020ebbfb13f000000c052dfb7bf00000040f1d6a73f000000807881c1bf00000000a003b33f000000408b79c53f000000a0f79fc23f00000040c63d983f000000c066dca0bf00000040cbe7cbbf0000004088d2993f000000e0ca5db03f000000a075f6c6bf00000000c408b63f000000a0134fc13f000000a0e0b9b6bf000000c0ee79b8bf0000002087dda6bf000000801a90d73f00000060a57fb43f000000201a83c6bf000000c0796fbfbf00000040afa2bf3f000000c0d645b0bf000000c05f93adbf000000604935b13f00000060727bccbf00000080d01bc3bf00000040c5dbd5bf0000000088f6b53f000000800848da3f00000080aa638b3f000000200ae7c9bf00000000843472bf000000009e91c1bf000000a07edaa83f000000e05ca7a43f000000602139c73f000000e027cbb2bf00000000cc2c933f00000040824ec0bf00000080866d90bf000000e02c53b43f0000004012f5b6bf000000a077ac9bbf000000606ae4cc3f000000007759773f000000a05fc5c03f000000802cb19dbf000000c07d4d733f000000c06b94b3bf0000008073f0abbf000000c030fbb7bf00000060f8a097bf00000040591399bf00000060aa1aabbf00000020d091b7bf000000e03ec6b23f000000e09e7ec5bf000000006f11b93f00000000e222953f0000002044c0913f00000040319bb1bf00000020871daa3f0000006039afb2bf0000004095eec1bf00000020bc9db23f000000e039a3d0bf000000c05dc0cb3f00000080544fce3f000000206396ab3f00000040c4c1c13f00000000f8dbbe3f00000080c452b73f000000e08a2aa3bf00000040099087bf000000e01472c6bf000000205ce38fbf000000e0ebcdc13f000000004cf5a6bf00000020653fad3f000000c02a05953f947494622e, 'standard', '(128,)', 'profile_right', 'Auto 3-angle - Nghiêng phải', NULL, NULL, 0, 1, '2026-06-16 14:06:44', '2026-06-16 14:06:44');

-- --------------------------------------------------------

--
-- Table structure for table `leave_requests`
--

CREATE TABLE `leave_requests` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `reason` text DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `reviewer_id` int(11) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `admin_note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `leave_requests`
--

INSERT INTO `leave_requests` (`id`, `employee_id`, `start_date`, `end_date`, `reason`, `status`, `created_at`, `updated_at`, `reviewer_id`, `reviewed_at`, `admin_note`) VALUES
(6, 27, '2026-06-09', '2026-06-09', '', 'pending', '2026-06-03 09:59:23', '2026-06-03 09:59:23', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `overtime_requests`
--

CREATE TABLE `overtime_requests` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `hours` float NOT NULL,
  `reason` text DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `reviewer_id` int(11) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `admin_note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `overtime_requests`
--

INSERT INTO `overtime_requests` (`id`, `employee_id`, `date`, `hours`, `reason`, `status`, `created_at`, `updated_at`, `reviewer_id`, `reviewed_at`, `admin_note`) VALUES
(4, 27, '2026-05-24', 8, 'Đăng ký làm Chủ nhật', 'approved', '2026-05-20 19:22:49', '2026-06-03 09:37:10', 1, '2026-06-03 09:37:10', NULL),
(9, 27, '2026-06-04', 2.5, 'Tăng ca 17:30 - 20:00', 'pending', '2026-06-03 09:59:07', '2026-06-03 09:59:07', NULL, NULL, NULL),
(10, 37, '2026-06-05', 2.5, 'Tăng ca 17:30 - 20:00', 'pending', '2026-06-03 12:01:33', '2026-06-03 12:01:33', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `permissions`
--

CREATE TABLE `permissions` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `is_system` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `role_permissions`
--

CREATE TABLE `role_permissions` (
  `id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `system_logs`
--

CREATE TABLE `system_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` int(11) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `system_logs`
--

INSERT INTO `system_logs` (`id`, `user_id`, `action`, `entity_type`, `entity_id`, `details`, `ip_address`, `user_agent`, `status`, `created_at`) VALUES
(1, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 18:44:16'),
(2, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 19:29:18'),
(3, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 19:29:27'),
(4, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 19:55:16'),
(5, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36', 'success', '2026-05-06 19:56:34'),
(6, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 22:10:59'),
(7, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.22621.4249', 'success', '2026-05-06 22:14:41'),
(8, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.22621.4249', 'success', '2026-05-06 22:15:06'),
(9, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.22621.4249', 'success', '2026-05-06 22:23:58'),
(10, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:30:15'),
(11, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 22:30:28'),
(12, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:31:53'),
(13, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 22:32:15'),
(14, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 22:33:13'),
(15, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:35:04'),
(16, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 22:35:19'),
(17, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.119.0 Chrome/142.0.7444.265 Electron/39.8.8 Safari/537.36', 'success', '2026-05-06 22:42:18'),
(18, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:43:20'),
(19, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.119.0 Chrome/142.0.7444.265 Electron/39.8.8 Safari/537.36', 'success', '2026-05-06 22:43:32'),
(20, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:58:17'),
(21, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.119.0 Chrome/142.0.7444.265 Electron/39.8.8 Safari/537.36', 'success', '2026-05-06 22:58:30'),
(22, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 22:58:47'),
(23, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.119.0 Chrome/142.0.7444.265 Electron/39.8.8 Safari/537.36', 'success', '2026-05-06 22:58:59'),
(24, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:02:06'),
(25, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:02:16'),
(26, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:05:56'),
(27, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:06:19'),
(28, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:07:20'),
(29, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:07:30'),
(30, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:09:14'),
(31, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:09:26'),
(32, 3, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:09:58'),
(33, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:10:07'),
(34, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:12:05'),
(35, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:12:21'),
(36, 3, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:19:04'),
(37, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:19:08'),
(38, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:24:31'),
(39, 3, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-06 23:24:50'),
(40, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-06 23:24:59'),
(41, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.22621.4249', 'success', '2026-05-06 23:26:22'),
(42, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 00:20:25'),
(43, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 00:20:34'),
(44, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 10:34:27'),
(45, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 10:35:35'),
(46, 3, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 10:35:50'),
(47, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:12:22'),
(48, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:12:58'),
(49, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:19:12'),
(50, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:19:25'),
(51, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:19:44'),
(52, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:20:34'),
(53, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:20:50'),
(54, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:21:50'),
(55, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:22:08'),
(56, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:34:31'),
(57, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:34:37'),
(58, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:41:33'),
(59, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:41:40'),
(60, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:41:48'),
(61, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:42:26'),
(62, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 14:47:25'),
(63, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 14:47:40'),
(64, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:03:02'),
(65, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:03:05'),
(66, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:15:19'),
(67, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:15:22'),
(68, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:19:16'),
(69, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:19:19'),
(70, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:22:02'),
(71, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:22:05'),
(72, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:29:17'),
(73, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:36:03'),
(74, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:36:23'),
(75, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:38:09'),
(76, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 15:41:15'),
(77, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 15:41:22'),
(78, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 21:43:24'),
(79, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 21:46:37'),
(80, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 21:46:45'),
(81, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 21:52:31'),
(82, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 21:52:38'),
(83, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.119.0 Chrome/142.0.7444.265 Electron/39.8.8 Safari/537.36', 'success', '2026-05-07 21:52:42'),
(84, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-07 21:55:00'),
(85, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 21:57:57'),
(86, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:10:31'),
(87, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 22:10:45'),
(88, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:15:06'),
(89, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 22:18:27'),
(90, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:18:34'),
(91, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 22:20:01'),
(92, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:20:44'),
(93, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 22:21:04'),
(94, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:21:33'),
(95, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-07 22:22:31'),
(96, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-07 22:23:15'),
(97, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 13:00:17'),
(98, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 13:00:45'),
(99, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 13:31:28'),
(100, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 13:54:29'),
(101, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 14:24:46'),
(102, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 14:25:17'),
(103, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 14:48:02'),
(104, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 14:48:48'),
(105, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 15:05:23'),
(106, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 15:05:28'),
(107, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 15:34:32'),
(108, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 15:36:06'),
(109, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 15:36:30'),
(110, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-08 15:36:42'),
(111, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0', 'success', '2026-05-08 15:36:57'),
(112, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 11:24:37'),
(113, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 11:35:22'),
(114, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 11:41:05'),
(115, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 11:56:23'),
(116, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 11:56:44'),
(117, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 11:56:55'),
(118, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 11:57:12'),
(119, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 11:57:38'),
(120, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 12:54:43'),
(121, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 12:56:07'),
(122, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 13:03:53'),
(123, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Python-urllib/3.11', 'success', '2026-05-15 13:08:19'),
(124, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Python-urllib/3.11', 'success', '2026-05-15 13:09:34'),
(125, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 13:11:15'),
(126, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 13:11:23'),
(127, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 13:11:28'),
(128, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 13:12:01'),
(129, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 13:38:04'),
(130, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 13:38:49'),
(131, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-15 13:44:21'),
(132, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-15 13:44:22'),
(133, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-15 13:46:11'),
(134, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-15 13:46:13'),
(135, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 17:25:45'),
(136, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 17:25:58'),
(137, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 17:26:24'),
(138, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-15 17:44:54'),
(139, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 17:45:25'),
(140, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 20:50:07'),
(141, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 22:26:11'),
(142, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-15 22:59:41'),
(143, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-16 06:38:12'),
(144, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 10:39:44'),
(145, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 10:40:41'),
(146, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 10:41:07'),
(147, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 10:52:06'),
(148, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 10:52:14'),
(149, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:00:37'),
(150, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:00:47'),
(151, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:09:06'),
(152, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:10:25'),
(153, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:11:26'),
(154, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:12:13'),
(155, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:32:21'),
(156, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:32:38'),
(157, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:32:44'),
(158, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:32:58'),
(159, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:33:07'),
(160, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:35:35'),
(161, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:35:38'),
(162, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:36:05'),
(163, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:37:56'),
(164, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 11:54:13'),
(165, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 11:54:20'),
(166, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 12:03:56'),
(167, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 12:29:13'),
(168, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 14:42:26'),
(169, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 14:42:46'),
(170, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 14:43:37'),
(171, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 14:43:50'),
(172, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 14:44:02'),
(173, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 14:46:28'),
(174, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 14:55:35'),
(175, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 14:55:51'),
(176, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 19:50:57'),
(177, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 19:51:01'),
(178, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 19:51:22'),
(179, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 20:51:45'),
(180, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 21:05:38'),
(181, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 21:05:52'),
(182, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-19 21:52:44'),
(183, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-19 22:00:24'),
(184, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-19 22:14:53'),
(185, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-19 22:15:05'),
(186, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:35:36'),
(187, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:35:50'),
(188, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:36:02'),
(189, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:36:14'),
(190, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:36:26'),
(191, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:38:20'),
(192, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:38:33'),
(193, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:42:25'),
(194, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:42:47'),
(195, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:48:22'),
(196, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:49:05'),
(197, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:50:55'),
(198, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:51:06'),
(199, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:51:58'),
(200, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:53:49'),
(201, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:54:09'),
(202, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:55:42'),
(203, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:55:56'),
(204, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:59:33'),
(205, 2, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 10:59:41'),
(206, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 10:59:53'),
(207, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 11:03:01'),
(208, NULL, 'notification_overtime_approved', 'employee', 23, 'Yêu cầu tăng ca ngày 2026-05-20 đã được duyệt.', NULL, NULL, 'success', '2026-05-20 11:04:53'),
(209, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 11:06:53'),
(210, 2, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 11:07:07'),
(211, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 11:09:48'),
(212, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 11:10:33'),
(213, NULL, 'notification_leave_rejected', 'employee', 23, 'Yêu cầu xin nghỉ 2026-05-20 -> 2026-05-20 bị từ chối. Lý do: Không có', NULL, NULL, 'success', '2026-05-20 11:11:17'),
(214, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 13:46:05'),
(215, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 13:52:29'),
(216, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 13:56:09'),
(217, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 13:58:17'),
(218, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 13:58:46'),
(219, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 14:37:39'),
(220, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 14:37:56'),
(221, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 14:40:07'),
(222, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 14:40:31'),
(223, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 14:40:43'),
(224, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 14:40:52'),
(225, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 14:41:38'),
(226, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 14:41:47'),
(227, NULL, 'notification_overtime_approved', 'employee', 26, 'Yêu cầu tăng ca ngày 2026-05-20 đã được duyệt.', NULL, NULL, 'success', '2026-05-20 14:41:52'),
(228, NULL, 'notification_leave_approved', 'employee', 26, 'Yêu cầu xin nghỉ 2026-05-20 -> 2026-05-20 đã được duyệt.', NULL, NULL, 'success', '2026-05-20 14:41:54'),
(229, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:43:54'),
(230, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:43:57'),
(231, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:46:47'),
(232, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:46:51'),
(233, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:48:40'),
(234, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:49:10'),
(235, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:50:28'),
(236, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:50:31'),
(237, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:52:10'),
(238, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Werkzeug/2.3.7', 'success', '2026-05-20 15:52:38'),
(239, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 15:53:51'),
(240, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 15:54:22'),
(241, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 15:54:34'),
(242, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 15:54:44'),
(243, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 15:55:04'),
(244, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 15:55:22'),
(245, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 15:55:50'),
(246, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:03:34'),
(247, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:03:49'),
(248, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:05:29'),
(249, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:05:35'),
(250, NULL, 'notification_leave_rejected', 'employee', 26, 'Yêu cầu xin nghỉ 2026-05-26 -> 2026-05-28 bị từ chối. Lý do: Không có', NULL, NULL, 'success', '2026-05-20 16:05:48'),
(251, NULL, 'notification_overtime_approved', 'employee', 26, 'Yêu cầu tăng ca ngày 2026-05-25 đã được duyệt.', NULL, NULL, 'success', '2026-05-20 16:05:56'),
(252, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:07:21'),
(253, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:07:33'),
(254, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:08:01'),
(255, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:08:11'),
(256, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:25:55'),
(257, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:26:05'),
(258, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:26:14'),
(259, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:26:33'),
(260, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:32:28'),
(261, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:32:46'),
(262, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 16:49:02'),
(263, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 16:49:12'),
(264, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 18:21:29'),
(265, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 18:41:45'),
(266, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:18:14'),
(267, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:19:14'),
(268, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:22:01'),
(269, 6, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:22:20'),
(270, 6, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:23:35'),
(271, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:23:47'),
(272, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:29:36'),
(273, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:29:52'),
(274, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:32:11'),
(275, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:33:43'),
(276, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:34:31'),
(277, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:34:42'),
(278, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:44:24'),
(279, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:44:39'),
(280, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:45:53'),
(281, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:46:04'),
(282, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:47:01'),
(283, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:49:14'),
(284, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:51:21'),
(285, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:51:51'),
(286, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:53:18'),
(287, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:54:11'),
(288, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:56:18'),
(289, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:56:27'),
(290, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 19:59:02'),
(291, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 19:59:13'),
(292, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 21:35:52'),
(293, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 21:36:22'),
(294, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 21:38:29'),
(295, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 21:38:56'),
(296, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 21:39:20'),
(297, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 21:42:30'),
(298, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-20 21:42:47'),
(299, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-20 21:43:44'),
(300, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-21 10:00:20'),
(301, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-21 10:05:33'),
(302, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-21 10:05:44'),
(303, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-21 16:41:50'),
(304, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-21 16:48:30'),
(305, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-21 16:48:54'),
(306, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-05-21 16:50:32'),
(307, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-22 18:32:59'),
(308, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-05-24 08:57:54'),
(309, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 08:59:53'),
(310, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:00:19'),
(311, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:00:45'),
(312, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:08:12'),
(313, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:08:33'),
(314, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:08:59'),
(315, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36', 'success', '2026-06-03 09:10:12'),
(316, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:10:46'),
(317, 5, 'employee_withdrew_overtime_request', 'employee', 26, 'Phạm Thị Thảo đã thu hồi yêu cầu #5.', NULL, NULL, 'success', '2026-06-03 09:10:52'),
(318, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:10:57'),
(319, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:12:55'),
(320, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:15:08'),
(321, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:15:23');
INSERT INTO `system_logs` (`id`, `user_id`, `action`, `entity_type`, `entity_id`, `details`, `ip_address`, `user_agent`, `status`, `created_at`) VALUES
(322, 5, 'employee_withdrew_overtime_request', 'employee', 26, 'Phạm Thị Thảo đã thu hồi yêu cầu #6.', NULL, NULL, 'success', '2026-06-03 09:15:36'),
(323, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:17:05'),
(324, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:17:18'),
(325, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:24:01'),
(326, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:29:29'),
(327, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:30:56'),
(328, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:31:12'),
(329, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:31:55'),
(330, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:32:22'),
(331, NULL, 'notification_overtime_approved', 'employee', 26, 'Yêu cầu tăng ca ngày 2026-06-04 đã được duyệt.', NULL, NULL, 'success', '2026-06-03 09:32:32'),
(332, NULL, 'notification_overtime_approved', 'employee', 27, 'Yêu cầu tăng ca ngày 2026-05-24 đã được duyệt.', NULL, NULL, 'success', '2026-06-03 09:37:10'),
(333, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:41:30'),
(334, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:41:48'),
(335, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:42:45'),
(336, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:43:08'),
(337, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:48:33'),
(338, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:48:48'),
(339, NULL, 'notification_overtime_rejected', 'employee', 26, 'Yêu cầu tăng ca ngày 2026-06-08 bị từ chối. Lý do: Không có', NULL, NULL, 'success', '2026-06-03 09:58:16'),
(340, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:58:36'),
(341, 6, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:58:54'),
(342, 6, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 09:59:28'),
(343, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 09:59:40'),
(344, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:28:34'),
(345, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36', 'success', '2026-06-03 11:36:09'),
(346, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:41:27'),
(347, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36', 'success', '2026-06-03 11:42:26'),
(348, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:43:59'),
(349, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:51:56'),
(350, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:53:12'),
(351, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:53:15'),
(352, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:53:38'),
(353, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:56:09'),
(354, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:56:22'),
(355, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:56:25'),
(356, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:56:41'),
(357, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 11:56:43'),
(358, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 11:58:46'),
(359, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 12:00:00'),
(360, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 12:00:12'),
(361, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 12:00:23'),
(362, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 12:00:49'),
(363, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 12:01:01'),
(364, 14, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 12:01:18'),
(365, 14, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 12:01:42'),
(366, 5, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0', 'success', '2026-06-03 13:37:43'),
(367, 5, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-03 13:37:47'),
(368, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 10:38:58'),
(369, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-16 11:05:30'),
(370, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 11:05:49'),
(371, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-16 11:05:51'),
(372, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 11:06:08'),
(373, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-16 11:06:40'),
(374, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 11:18:30'),
(375, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-16 11:18:45'),
(376, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 11:44:49'),
(377, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Zalo iOS/260502804 ZaloTheme/light ZaloLanguage/vn', 'success', '2026-06-16 14:00:30'),
(378, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36', 'success', '2026-06-16 14:01:25'),
(379, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5 Safari/605.1.15', 'success', '2026-06-16 14:03:01'),
(380, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36', 'success', '2026-06-16 14:05:21'),
(381, 1, 'logout', NULL, NULL, NULL, '127.0.0.1', NULL, 'success', '2026-06-16 14:06:52'),
(382, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36', 'success', '2026-06-16 14:07:16'),
(383, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0', 'success', '2026-06-16 14:08:10'),
(384, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_5_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/424.4.924152415 Mobile/15E148 Safari/604.1', 'success', '2026-06-16 14:15:23'),
(385, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36', 'success', '2026-06-16 14:15:50'),
(386, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/149 Version/11.1.1 Safari/605.1.15', 'success', '2026-06-16 14:18:25'),
(387, 1, 'login', NULL, NULL, NULL, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/149 Version/11.1.1 Safari/605.1.15', 'success', '2026-06-16 14:24:37');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `failed_login_attempts` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `is_active`, `last_login`, `failed_login_attempts`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'admin@attendance.com', 'pbkdf2:sha256:600000$MF7R1o2RB3dRLaPF$14d37e0944eb2e56dcc21803bdc9ca4067a41b5b9178a8b8c0f3b8b7fcff68e0', 'admin', 1, '2026-06-16 07:24:37', 0, '2026-05-06 18:42:17', '2026-06-16 14:24:37'),
(2, 'EMP001', 'nguyenvana@company.com', 'pbkdf2:sha256:600000$HA6dcRIG1l6vvrFg$b7bfb1928501cf38be0d715dd5d2c39a0d4de659699d0fad7b63664c64303a61', 'employee', 1, '2026-05-20 04:07:07', 0, '2026-05-06 21:42:03', '2026-05-20 11:07:07'),
(3, 'EMP002', 'tranthib@company.com', 'pbkdf2:sha256:600000$KhcqQxsyRMp6AR87$1d9fbfe6731ecc80b9762604e6752522a4fe9fdcfe5510a70b3c5423cdb6f156', 'employee', 1, '2026-05-07 03:35:50', 0, '2026-05-06 21:42:04', '2026-05-07 10:35:50'),
(4, 'EMP003', 'levanc@company.com', 'pbkdf2:sha256:600000$f6gN6DjhWvTdVYwr$c3c20194b474bad57db9f431f236629f1a7dc92bfa7e034e39ee75ee22303e9d', 'employee', 1, NULL, 0, '2026-05-06 21:42:04', '2026-05-06 21:42:04'),
(5, 'NV001', '2022202@eaut.edu.vn', 'pbkdf2:sha256:600000$ArMgrJvHYuVjBCmg$01d08eb7acc4885e956db26001de9b875768d56b166f9566e211ae7522ea6ed6', 'employee', 1, '2026-06-03 06:37:43', 0, '2026-05-20 13:47:05', '2026-06-03 13:37:43'),
(6, 'NV002', '202220@eaut.edu.vn', 'pbkdf2:sha256:600000$0CNfh1m6ay8YPhcn$0af1ff577a16aee0e7c7d1654b27bb1745ca3fb051bbe0b3c7e7cf7d3090708d', 'employee', 1, '2026-06-03 02:58:54', 0, '2026-05-20 13:47:53', '2026-06-03 09:58:54'),
(7, 'NV003', '2022201@eaut.edu.vn', 'pbkdf2:sha256:600000$3bhvDOwcRlmrR4uo$a67aaee050ab6673cef227714236e63f882e9396c46ea6ddf821dd7e7d6c8146', 'employee', 1, NULL, 0, '2026-05-20 13:49:16', '2026-05-20 13:49:16'),
(8, 'NV004', '20222012@eaut.edu.vn', 'pbkdf2:sha256:600000$m0qLXwsJ2JkYdH5q$6a2482ee3092dee36750dae823bc67c16557fed2a1264a81b2fade7e347364a5', 'employee', 1, NULL, 0, '2026-05-20 13:49:47', '2026-05-20 13:49:47'),
(9, 'NV005', '2022012@eaut.edu.vn', 'pbkdf2:sha256:600000$PPouqSCpSevWwwhi$f411ec6d389aefa915f3b758fa3ebe89dda06fd190fe73eb0ef5bd39d5a6a768', 'employee', 1, NULL, 0, '2026-05-20 13:50:10', '2026-05-20 13:50:10'),
(10, 'NV006', '202012@eaut.edu.vn', 'pbkdf2:sha256:600000$hWvhoYgAj4U6Rqgw$99ca6dd2c3d0a173c446ae20474d21733e540a89317df0730f53d6d1b22e0808', 'employee', 1, NULL, 0, '2026-05-20 13:50:22', '2026-05-20 13:50:22'),
(11, 'NV007', '20239558@gmail.com', 'pbkdf2:sha256:600000$CSJulNx6KTu1l3Ck$035e694bdc58eeb3be57afc740f5ebaf1bfa9da2477a249c3734667fab966920', 'employee', 1, NULL, 0, '2026-05-20 13:50:57', '2026-05-20 13:50:57'),
(12, 'NV008', '514546@mail.com', 'pbkdf2:sha256:600000$Dp0OiTy8tHOY6gS9$fec63fbab6f015b7af30139944e17eb9528a24029e3141b5a5ff653bf90d7d41', 'employee', 1, NULL, 0, '2026-05-20 13:51:31', '2026-05-20 13:51:31'),
(13, 'NV009', '2022082@eaut.edu.vn', 'pbkdf2:sha256:600000$YIpCUYaYGvA1aEsW$c77affa8397ce84c3e9804c8edc2b8eac35b11f7e70d93fd7ff11baf6ef0c165', 'employee', 1, NULL, 0, '2026-05-20 13:52:01', '2026-05-20 13:52:01'),
(14, 'NV010', '51454776@mail.com', 'pbkdf2:sha256:600000$dNSqQxxBbB5DoxxH$700a2fbb9f43953cb7f1f9171e93645c30f2c413983e2f11b873a14e553d9606', 'employee', 1, '2026-06-03 05:01:18', 0, '2026-05-20 13:56:31', '2026-06-03 12:01:18'),
(15, 'NV011', '20222082@eaut.edu.vn', 'pbkdf2:sha256:600000$usHhejiW2fPQ11cv$5881ba785c200f5fd849fdf5bfb13ee056b75087dbbbb371836b36bfa3915935', 'employee', 1, NULL, 0, '2026-05-24 09:07:19', '2026-06-16 11:45:20'),
(16, 'NV012', '2022208222@eaut.edu.vn', 'pbkdf2:sha256:600000$L1Y3aSkyBhVr82nB$66b9e9c7f38701170d10525754674ae2b6479ddce3d028ef2d2c12400669c8c5', 'employee', 1, NULL, 0, '2026-06-16 11:49:00', '2026-06-16 11:49:00');

-- --------------------------------------------------------

--
-- Table structure for table `user_roles`
--

CREATE TABLE `user_roles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `work_schedules`
--

CREATE TABLE `work_schedules` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `shift_start` time NOT NULL,
  `shift_end` time NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `work_days` varchar(32) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `work_schedules`
--

INSERT INTO `work_schedules` (`id`, `employee_id`, `shift_start`, `shift_end`, `is_active`, `effective_from`, `effective_to`, `work_days`, `notes`, `created_at`, `updated_at`) VALUES
(8, 27, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:53:23', '2026-05-20 13:53:23'),
(9, 28, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:53:37', '2026-05-20 13:53:37'),
(11, 30, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:53:47', '2026-05-20 13:53:47'),
(12, 31, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:53:51', '2026-05-20 13:53:51'),
(13, 32, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:53:56', '2026-05-20 13:53:56'),
(14, 33, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-05-20 13:54:00', '2026-05-20 13:54:00'),
(18, 37, '08:00:00', '17:00:00', 1, NULL, NULL, '0,1,2,3,4,5', NULL, '2026-06-03 11:44:41', '2026-06-03 11:44:41');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_employee_date` (`employee_id`,`date`),
  ADD KEY `ix_attendance_date` (`date`),
  ADD KEY `ix_attendance_employee_id` (`employee_id`);

--
-- Indexes for table `departments`
--
ALTER TABLE `departments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_departments_name` (`name`),
  ADD UNIQUE KEY `ix_departments_code` (`code`),
  ADD KEY `ix_departments_is_active` (`is_active`),
  ADD KEY `parent_id` (`parent_id`),
  ADD KEY `manager_id` (`manager_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_employees_employee_code` (`employee_code`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `ix_employees_department_id` (`department_id`);

--
-- Indexes for table `face_embeddings`
--
ALTER TABLE `face_embeddings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_face_embeddings_employee_id` (`employee_id`),
  ADD KEY `ix_face_embeddings_employee_code` (`employee_code`);

--
-- Indexes for table `leave_requests`
--
ALTER TABLE `leave_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_leave_requests_employee_id` (`employee_id`),
  ADD KEY `ix_leave_requests_reviewer_id` (`reviewer_id`);

--
-- Indexes for table `overtime_requests`
--
ALTER TABLE `overtime_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_overtime_requests_employee_id` (`employee_id`),
  ADD KEY `ix_overtime_requests_reviewer_id` (`reviewer_id`);

--
-- Indexes for table `permissions`
--
ALTER TABLE `permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_permissions_name` (`name`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_roles_name` (`name`);

--
-- Indexes for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_role_permission` (`role_id`,`permission_id`),
  ADD KEY `ix_role_permissions_role_id` (`role_id`),
  ADD KEY `ix_role_permissions_permission_id` (`permission_id`);

--
-- Indexes for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_entity` (`entity_type`,`entity_id`),
  ADD KEY `ix_system_logs_action` (`action`),
  ADD KEY `ix_system_logs_created_at` (`created_at`),
  ADD KEY `ix_system_logs_user_id` (`user_id`),
  ADD KEY `idx_user_action` (`user_id`,`action`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_username` (`username`),
  ADD UNIQUE KEY `ix_users_email` (`email`);

--
-- Indexes for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_user_role` (`user_id`,`role_id`),
  ADD KEY `ix_user_roles_role_id` (`role_id`),
  ADD KEY `ix_user_roles_user_id` (`user_id`);

--
-- Indexes for table `work_schedules`
--
ALTER TABLE `work_schedules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_work_schedules_employee_id` (`employee_id`),
  ADD KEY `idx_work_schedule_employee_active` (`employee_id`,`is_active`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=126;

--
-- AUTO_INCREMENT for table `departments`
--
ALTER TABLE `departments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `face_embeddings`
--
ALTER TABLE `face_embeddings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `leave_requests`
--
ALTER TABLE `leave_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `overtime_requests`
--
ALTER TABLE `overtime_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `permissions`
--
ALTER TABLE `permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `role_permissions`
--
ALTER TABLE `role_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `system_logs`
--
ALTER TABLE `system_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=388;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `user_roles`
--
ALTER TABLE `user_roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `work_schedules`
--
ALTER TABLE `work_schedules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`);

--
-- Constraints for table `departments`
--
ALTER TABLE `departments`
  ADD CONSTRAINT `departments_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `departments` (`id`),
  ADD CONSTRAINT `departments_ibfk_2` FOREIGN KEY (`manager_id`) REFERENCES `employees` (`id`);

--
-- Constraints for table `employees`
--
ALTER TABLE `employees`
  ADD CONSTRAINT `employees_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`);

--
-- Constraints for table `face_embeddings`
--
ALTER TABLE `face_embeddings`
  ADD CONSTRAINT `face_embeddings_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`);

--
-- Constraints for table `leave_requests`
--
ALTER TABLE `leave_requests`
  ADD CONSTRAINT `leave_requests_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`),
  ADD CONSTRAINT `leave_requests_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `overtime_requests`
--
ALTER TABLE `overtime_requests`
  ADD CONSTRAINT `overtime_requests_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`),
  ADD CONSTRAINT `overtime_requests_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  ADD CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`);

--
-- Constraints for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`);

--
-- Constraints for table `work_schedules`
--
ALTER TABLE `work_schedules`
  ADD CONSTRAINT `work_schedules_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

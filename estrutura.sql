CREATE TABLE `clientes`
(
    `id`             int(11) NOT NULL AUTO_INCREMENT,
    `email`          varchar(255)       DEFAULT NULL,
    `fone`           varchar(50)        DEFAULT NULL,
    `celular`        varchar(50)        DEFAULT NULL,
    `nome`           varchar(100)       DEFAULT NULL,
    `cpf_cnpj`       varchar(20)        DEFAULT NULL,
    `ativo`          varchar(1)         DEFAULT 'N',
    `bloqueado`      varchar(1)         DEFAULT 'N',
    `imagem`         varchar(255)       DEFAULT NULL,
    `endereco`       varchar(100)       DEFAULT NULL,
    `numero`         varchar(10)        DEFAULT NULL,
    `complemento`    varchar(100)       DEFAULT NULL,
    `bairro`         varchar(100)       DEFAULT NULL,
    `cep`            varchar(20)        DEFAULT NULL,
    `cidade`         varchar(50)        DEFAULT NULL,
    `uf`             varchar(2)         DEFAULT NULL,
    `password`       varchar(255)       DEFAULT NULL,
    `session_id`     varchar(255)       DEFAULT NULL,
    `remember_token` varchar(100)       DEFAULT NULL,
    `updated_at`     timestamp NULL DEFAULT NULL,
    `created_at`     timestamp NOT NULL DEFAULT current_timestamp(),
    `idsla`          int(11) DEFAULT NULL,
    `idtecnico`      int(11) DEFAULT NULL,
    `deleted_at`     timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY              `clientes_idtecnico_index` (`idtecnico`),
    KEY              `idx_clientes_nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

CREATE TABLE `cliente_emails`
(
    `id`                int(11) NOT NULL AUTO_INCREMENT,
    `idcliente`         bigint(20) DEFAULT NULL,
    `email`             varchar(255)       DEFAULT NULL,
    `nome`              varchar(50)        DEFAULT NULL,
    `admin`             varchar(1)         DEFAULT 'N' COMMENT 'Se o usuário é admin S/N',
    `password`          varchar(255)       DEFAULT NULL,
    `session_id`        varchar(255)       DEFAULT NULL,
    `remember_token`    varchar(100)       DEFAULT NULL,
    `updated_at`        timestamp NULL DEFAULT NULL,
    `created_at`        timestamp NOT NULL DEFAULT current_timestamp(),
    `ramal`             varchar(10)        DEFAULT NULL,
    `telefone`          varchar(20)        DEFAULT NULL,
    `idsla`             int(11) DEFAULT NULL,
    `idbling`           int(11) DEFAULT NULL,
    `email_verified_at` timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY                 `cliente_emails_idbling` (`idbling`),
    KEY                 `idcliente_idx` (`idcliente`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Tempo de geração: 16/01/2026 às 16:02
-- Versão do servidor: 10.6.24-MariaDB
-- Versão do PHP: 8.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `cpsndesk_legal`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `departamentos`
--

CREATE TABLE `departamentos` (
  `id` int(11) NOT NULL,
  `descricao` varchar(100) DEFAULT NULL,
  `icone` varchar(255) DEFAULT NULL,
  `ativo` varchar(1) DEFAULT NULL,
  `idtipo` int(11) DEFAULT 1,
  `portal_cliente` tinyint(1) DEFAULT 1,
  `id_termo_personalizado` int(11) DEFAULT NULL,
  `valor_departamento` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;



-- --------------------------------------------------------

--
-- Estrutura para tabela `produtos`
--

CREATE TABLE `produtos` (
  `id` int(11) NOT NULL,
  `descricao` varchar(100) NOT NULL,
  `icone` varchar(255) NOT NULL,
  `ativo` varchar(1) NOT NULL DEFAULT 'S',
  `idsla` int(11) DEFAULT NULL,
  `portal_cliente` tinyint(1) DEFAULT 1,
  `id_termo_personalizado` int(11) DEFAULT NULL,
  `valor_categoria` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Despejando dados para a tabela `produtos`
--


-- --------------------------------------------------------

--
-- Estrutura para tabela `produto_departamentos`
--

CREATE TABLE `produto_departamentos` (
  `id` int(11) NOT NULL,
  `idproduto` int(11) DEFAULT NULL,
  `iddepartamento` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


--
-- Estrutura para tabela `tipos`
--

CREATE TABLE `tipos` (
  `id` int(11) NOT NULL,
  `descricao` varchar(100) NOT NULL,
  `ativo` varchar(1) NOT NULL DEFAULT 'S',
  `icone` varchar(255) NOT NULL,
  `idproduto` int(11) DEFAULT 1,
  `portal_cliente` tinyint(1) DEFAULT 1,
  `id_termo_personalizado` int(11) DEFAULT NULL,
  `valor_tipo` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


-- --------------------------------------------------------

--
-- Estrutura para tabela `tipo_departamentos`
--

-- CREATE TABLE `tipo_departamentos` (
--   `id` int(11) NOT NULL,
--   `idtipo` int(11) DEFAULT NULL,
--   `iddepartamento` int(11) DEFAULT NULL
-- ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
--

-- Índices para tabelas despejadas
--

--
-- Índices de tabela `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `produtos`
--
ALTER TABLE `produtos`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `produto_departamentos`
--
ALTER TABLE `produto_departamentos`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `tipos`
--
ALTER TABLE `tipos`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `tipo_departamentos`
--
-- ALTER TABLE `tipo_departamentos`
--   ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `produtos`
--
ALTER TABLE `produtos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `produto_departamentos`
--
ALTER TABLE `produto_departamentos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `tipos`
--
ALTER TABLE `tipos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de tabela `tipo_departamentos`
--
-- ALTER TABLE `tipo_departamentos`
--   MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

CREATE TABLE `tipo_produtos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idtipo` int(11) DEFAULT NULL,
  `idproduto` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=Inno;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

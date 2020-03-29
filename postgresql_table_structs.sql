/*
 Source Server         : 127.0.0.1
 Source Server Type    : PostgreSQL
 Source Server Version : 120002
 Source Host           : 127.0.0.1:5432
 Source Catalog        : secblocks
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 120002
 File Encoding         : 65001

 Date: 29/03/2020 15:53:02
*/


-- ----------------------------
-- Sequence structure for domains_list_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."domains_list_id_seq";
CREATE SEQUENCE "public"."domains_list_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."domains_list_id_seq" OWNER TO "testpsql1";

-- ----------------------------
-- Sequence structure for ips_list_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."ips_list_id_seq";
CREATE SEQUENCE "public"."ips_list_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."ips_list_id_seq" OWNER TO "testpsql1";

-- ----------------------------
-- Sequence structure for ports_detail_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."ports_detail_id_seq";
CREATE SEQUENCE "public"."ports_detail_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."ports_detail_id_seq" OWNER TO "testpsql1";

-- ----------------------------
-- Sequence structure for ports_list_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."ports_list_id_seq";
CREATE SEQUENCE "public"."ports_list_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."ports_list_id_seq" OWNER TO "testpsql1";

-- ----------------------------
-- Sequence structure for websites_detail_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."websites_detail_id_seq";
CREATE SEQUENCE "public"."websites_detail_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."websites_detail_id_seq" OWNER TO "testpsql1";

-- ----------------------------
-- Table structure for domains_list
-- ----------------------------
DROP TABLE IF EXISTS "public"."domains_list";
CREATE TABLE "public"."domains_list" (
  "id" int4 NOT NULL DEFAULT nextval('domains_list_id_seq'::regclass),
  "ips" varchar(2550) COLLATE "pg_catalog"."default",
  "org_name" varchar(2550) COLLATE "pg_catalog"."default",
  "target" int4 DEFAULT 0,
  "scan_times" int4 DEFAULT 0,
  "time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "synced" int4 DEFAULT 0,
  "domain" varchar(2550) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "public"."domains_list" OWNER TO "testpsql1";

-- ----------------------------
-- Table structure for ips_list
-- ----------------------------
DROP TABLE IF EXISTS "public"."ips_list";
CREATE TABLE "public"."ips_list" (
  "id" int4 NOT NULL DEFAULT nextval('ips_list_id_seq'::regclass),
  "ip" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "org_name" varchar(255) COLLATE "pg_catalog"."default",
  "target" int4 DEFAULT 0,
  "list_times" int4 DEFAULT 0,
  "detail_times" int4 DEFAULT 0,
  "time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "synced" int4 DEFAULT 0
)
;
ALTER TABLE "public"."ips_list" OWNER TO "testpsql1";

-- ----------------------------
-- Table structure for ports_detail
-- ----------------------------
DROP TABLE IF EXISTS "public"."ports_detail";
CREATE TABLE "public"."ports_detail" (
  "id" int4 NOT NULL DEFAULT nextval('ports_detail_id_seq'::regclass),
  "detail" text COLLATE "pg_catalog"."default",
  "time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "ip" text COLLATE "pg_catalog"."default",
  "synced" int4 DEFAULT 0
)
;
ALTER TABLE "public"."ports_detail" OWNER TO "testpsql1";

-- ----------------------------
-- Table structure for ports_list
-- ----------------------------
DROP TABLE IF EXISTS "public"."ports_list";
CREATE TABLE "public"."ports_list" (
  "id" int4 NOT NULL DEFAULT nextval('ports_list_id_seq'::regclass),
  "time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "list" text COLLATE "pg_catalog"."default",
  "ip" text COLLATE "pg_catalog"."default",
  "synced" int4 DEFAULT 0
)
;
ALTER TABLE "public"."ports_list" OWNER TO "testpsql1";

-- ----------------------------
-- Table structure for websites_detail
-- ----------------------------
DROP TABLE IF EXISTS "public"."websites_detail";
CREATE TABLE "public"."websites_detail" (
  "id" int4 NOT NULL DEFAULT nextval('websites_detail_id_seq'::regclass),
  "detail" text COLLATE "pg_catalog"."default",
  "time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "domain" text COLLATE "pg_catalog"."default",
  "synced" int4 DEFAULT 0
)
;
ALTER TABLE "public"."websites_detail" OWNER TO "testpsql1";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."domains_list_id_seq"
OWNED BY "public"."domains_list"."id";
SELECT setval('"public"."domains_list_id_seq"', 120774, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."ips_list_id_seq"
OWNED BY "public"."ips_list"."id";
SELECT setval('"public"."ips_list_id_seq"', 45111, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."ports_detail_id_seq"
OWNED BY "public"."ports_detail"."id";
SELECT setval('"public"."ports_detail_id_seq"', 2500, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."ports_list_id_seq"
OWNED BY "public"."ports_list"."id";
SELECT setval('"public"."ports_list_id_seq"', 2619, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."websites_detail_id_seq"
OWNED BY "public"."websites_detail"."id";
SELECT setval('"public"."websites_detail_id_seq"', 5, true);

-- ----------------------------
-- Primary Key structure for table domains_list
-- ----------------------------
ALTER TABLE "public"."domains_list" ADD CONSTRAINT "ips_list_copy1_pkey1" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table ips_list
-- ----------------------------
ALTER TABLE "public"."ips_list" ADD CONSTRAINT "ips_list_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table ports_detail
-- ----------------------------
ALTER TABLE "public"."ports_detail" ADD CONSTRAINT "ips_list_copy1_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table ports_list
-- ----------------------------
ALTER TABLE "public"."ports_list" ADD CONSTRAINT "ports_list_copy1_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table websites_detail
-- ----------------------------
ALTER TABLE "public"."websites_detail" ADD CONSTRAINT "ports_detail_copy1_pkey" PRIMARY KEY ("id");

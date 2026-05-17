/*
 Navicat Premium Data Transfer

 Source Server         : 本机
 Source Server Type    : PostgreSQL
 Source Server Version : 170004 (170004)
 Source Host           : localhost:5432
 Source Catalog        : 泉州市
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170004 (170004)
 File Encoding         : 65001

 Date: 09/03/2025 19:33:43
*/


-- ----------------------------
-- Table structure for 希望小学
-- ----------------------------
DROP TABLE IF EXISTS "public"."希望小学";
CREATE TABLE "public"."希望小学" (
  "姓名" varchar(255) COLLATE "pg_catalog"."default",
  "年龄" int4,
  "年级" varchar(255) COLLATE "pg_catalog"."default",
  "签到日期" varchar(255) COLLATE "pg_catalog"."default",
  "喜欢的科目" varchar(255) COLLATE "pg_catalog"."default",
  "爱好" varchar(255) COLLATE "pg_catalog"."default",
  "视力" float4,
  "性别" varchar(255) COLLATE "pg_catalog"."default",
  "备注" varchar(255) COLLATE "pg_catalog"."default",
  "id" int4 NOT NULL DEFAULT nextval('"希望小学_id_seq"'::regclass)
)
;

-- ----------------------------
-- Primary Key structure for table 希望小学
-- ----------------------------
ALTER TABLE "public"."希望小学" ADD CONSTRAINT "希望小学_pkey" PRIMARY KEY ("id");

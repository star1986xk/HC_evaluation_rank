-- ----------------------------
-- Table structure for evaluation_rank
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[evaluation_rank]') AND type IN ('U'))
	DROP TABLE [dbo].[evaluation_rank]
GO

CREATE TABLE [dbo].[evaluation_rank] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [score_type] nvarchar(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [ranking] int  NULL,
  [company] nvarchar(100) COLLATE Chinese_PRC_CI_AS  NULL,
  [organization_code] nvarchar(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [credit_code] nvarchar(50) COLLATE Chinese_PRC_CI_AS  NULL,
  [normal_score] float(53)  NULL,
  [promise_score] float(53)  NULL,
  [quality_score] float(53)  NULL,
  [total_score] float(53)  NULL,
  [calculate_date] date  NULL
)
GO

ALTER TABLE [dbo].[evaluation_rank] SET (LOCK_ESCALATION = TABLE)
GO

EXEC sp_addextendedproperty
'MS_Description', N'评分类型',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'score_type'
GO

EXEC sp_addextendedproperty
'MS_Description', N'排名',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'ranking'
GO

EXEC sp_addextendedproperty
'MS_Description', N'企业名称',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'company'
GO

EXEC sp_addextendedproperty
'MS_Description', N'机构代码',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'organization_code'
GO

EXEC sp_addextendedproperty
'MS_Description', N'信用代码',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'credit_code'
GO

EXEC sp_addextendedproperty
'MS_Description', N'通常行为分',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'normal_score'
GO

EXEC sp_addextendedproperty
'MS_Description', N'合同履约分',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'promise_score'
GO

EXEC sp_addextendedproperty
'MS_Description', N'质量安全文明分',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'quality_score'
GO

EXEC sp_addextendedproperty
'MS_Description', N'总分',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'total_score'
GO

EXEC sp_addextendedproperty
'MS_Description', N'计算日期',
'SCHEMA', N'dbo',
'TABLE', N'evaluation_rank',
'COLUMN', N'calculate_date'
GO


-- ----------------------------
-- Auto increment value for evaluation_rank
-- ----------------------------
DBCC CHECKIDENT ('[dbo].[evaluation_rank]', RESEED, 2019)
GO


-- ----------------------------
-- Indexes structure for table evaluation_rank
-- ----------------------------
CREATE UNIQUE NONCLUSTERED INDEX [index]
ON [dbo].[evaluation_rank] (
  [organization_code] ASC,
  [calculate_date] ASC,
  [score_type] ASC
)
GO


-- ----------------------------
-- Primary Key structure for table evaluation_rank
-- ----------------------------
ALTER TABLE [dbo].[evaluation_rank] ADD CONSTRAINT [PK__evaluati__3213E83F73BA3083] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
GO

